from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.orm import Agency, MonthlyReview, MonthlyResult, User
from app.services.tracking_service import get_monthly_summary, get_monthly_review, get_action_items
from app.services.agency_service import list_agencies, get_agency_detail
from app.services.access_service import get_user_agencies
from app.utils.helpers import month_name


def get_agency_dashboard_data(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> Optional[Dict[str, Any]]:
    agency_detail = get_agency_detail(db, agency_id)
    if not agency_detail:
        return None

    agency = {
        "id": agency_detail["id"],
        "name": agency_detail["name"],
        "city": agency_detail["city"],
        "manager": agency_detail.get("active_manager")
    }

    kpi_summary = get_monthly_summary(db, agency_id, year, month)

    green_count = sum(1 for k in kpi_summary if k["status"] == "green")
    yellow_count = sum(1 for k in kpi_summary if k["status"] == "yellow")
    red_count = sum(1 for k in kpi_summary if k["status"] == "red")

    if red_count > 0:
        overall_status = "red"
    elif yellow_count > 0:
        overall_status = "yellow"
    elif green_count > 0:
        overall_status = "green"
    else:
        overall_status = "none"

    review = get_monthly_review(db, agency_id, year, month)

    actions = get_action_items(db, agency_id, year, month)
    pending_actions = [a for a in actions if not a["done"]]
    completed_actions = [a for a in actions if a["done"]]

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


def get_admin_dashboard_data(db: Session, year: int, month: int) -> Dict[str, Any]:
    agencies = list_agencies(db, active_only=True)

    agencies_data = []
    total_green = 0
    total_yellow = 0
    total_red = 0
    pending_reviews = []

    for agency in agencies:
        agency_data = get_agency_dashboard_data(db, agency["id"], year, month)
        if agency_data:
            agencies_data.append(agency_data)

            total_green += agency_data["green_count"]
            total_yellow += agency_data["yellow_count"]
            total_red += agency_data["red_count"]

            if agency_data["review_pending"]:
                pending_reviews.append({
                    "agency_id": agency["id"],
                    "agency_name": agency["name"],
                    "manager_name": agency["manager"]["full_name"] if agency["manager"] else "Sin jefe"
                })

    agencies_data.sort(
        key=lambda x: (
            -x["red_count"],
            -x["yellow_count"],
            x["green_count"]
        )
    )

    at_risk = [a for a in agencies_data if a["red_count"] > 0]

    total_kpis = total_green + total_yellow + total_red
    health_pct = (total_green / total_kpis * 100) if total_kpis > 0 else 0

    return {
        "year": year,
        "month": month,
        "month_name": month_name(month),
        "total_agencies": len(agencies_data),
        "total_green": total_green,
        "total_yellow": total_yellow,
        "total_red": total_red,
        "health_pct": round(health_pct, 1),
        "agencies": agencies_data,
        "at_risk": at_risk,
        "pending_reviews": pending_reviews
    }


def get_normal_dashboard_data(
    db: Session,
    user_id: int,
    year: int,
    month: int,
    agency_id: Optional[int] = None
) -> Dict[str, Any]:
    agencies = get_user_agencies(db, user_id)

    if not agencies:
        return {
            "has_agencies": False,
            "agencies": [],
            "selected_agency": None,
            "dashboard": None
        }

    if agency_id is None:
        agency_id = agencies[0]["id"]

    selected_agency = next((a for a in agencies if a["id"] == agency_id), agencies[0])

    dashboard = get_agency_dashboard_data(db, selected_agency["id"], year, month)

    return {
        "has_agencies": True,
        "agencies": agencies,
        "selected_agency": selected_agency,
        "dashboard": dashboard
    }


def get_kpi_card_data(kpi_data: Dict[str, Any]) -> Dict[str, Any]:
    status = kpi_data["status"]

    status_config = {
        "green": {"color": "#28a745", "label": "Alcanzado"},
        "yellow": {"color": "#ffc107", "label": "En riesgo"},
        "red": {"color": "#dc3545", "label": "No alcanzado"}
    }

    config = status_config.get(status, {"color": "#6c757d", "label": "Sin datos"})

    return {
        "code": kpi_data["kpi_code"],
        "label": kpi_data["kpi_label"],
        "unit": kpi_data["kpi_unit"],
        "target": kpi_data["target"],
        "actual": kpi_data["actual"],
        "diff": kpi_data["diff"],
        "pct": kpi_data["pct"],
        "status": status,
        "status_color": config["color"],
        "status_label": config["label"]
    }


def check_monthly_review_complete(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> Dict[str, bool]:
    summary = get_monthly_summary(db, agency_id, year, month)
    review = get_monthly_review(db, agency_id, year, month)
    actions = get_action_items(db, agency_id, year, month)

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
