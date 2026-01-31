"""
Dashboard Service - Business logic for dashboard views.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from db.database import SessionLocal
from db.models import Agency, MonthlyReview, MonthlyResult, User
from services.tracking_service import get_monthly_summary, get_monthly_review, get_action_items
from services.agency_service import list_agencies, get_agency_detail
from services.access_service import get_user_agencies
from services.utils import month_name


def get_agency_dashboard_data(
    agency_id: int,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Get complete dashboard data for a single agency.

    Args:
        agency_id: Agency ID
        year: Year
        month: Month (1-12)

    Returns:
        Dict with all dashboard data
    """
    # Get agency details
    agency = get_agency_detail(agency_id)
    if not agency:
        return None

    # Get KPI summary
    kpi_summary = get_monthly_summary(agency_id, year, month)

    # Calculate overall status
    green_count = sum(1 for k in kpi_summary if k["status"] == "green")
    yellow_count = sum(1 for k in kpi_summary if k["status"] == "yellow")
    red_count = sum(1 for k in kpi_summary if k["status"] == "red")

    # Determine overall status
    if red_count > 0:
        overall_status = "red"
    elif yellow_count > 0:
        overall_status = "yellow"
    elif green_count > 0:
        overall_status = "green"
    else:
        overall_status = "none"

    # Get review
    review = get_monthly_review(agency_id, year, month)

    # Get actions
    actions = get_action_items(agency_id, year, month)
    pending_actions = [a for a in actions if not a["done"]]
    completed_actions = [a for a in actions if a["done"]]

    # Check if review is complete
    has_results = any(k["actual"] > 0 for k in kpi_summary)
    has_review = review is not None and (
        review.get("what_happened") or review.get("improvement_plan")
    )

    return {
        "agency": agency,
        "year": year,
        "month": month,
        "month_name": month_name(month),
        "kpis": kpi_summary,
        "overall_status": overall_status,
        "green_count": green_count,
        "yellow_count": yellow_count,
        "red_count": red_count,
        "review": review,
        "actions": actions,
        "pending_actions": pending_actions,
        "completed_actions": completed_actions,
        "has_results": has_results,
        "has_review": has_review,
        "review_pending": has_results and not has_review
    }


def get_admin_dashboard_data(year: int, month: int) -> Dict[str, Any]:
    """
    Get dashboard data for admin view (all agencies).

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Dict with admin dashboard data
    """
    agencies = list_agencies(active_only=True)

    # Collect data for all agencies
    agencies_data = []
    total_green = 0
    total_yellow = 0
    total_red = 0
    pending_reviews = []

    for agency in agencies:
        agency_data = get_agency_dashboard_data(agency["id"], year, month)
        if agency_data:
            agencies_data.append(agency_data)

            total_green += agency_data["green_count"]
            total_yellow += agency_data["yellow_count"]
            total_red += agency_data["red_count"]

            if agency_data["review_pending"]:
                pending_reviews.append({
                    "agency_name": agency["name"],
                    "manager_name": agency["manager"]["name"] if agency["manager"] else "Sin jefe"
                })

    # Sort by status (worst first)
    agencies_data.sort(
        key=lambda x: (
            -x["red_count"],
            -x["yellow_count"],
            x["green_count"]
        )
    )

    # Agencies at risk (any red KPI)
    at_risk = [a for a in agencies_data if a["red_count"] > 0]

    return {
        "year": year,
        "month": month,
        "month_name": month_name(month),
        "total_agencies": len(agencies_data),
        "total_green": total_green,
        "total_yellow": total_yellow,
        "total_red": total_red,
        "agencies": agencies_data,
        "at_risk": at_risk,
        "pending_reviews": pending_reviews
    }


def get_kpi_card_data(kpi_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format KPI data for card display.

    Args:
        kpi_data: Raw KPI data from get_monthly_summary

    Returns:
        Formatted data for UI card
    """
    status = kpi_data["status"]

    # Status emoji and color
    status_config = {
        "green": {"emoji": "🟢", "color": "#28a745", "label": "Alcanzado"},
        "yellow": {"emoji": "🟡", "color": "#ffc107", "label": "En riesgo"},
        "red": {"emoji": "🔴", "color": "#dc3545", "label": "No alcanzado"}
    }

    config = status_config.get(status, {"emoji": "⚪", "color": "#6c757d", "label": "Sin datos"})

    return {
        "code": kpi_data["kpi_code"],
        "label": kpi_data["kpi_label"],
        "unit": kpi_data["kpi_unit"],
        "target": kpi_data["target"],
        "actual": kpi_data["actual"],
        "diff": kpi_data["diff"],
        "pct": kpi_data["pct"],
        "status": status,
        "status_emoji": config["emoji"],
        "status_color": config["color"],
        "status_label": config["label"]
    }


def get_period_status_message(data: Dict[str, Any]) -> str:
    """
    Generate a human-readable status message.

    Args:
        data: Dashboard data

    Returns:
        Status message string
    """
    green = data["green_count"]
    yellow = data["yellow_count"]
    red = data["red_count"]

    if red > 0:
        return f"⚠️ {red} KPI(s) por debajo del objetivo"
    elif yellow > 0:
        return f"🟡 {yellow} KPI(s) en riesgo, {green} OK"
    elif green > 0:
        return f"✅ ¡Todos los KPIs alcanzados!"
    else:
        return "📊 Sin datos registrados aún"


def check_monthly_review_complete(agency_id: int, year: int, month: int) -> Dict[str, bool]:
    """
    Check if monthly review is complete.

    Args:
        agency_id: Agency ID
        year: Year
        month: Month

    Returns:
        Dict with completion status for each part
    """
    summary = get_monthly_summary(agency_id, year, month)
    review = get_monthly_review(agency_id, year, month)
    actions = get_action_items(agency_id, year, month)

    has_targets = any(k["target"] > 0 for k in summary)
    has_results = any(k["actual"] > 0 for k in summary)
    has_what_happened = review and review.get("what_happened")
    has_improvement_plan = review and review.get("improvement_plan")
    has_actions = len(actions) > 0

    return {
        "has_targets": has_targets,
        "has_results": has_results,
        "has_what_happened": bool(has_what_happened),
        "has_improvement_plan": bool(has_improvement_plan),
        "has_actions": has_actions,
        "is_complete": has_results and has_what_happened and has_improvement_plan and has_actions
    }
