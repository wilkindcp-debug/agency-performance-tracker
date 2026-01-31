"""
Access Service - Authorization and access control.
"""
from typing import List, Optional, Dict, Any
from db.database import SessionLocal
from db.models import User, UserAgency, Agency


class AccessServiceError(Exception):
    """Custom exception for access service errors."""
    pass


def get_user_agencies(user_id: int) -> List[Dict[str, Any]]:
    """
    Get the agencies a user has access to.
    ADMIN users have access to all agencies.
    NORMAL users only have access to assigned agencies.

    Args:
        user_id: User ID

    Returns:
        List of agency dicts
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        if user.role == "ADMIN":
            # ADMIN has access to all agencies
            agencies = db.query(Agency).filter(Agency.active == True).order_by(Agency.name).all()
        else:
            # NORMAL user only has assigned agencies
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
    finally:
        db.close()


def get_user_agency_ids(user_id: int) -> List[int]:
    """
    Get the IDs of agencies a user has access to.

    Args:
        user_id: User ID

    Returns:
        List of agency IDs
    """
    agencies = get_user_agencies(user_id)
    return [a["id"] for a in agencies]


def user_can_access_agency(user_id: int, agency_id: int) -> bool:
    """
    Check if a user can access a specific agency.

    Args:
        user_id: User ID
        agency_id: Agency ID to check

    Returns:
        True if user can access the agency
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        if user.role == "ADMIN":
            # ADMIN can access all agencies
            return True

        # Check if NORMAL user has assignment
        assignment = db.query(UserAgency).filter(
            UserAgency.user_id == user_id,
            UserAgency.agency_id == agency_id
        ).first()

        return assignment is not None
    finally:
        db.close()


def assign_agency_to_user(user_id: int, agency_id: int) -> None:
    """
    Assign an agency to a user.

    Args:
        user_id: User ID
        agency_id: Agency ID to assign
    """
    db = SessionLocal()
    try:
        # Check if already assigned
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
    except Exception as e:
        db.rollback()
        raise AccessServiceError(f"Error al asignar agencia: {str(e)}")
    finally:
        db.close()


def remove_agency_from_user(user_id: int, agency_id: int) -> None:
    """
    Remove an agency assignment from a user.

    Args:
        user_id: User ID
        agency_id: Agency ID to remove
    """
    db = SessionLocal()
    try:
        db.query(UserAgency).filter(
            UserAgency.user_id == user_id,
            UserAgency.agency_id == agency_id
        ).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise AccessServiceError(f"Error al quitar agencia: {str(e)}")
    finally:
        db.close()


def set_user_agencies(user_id: int, agency_ids: List[int]) -> None:
    """
    Set the complete list of agencies for a user.
    Replaces all existing assignments.

    Args:
        user_id: User ID
        agency_ids: List of agency IDs to assign
    """
    db = SessionLocal()
    try:
        # Remove all existing assignments
        db.query(UserAgency).filter(UserAgency.user_id == user_id).delete()

        # Add new assignments
        for agency_id in agency_ids:
            assignment = UserAgency(
                user_id=user_id,
                agency_id=agency_id
            )
            db.add(assignment)

        db.commit()
    except Exception as e:
        db.rollback()
        raise AccessServiceError(f"Error al actualizar agencias: {str(e)}")
    finally:
        db.close()


def get_assigned_agency_ids(user_id: int) -> List[int]:
    """
    Get explicitly assigned agency IDs for a user.
    Unlike get_user_agency_ids, this doesn't consider ADMIN role.

    Args:
        user_id: User ID

    Returns:
        List of assigned agency IDs
    """
    db = SessionLocal()
    try:
        assignments = db.query(UserAgency).filter(
            UserAgency.user_id == user_id
        ).all()
        return [a.agency_id for a in assignments]
    finally:
        db.close()


def is_admin(user_id: int) -> bool:
    """
    Check if a user is an admin.

    Args:
        user_id: User ID

    Returns:
        True if user is ADMIN
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user is not None and user.role == "ADMIN"
    finally:
        db.close()


def require_admin(user: Dict[str, Any]) -> None:
    """
    Require that the current user is an admin.

    Args:
        user: User dict from session

    Raises:
        AccessServiceError: If user is not admin
    """
    if not user or user.get("role") != "ADMIN":
        raise AccessServiceError("Esta acción requiere permisos de administrador")


def filter_agencies_for_user(user: Dict[str, Any], agencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter a list of agencies to only those the user can access.

    Args:
        user: User dict from session
        agencies: List of agency dicts

    Returns:
        Filtered list of agencies
    """
    if not user:
        return []

    if user.get("role") == "ADMIN":
        return agencies

    allowed_ids = set(get_user_agency_ids(user["id"]))
    return [a for a in agencies if a["id"] in allowed_ids]
