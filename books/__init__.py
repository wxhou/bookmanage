#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint
from .views_auth import bp_auth
from .views_books import bp_book
from .views_demo import bp_demo


bp_client = Blueprint('client', __name__)
bp_client.register_blueprint(bp_auth, url_prefix='/auth')
bp_client.register_blueprint(bp_book, url_prefix='/book')
bp_client.register_blueprint(bp_demo, url_prefix='/demo')
