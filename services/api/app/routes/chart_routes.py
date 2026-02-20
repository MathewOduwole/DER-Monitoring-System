from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.schemas.chart_schema import CreateChartSchema, UpdateChartSchema
from app.services.chart_service import ChartService

chart_bp = Blueprint("charts", __name__, url_prefix="/api/charts")

create_schema = CreateChartSchema()
update_schema = UpdateChartSchema()


@chart_bp.route("", methods=["GET"])
def list_charts():
    charts = ChartService.get_all()
    return jsonify([c.to_dict() for c in charts]), 200


@chart_bp.route("", methods=["POST"])
def create_chart():
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    chart, error = ChartService.create(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(chart.to_dict()), 201


@chart_bp.route("/<int:chart_id>", methods=["GET"])
def get_chart(chart_id: int):
    chart = ChartService.get_by_id(chart_id)
    if chart is None:
        return jsonify({"error": "Chart not found."}), 404

    chart_data = ChartService.get_chart_data(chart)
    return jsonify(chart_data), 200


@chart_bp.route("/<int:chart_id>", methods=["PUT"])
def update_chart(chart_id: int):
    chart = ChartService.get_by_id(chart_id)
    if chart is None:
        return jsonify({"error": "Chart not found."}), 404

    try:
        data = update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    updated, error = ChartService.update(chart, data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(updated.to_dict()), 200


@chart_bp.route("/<int:chart_id>", methods=["DELETE"])
def delete_chart(chart_id: int):
    chart = ChartService.get_by_id(chart_id)
    if chart is None:
        return jsonify({"error": "Chart not found."}), 404

    ChartService.delete(chart)
    return jsonify({"message": "Chart deleted."}), 200
