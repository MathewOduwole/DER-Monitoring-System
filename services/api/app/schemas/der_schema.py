from marshmallow import Schema, fields, validate


class CreateDERSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    mrid_id = fields.String(required=True, validate=validate.Length(min=1, max=255))
    location = fields.String(validate=validate.Length(max=255), load_default=None)
    type = fields.String(required=True, validate=validate.Length(min=1, max=100))


class UpdateDERSchema(Schema):
    mrid_id = fields.String(validate=validate.Length(min=1, max=255))
    location = fields.String(validate=validate.Length(max=255), allow_none=True)
    type = fields.String(validate=validate.Length(min=1, max=100))
