from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import timedelta

from app.models.chart import MAX_DERS_PER_CHART, MAX_DATE_RANGE_DAYS


class CreateChartSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    der_names = fields.List(
        fields.String(validate=validate.Length(min=1)),
        required=True,
        validate=validate.Length(min=1, max=MAX_DERS_PER_CHART),
    )
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

    @validates("der_names")
    def validate_unique_ders(self, value):
        if len(value) != len(set(value)):
            raise ValidationError("DER names must be unique.")

    def validate(self, data, **kwargs):
        errors = {}
        if "start_date" in data and "end_date" in data:
            if data["end_date"] <= data["start_date"]:
                errors["end_date"] = ["end_date must be after start_date."]
            elif data["end_date"] - data["start_date"] > timedelta(days=MAX_DATE_RANGE_DAYS):
                errors["end_date"] = [
                    f"Date range must not exceed {MAX_DATE_RANGE_DAYS} days."
                ]
        if errors:
            raise ValidationError(errors)
        return data


class UpdateChartSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=255))
    der_names = fields.List(
        fields.String(validate=validate.Length(min=1)),
        validate=validate.Length(min=1, max=MAX_DERS_PER_CHART),
    )
    start_date = fields.DateTime()
    end_date = fields.DateTime()

    @validates("der_names")
    def validate_unique_ders(self, value):
        if len(value) != len(set(value)):
            raise ValidationError("DER names must be unique.")
