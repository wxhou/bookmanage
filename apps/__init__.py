#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint
from apps.views_auth import bp_auth

bp_client = Blueprint('client', __name__)


bp_client.register_blueprint(bp_auth, url_prefix='/auth')
