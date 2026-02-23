import logging
from datetime import timedelta

from app.extensions import db
from app.models.chart import Chart, MAX_DERS_PER_CHART, MAX_DATE_RANGE_DAYS
from app.models.der import DER
from app.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class ChartService:
    """Business logic for chart configuration and data retrieval.

    I validate DER existence and date-range constraints at the service layer
    (in addition to the DB CHECK constraints) so I can return clear error messages
    to the client rather than raw database errors.
    """

    @staticmethod
    def create(data: dict) -> tuple[Chart | None, str | None]:
        error = ChartService._validate_chart_data(data)
        if error:
            return None, error

        chart = Chart(
            name=data["name"],
            der_names=data["der_names"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        db.session.add(chart)
        db.session.commit()
        logger.info("Chart created: %s (id=%d)", chart.name, chart.id)
        return chart, None

    @staticmethod
    def get_by_id(chart_id: int) -> Chart | None:
        return db.session.get(Chart, chart_id)

    @staticmethod
    def get_all() -> list[Chart]:
        return Chart.query.order_by(Chart.created_at.desc()).all()

    @staticmethod
    def get_chart_data(chart: Chart) -> dict:
        result = chart.to_dict()
        series = {}

        for der_name in chart.der_names:
            der = DER.query.filter_by(name=der_name).first()
            if der is None:
                series[der_name] = []
                continue

            records = (
                TelemetryData.query
                .filter(
                    TelemetryData.der_id == der.id,
                    TelemetryData.timestamp >= chart.start_date,
                    TelemetryData.timestamp <= chart.end_date,
                )
                .order_by(TelemetryData.timestamp.asc())
                .all()
            )
            series[der_name] = [r.to_dict() for r in records]

        result["series"] = series
        return result

    @staticmethod
    def update(chart: Chart, data: dict) -> tuple[Chart | None, str | None]:
        merged = {
            "der_names": data.get("der_names", chart.der_names),
            "start_date": data.get("start_date", chart.start_date),
            "end_date": data.get("end_date", chart.end_date),
        }
        error = ChartService._validate_chart_data(merged)
        if error:
            return None, error

        for key, value in data.items():
            if hasattr(chart, key):
                setattr(chart, key, value)

        db.session.commit()
        logger.info("Chart updated: %s (id=%d)", chart.name, chart.id)
        return chart, None

    @staticmethod
    def delete(chart: Chart) -> None:
        chart_id = chart.id
        db.session.delete(chart)
        db.session.commit()
        logger.info("Chart deleted: id=%d", chart_id)

    @staticmethod
    def _validate_chart_data(data: dict) -> str | None:
        der_names = data.get("der_names", [])
        if len(der_names) > MAX_DERS_PER_CHART:
            return f"A chart supports at most {MAX_DERS_PER_CHART} DERs."

        start = data.get("start_date")
        end = data.get("end_date")
        if start and end:
            if end <= start:
                return "end_date must be after start_date."
            if (end - start) > timedelta(days=MAX_DATE_RANGE_DAYS):
                return f"Date range must not exceed {MAX_DATE_RANGE_DAYS} days."

        missing = [n for n in der_names if DER.query.filter_by(name=n).first() is None]
        if missing:
            return f"DERs not found: {', '.join(missing)}"

        return None
