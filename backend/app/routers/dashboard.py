from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services import tracking_service, access_service, dashboard_service, onboarding_service
from app.models.orm import User
from app.utils.helpers import get_current_year, get_current_month

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    year: int = Query(None),
    month: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if year is None:
        year = get_current_year()
    if month is None:
        month = get_current_month()

    all_summaries = tracking_service.get_all_agencies_summary(db, year, month)

    summaries = access_service.filter_agencies_for_user(
        db, current_user,
        [{"id": s["agency_id"], **s} for s in all_summaries]
    )

    filtered_summaries = [s for s in all_summaries if s["agency_id"] in {a["id"] for a in summaries}]

    total_agencies = len(filtered_summaries)
    avg_performance = (
        sum(s["avg_pct"] for s in filtered_summaries) / total_agencies
        if total_agencies > 0 else 0
    )
    alerts_count = sum(s["red_count"] for s in filtered_summaries)

    return {
        "year": year,
        "month": month,
        "agencies": filtered_summaries,
        "total_agencies": total_agencies,
        "avg_performance": round(avg_performance, 1),
        "alerts_count": alerts_count
    }


@router.get("/admin")
def get_admin_dashboard(
    year: int = Query(None),
    month: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    if year is None:
        year = get_current_year()
    if month is None:
        month = get_current_month()

    return dashboard_service.get_admin_dashboard_data(db, year, month)


@router.get("/normal")
def get_normal_dashboard(
    year: int = Query(None),
    month: int = Query(None),
    agency_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if year is None:
        year = get_current_year()
    if month is None:
        month = get_current_month()

    data = dashboard_service.get_normal_dashboard_data(
        db, current_user.id, year, month, agency_id
    )

    onboarding_completed = onboarding_service.is_onboarding_completed(db, current_user.id)
    checklist = onboarding_service.get_onboarding_checklist(db, current_user.id, year, month)

    return {
        **data,
        "onboarding_completed": onboarding_completed,
        "checklist": checklist,
        "year": year,
        "month": month
    }


@router.post("/complete-onboarding")
def complete_user_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    onboarding_service.complete_onboarding(db, current_user.id)
    return {"success": True}


@router.get("/agency/{agency_id}/summary")
def get_agency_summary(
    agency_id: int,
    year: int = Query(None),
    month: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if year is None:
        year = get_current_year()
    if month is None:
        month = get_current_month()

    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        return {"error": "Access denied"}

    data = dashboard_service.get_agency_dashboard_data(db, agency_id, year, month)

    if not data:
        return {"error": "Agency not found"}

    return data
