from typing import Tuple
from datetime import date
from app.config import settings

MONTH_NAMES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def month_name(month_int: int) -> str:
    return MONTH_NAMES.get(month_int, "Invalid")


def compute_kpi_status(target: float, actual: float) -> Tuple[float, float, str]:
    diff = actual - target

    if target > 0:
        pct = (actual / target) * 100
    else:
        pct = 0.0 if actual == 0 else 100.0

    if pct >= settings.THRESHOLD_GREEN:
        status = "green"
    elif pct >= settings.THRESHOLD_YELLOW:
        status = "yellow"
    else:
        status = "red"

    return diff, pct, status


def get_status_color(status: str) -> str:
    color_map = {
        "green": "#28a745",
        "yellow": "#ffc107",
        "red": "#dc3545"
    }
    return color_map.get(status, "#6c757d")


def format_number(value: float, decimals: int = 0) -> str:
    if decimals == 0:
        return f"{value:,.0f}".replace(",", " ")
    else:
        return f"{value:,.{decimals}f}".replace(",", " ")


def validate_month(month: int) -> bool:
    return 1 <= month <= 12


def validate_year(year: int) -> bool:
    return 2020 <= year <= 2100


def get_current_year() -> int:
    return date.today().year


def get_current_month() -> int:
    return date.today().month
