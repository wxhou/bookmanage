from marshmallow import fields, validate, validates, Schema, ValidationError
from app.extensions import apispec_plugin


@apispec_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass


class PageSchema(Schema):
    page = fields.String(default=1)

    @validates('page')
    def validate_page(self, value):
        try:
            if not (0 < int(value) < 99999999):
                raise ValidationError("value must be a number")
        except:
            raise ValidationError("value must be a number")
