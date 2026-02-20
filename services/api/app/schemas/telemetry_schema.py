from marshmallow import Schema, fields, validate


class TelemetryEventSchema(Schema):
    der_name = fields.String(required=True, validate=validate.Length(min=1))
    active_power = fields.Float(required=True)
    reactive_power = fields.Float(required=True)
    voltage = fields.Float(required=True)
    timestamp = fields.DateTime(required=True)
