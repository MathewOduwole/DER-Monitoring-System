from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.schemas.der_schema import CreateDERSchema, UpdateDERSchema
from app.services.der_service import DERService
from app.services.telemetry_service import TelemetryService

der_bp = Blueprint("ders", __name__, url_prefix="/api/ders")

create_schema = CreateDERSchema()
update_schema = UpdateDERSchema()


@der_bp.route("", methods=["GET"])
def list_ders():
    ders = DERService.get_all()
    return jsonify([d.to_dict() for d in ders]), 200


@der_bp.route("", methods=["POST"])
def register_der():
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    existing = DERService.get_by_name(data["name"])
    if existing:
        return jsonify({"error": f"DER '{data['name']}' already exists."}), 409

    der = DERService.create(data)
    return jsonify(der.to_dict()), 201


@der_bp.route("/<string:der_name>", methods=["PUT"])
def update_der(der_name: str):
    der = DERService.get_by_name(der_name)
    if der is None:
        return jsonify({"error": f"DER '{der_name}' not found."}), 404

    try:
        data = update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    updated = DERService.update(der, data)
    return jsonify(updated.to_dict()), 200


@der_bp.route("/<string:der_name>", methods=["DELETE"])
def delete_der(der_name: str):
    der = DERService.get_by_name(der_name)
    if der is None:
        return jsonify({"error": f"DER '{der_name}' not found."}), 404

    DERService.delete(der)
    return jsonify({"message": f"DER '{der_name}' deleted."}), 200


@der_bp.route("/<string:der_name>/data", methods=["GET"])
def get_der_data(der_name: str):
    from datetime import datetime

    start_str = request.args.get("start")
    end_str = request.args.get("end")

    start = datetime.fromisoformat(start_str) if start_str else None
    end = datetime.fromisoformat(end_str) if end_str else None

    data = TelemetryService.get_time_series(der_name, start=start, end=end)
    if data is None:
        return jsonify({"error": f"DER '{der_name}' not found."}), 404

    return jsonify(data), 200
