"""
Utility functions for the Agency Performance Tracker.
"""
from typing import Tuple, Optional
from datetime import date

# Status thresholds (configurable)
THRESHOLD_GREEN = 100  # >= 100% is green
THRESHOLD_YELLOW = 90  # >= 90% is yellow, < 90% is red

# Month names in Spanish
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
    """
    Convert month number (1-12) to Spanish month name.

    Args:
        month_int: Month number (1-12)

    Returns:
        Spanish month name or "Inválido" if out of range
    """
    return MONTH_NAMES.get(month_int, "Inválido")


def compute_kpi_status(target: float, actual: float) -> Tuple[float, float, str]:
    """
    Compute KPI status based on target and actual values.

    Args:
        target: Target value for the KPI
        actual: Actual achieved value

    Returns:
        Tuple of (difference, percentage, status)
        - difference: actual - target
        - percentage: (actual / target) * 100 if target > 0, else 0
        - status: "green", "yellow", or "red"
    """
    diff = actual - target

    if target > 0:
        pct = (actual / target) * 100
    else:
        pct = 0.0 if actual == 0 else 100.0  # If no target, consider 100% if actual > 0

    # Determine status based on percentage
    if pct >= THRESHOLD_GREEN:
        status = "green"
    elif pct >= THRESHOLD_YELLOW:
        status = "yellow"
    else:
        status = "red"

    return diff, pct, status


def get_status_emoji(status: str) -> str:
    """
    Get emoji for status indicator.

    Args:
        status: "green", "yellow", or "red"

    Returns:
        Corresponding emoji
    """
    emoji_map = {
        "green": "🟢",
        "yellow": "🟡",
        "red": "🔴"
    }
    return emoji_map.get(status, "⚪")


def get_status_color(status: str) -> str:
    """
    Get hex color for status indicator.

    Args:
        status: "green", "yellow", or "red"

    Returns:
        Corresponding hex color
    """
    color_map = {
        "green": "#28a745",
        "yellow": "#ffc107",
        "red": "#dc3545"
    }
    return color_map.get(status, "#6c757d")


def format_number(value: float, decimals: int = 0) -> str:
    """
    Format a number with thousand separators.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string with thousand separators
    """
    if decimals == 0:
        return f"{value:,.0f}".replace(",", " ")
    else:
        return f"{value:,.{decimals}f}".replace(",", " ")


def validate_month(month: int) -> bool:
    """
    Validate that month is in valid range (1-12).

    Args:
        month: Month number to validate

    Returns:
        True if valid, False otherwise
    """
    return 1 <= month <= 12


def validate_year(year: int) -> bool:
    """
    Validate that year is reasonable.

    Args:
        year: Year to validate

    Returns:
        True if valid, False otherwise
    """
    return 2020 <= year <= 2100


def get_current_year() -> int:
    """Get current year."""
    return date.today().year


def get_current_month() -> int:
    """Get current month (1-12)."""
    return date.today().month
