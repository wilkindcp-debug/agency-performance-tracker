from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.orm import User, UserAgency, Agency

class AccessServiceError(Exception):
    pass

def get_user_agencies(db: Session, user_id: int) -> List[Dict[str, Any]]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    if user.role == "ADMIN":
        agencies = db.query(Agency).filter(Agency.active == True).order_by(Agency.name).all()
    else:
        agencies = db.query(Agency).join(UserAgency).filter(
            UserAgency.user_id == user_id,
            Agency.active == True
        ).order_by(Agency.name).all()

    return [
        {
            "id": a.id,
            "name": a.name,
            "city": a.city
        }
        for a in agencies
    ]

def get_user_agency_ids(db: Session, user_id: int) -> List[int]:
    agencies = get_user_agencies(db, user_id)
    return [a["id"] for a in agencies]

def user_can_access_agency(db: Session, user_id: int, agency_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    if user.role == "ADMIN":
        return True

    assignment = db.query(UserAgency).filter(
        UserAgency.user_id == user_id,
        UserAgency.agency_id == agency_id
    ).first()

    return assignment is not None

def assign_agency_to_user(db: Session, user_id: int, agency_id: int) -> None:
    existing = db.query(UserAgency).filter(
        UserAgency.user_id == user_id,
        UserAgency.agency_id == agency_id
    ).first()

    if not existing:
        assignment = UserAgency(
            user_id=user_id,
            agency_id=agency_id
        )
        db.add(assignment)
        db.commit()

def remove_agency_from_user(db: Session, user_id: int, agency_id: int) -> None:
    db.query(UserAgency).filter(
        UserAgency.user_id == user_id,
        UserAgency.agency_id == agency_id
    ).delete()
    db.commit()

def set_user_agencies(db: Session, user_id: int, agency_ids: List[int]) -> None:
    db.query(UserAgency).filter(UserAgency.user_id == user_id).delete()

    for agency_id in agency_ids:
        assignment = UserAgency(
            user_id=user_id,
            agency_id=agency_id
        )
        db.add(assignment)

    db.commit()

def get_assigned_agency_ids(db: Session, user_id: int) -> List[int]:
    assignments = db.query(UserAgency).filter(
        UserAgency.user_id == user_id
    ).all()
    return [a.agency_id for a in assignments]

def is_admin(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return user is not None and user.role == "ADMIN"

def filter_agencies_for_user(db: Session, user: User, agencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not user:
        return []

    if user.role == "ADMIN":
        return agencies

    allowed_ids = set(get_user_agency_ids(db, user.id))
    return [a for a in agencies if a["id"] in allowed_ids]
