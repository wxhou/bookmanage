#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from flask import g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from common.extensions import db

roles_permissions = db.Table(
    'roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))


class Permission(db.Model):
    # __tablename__ = 'book_permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role',
                            secondary=roles_permissions,
                            back_populates='permissions')


class Role(db.Model):
    """角色"""
    # __tablename__ = 'book_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, index=True)
    users = db.relationship(
        'User',
        backref='role',
    )
    permissions = db.relationship('Permission',
                                  secondary=roles_permissions,
                                  back_populates='roles')


class ModelMixin(object):
    """混入模型"""
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


class User(ModelMixin, db.Model):
    """用户信息"""
    # __tablename__ = 'book_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(11))
    avatar_id = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return '<User {}>'.format(self.email)

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
        except (BadSignature, SignatureExpired):
            return False
        user = User.query.filter_by(id=data.get('id'), status=0).one_or_none()
        if user is not None and user.token == token:
            g.current_user = user
            current_app.logger.info(g.current_user)
            return True
        return False

    @property
    def is_admin(self):
        return self.role.name == 'Admin'

    @property
    def is_active(self):
        return self.active

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        res = (permission is not None, self.role is not None, permission
               in self.role.permissions)
        return all(res)


class Avatar(ModelMixin, db.Model):
    """用户资源"""
    # __tablename__ = 'book_avatar'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), index=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer)
    url = db.Column(db.String(256))
    mtype = db.Column(db.Integer)  # 资源类型(image 1/audio 2/video 3)
    ctype = db.Column(db.Integer)  # 图片类型(cover 1/content 2)