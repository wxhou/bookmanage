from marshmallow import fields
from .extensions import apispec_plugin


@apispec_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass