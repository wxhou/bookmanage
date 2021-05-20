#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from flask import g, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import BadTimeSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from core.extensions import db

roles_permissions = db.Table(
    'roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))


class Permission(db.Model):
    """权限"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, index=True)
    roles = db.relationship('Role',
                            secondary=roles_permissions,
                            back_populates='permissions')


class Role(db.Model):
    """角色"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, index=True)
    permissions = db.relationship('Permission',
                                  secondary=roles_permissions,
                                  back_populates='roles')

    @staticmethod
    def init_role():
        roles_permissions_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD'],
            'Moderator':
            ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE'],
            'Administrator':
            ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE', 'ADMIN']
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


class ModelMixin(object):
    """混入模型"""
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


class User(ModelMixin, db.Model):
    """用户信息"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True)
    avatar = db.Column(db.String(256))
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(256))

    @property
    def password(self):
        raise AttributeError("password is only readable")

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        token = s.dumps({'id': self.id}).decode()
        return token, expires_in

    @staticmethod
    def validate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadTimeSignature, SignatureExpired):
            return False
        user = User.query.filter_by(id=data.get('id'), status=0).one_or_none()
        if user is not None and user.token == token:
            g.current_user = user
            return True
        return False


class Press(ModelMixin, db.Model):
    """出版社信息"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 名称
    addr = db.Column(db.String(128))  # 地址
    books = db.relationship('Book', backref='press', lazy=True)


author_books = db.Table(
    'books',
    db.Column('author_id',
              db.Integer,
              db.ForeignKey('author.id'),
              primary_key=True),
    db.Column('book_id',
              db.Integer,
              db.ForeignKey('book.id'),
              primary_key=True))


class Book(ModelMixin, db.Model):
    """图书信息"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 图书名称
    ISBN = db.Column(db.String(64))  # 图书编号
    author = db.Column(db.String(128))  # 作者
    translator = db.Column(db.String(64))  # 译者
    desc = db.Column(db.Text)  # 简介
    press_id = db.Column(db.Integer, db.ForeignKey('press.id'))  # 出版社ID
    authors = db.relationship('Author',
                              secondary=author_books,
                              back_populates='books')


class BookMedia(ModelMixin, db.Model):
    """图书资源"""
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    url = db.Column(db.String(128))
    mtype = db.Column(db.Integer)  # 资源类型(image 1/audio 2/video 3)
    ctype = db.Column(db.Integer)  # 图片类型(cover 1/content 2)


class Author(ModelMixin, db.Model):
    """作者信息"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 姓名
    sex = db.Column(db.String(4))  # 性别
    books = db.relationship('Book',
                            secondary=author_books,
                            back_populates='authors')


class BorrowRead(ModelMixin, db.Model):
    """借阅信息"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
