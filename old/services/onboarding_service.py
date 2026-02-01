"""
Onboarding Service - Manage user onboarding flow and status tracking.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from db.database import SessionLocal
from db.models import User
from services.tracking_service import (
    get_monthly_targets,
    get_monthly_results,
    get_monthly_review,
    get_action_items
)
from services.access_service import get_user_agencies


def is_onboarding_completed(user_id: int) -> bool:
    """
    Check if user has completed onboarding.

    Args:
        user_id: User ID

    Returns:
        True if onboarding is completed
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.onboarding_completed if user else False
    finally:
        db.close()


def complete_onboarding(user_id: int) -> None:
    """
    Mark onboarding as completed for a user.

    Args:
        user_id: User ID
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.onboarding_completed = True
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def update_last_login(user_id: int) -> None:
    """
    Update last login timestamp.

    Args:
        user_id: User ID
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def get_onboarding_checklist(user_id: int, year: int, month: int) -> Dict[str, bool]:
    """
    Get onboarding checklist status for a user.
    Checks if key tasks have been completed.

    Args:
        user_id: User ID
        year: Current year
        month: Current month

    Returns:
        Dict with checklist items and their completion status
    """
    agencies = get_user_agencies(user_id)

    if not agencies:
        return {
            "has_agency": False,
            "viewed_targets": False,
            "reviewed_previous": False,
            "completed_review": False,
            "defined_actions": False
        }

    agency_id = agencies[0]["id"]  # Primary agency

    # Check targets exist for current month
    targets = get_monthly_targets(agency_id, year, month)
    has_targets = len(targets) > 0

    # Check previous month review (if applicable)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_review = get_monthly_review(agency_id, prev_year, prev_month)
    has_prev_review = prev_review is not None and (
        prev_review.get("what_happened") or prev_review.get("improvement_plan")
    )

    # Check current month review
    current_review = get_monthly_review(agency_id, year, month)
    has_current_review = current_review is not None and (
        current_review.get("what_happened") or current_review.get("improvement_plan")
    )

    # Check actions defined
    actions = get_action_items(agency_id, year, month)
    has_actions = len(actions) > 0

    return {
        "has_agency": True,
        "viewed_targets": has_targets,
        "reviewed_previous": has_prev_review or month == 1,  # First month doesn't need previous
        "completed_review": has_current_review,
        "defined_actions": has_actions
    }


def is_checklist_complete(checklist: Dict[str, bool]) -> bool:
    """
    Check if all checklist items are complete.

    Args:
        checklist: Checklist dict from get_onboarding_checklist

    Returns:
        True if all items are complete
    """
    if not checklist.get("has_agency"):
        return False

    return all([
        checklist.get("viewed_targets"),
        checklist.get("reviewed_previous"),
        checklist.get("completed_review"),
        checklist.get("defined_actions")
    ])


def get_user_primary_agency(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the primary (first) agency for a user.

    Args:
        user_id: User ID

    Returns:
        Agency dict or None
    """
    agencies = get_user_agencies(user_id)
    return agencies[0] if agencies else None
