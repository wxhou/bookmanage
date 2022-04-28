#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from common.extensions import db


class Press(db.Model):
    """出版社信息"""
    # __tablename__ = 'book_press'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 名称
    addr = db.Column(db.String(128))  # 地址
    books = db.relationship('Book', backref='press', lazy=True)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


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


class Book(db.Model):
    """图书信息"""
    # __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 图书名称
    ISBN = db.Column(db.String(64))  # 图书编号
    translator = db.Column(db.String(64))  # 译者
    desc = db.Column(db.Text)  # 简介
    stock = db.Column(db.Integer)  # 库存
    press_id = db.Column(db.Integer, db.ForeignKey('press.id'))  # 出版社ID
    authors = db.relationship('Author',
                              secondary=author_books,
                              back_populates='books')
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


class BookMedia(db.Model):
    """图书资源"""
    # __tablename__ = 'book_media'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    url = db.Column(db.String(128))
    mtype = db.Column(db.Integer)  # 资源类型(image 1/audio 2/video 3)
    ctype = db.Column(db.Integer)  # 图片类型(cover 1/content 2)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


class Author(db.Model):
    """作者信息"""
    # __tablename__ = 'book_author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))  # 姓名
    sex = db.Column(db.String(4))  # 性别
    books = db.relationship('Book',
                            secondary=author_books,
                            back_populates='authors')
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)


class BorrowRead(db.Model):
    """借阅信息"""
    # __tablename__ = 'book_borrowread'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 正常 -1 删除
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modify_time = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)
