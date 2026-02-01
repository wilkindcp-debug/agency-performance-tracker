from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.orm import User
from app.services.tracking_service import (
    get_monthly_targets,
    get_monthly_review,
    get_action_items
)
from app.services.access_service import get_user_agencies


def is_onboarding_completed(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return user.onboarding_completed if user else False


def complete_onboarding(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.onboarding_completed = True
        db.commit()


def update_last_login(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login_at = datetime.utcnow()
        db.commit()


def get_onboarding_checklist(
    db: Session,
    user_id: int,
    year: int,
    month: int
) -> Dict[str, bool]:
    agencies = get_user_agencies(db, user_id)

    if not agencies:
        return {
            "has_agency": False,
            "viewed_targets": False,
            "reviewed_previous": False,
            "completed_review": False,
            "defined_actions": False
        }

    agency_id = agencies[0]["id"]

    targets = get_monthly_targets(db, agency_id, year, month)
    has_targets = len(targets) > 0

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_review = get_monthly_review(db, agency_id, prev_year, prev_month)
    has_prev_review = prev_review is not None and (
        prev_review.get("what_happened") or prev_review.get("improvement_plan")
    )

    current_review = get_monthly_review(db, agency_id, year, month)
    has_current_review = current_review is not None and (
        current_review.get("what_happened") or current_review.get("improvement_plan")
    )

    actions = get_action_items(db, agency_id, year, month)
    has_actions = len(actions) > 0

    return {
        "has_agency": True,
        "viewed_targets": has_targets,
        "reviewed_previous": has_prev_review or month == 1,
        "completed_review": has_current_review,
        "defined_actions": has_actions
    }


def is_checklist_complete(checklist: Dict[str, bool]) -> bool:
    if not checklist.get("has_agency"):
        return False

    return all([
        checklist.get("viewed_targets"),
        checklist.get("reviewed_previous"),
        checklist.get("completed_review"),
        checklist.get("defined_actions")
    ])


def get_user_primary_agency(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    agencies = get_user_agencies(db, user_id)
    return agencies[0] if agencies else None
