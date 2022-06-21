from flask import current_app
from marshmallow import Schema, fields, validate


class BaseSchema(Schema):
    id = fields.Integer(dump_only=True)
    create_time = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M:%S")
    modify_time = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M:%S")


class PageSchema(Schema):
    page = fields.Integer(missing=1, load_only=True)
    page_size = fields.Integer(missing=15, load_only=True)
