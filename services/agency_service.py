"""
Agency Service - Business logic for agency operations.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.database import SessionLocal
from db.models import Agency, AgencyManager, AgencyKPI, KPI


class AgencyServiceError(Exception):
    """Custom exception for agency service errors."""
    pass


def create_agency(
    name: str,
    city: str,
    manager_name: str,
    manager_email: Optional[str] = None,
    manager_phone: Optional[str] = None,
    kpi_ids: Optional[List[int]] = None
) -> Agency:
    """
    Create a new agency with its manager and assigned KPIs.
    Uses transaction with rollback on error.

    Args:
        name: Agency name (must be unique)
        city: Agency city
        manager_name: Full name of the manager
        manager_email: Manager's email (optional)
        manager_phone: Manager's phone (optional)
        kpi_ids: List of KPI IDs to assign to this agency

    Returns:
        Created Agency object

    Raises:
        AgencyServiceError: If agency name already exists or other error
    """
    db = SessionLocal()
    try:
        # Check if agency name already exists
        existing = db.query(Agency).filter(Agency.name == name).first()
        if existing:
            raise AgencyServiceError(f"Ya existe una agencia con el nombre '{name}'")

        # Create agency
        agency = Agency(
            name=name,
            city=city,
            active=True
        )
        db.add(agency)
        db.flush()  # Get the agency ID

        # Create manager
        manager = AgencyManager(
            agency_id=agency.id,
            full_name=manager_name,
            email=manager_email,
            phone=manager_phone,
            start_date=date.today(),
            active=True
        )
        db.add(manager)

        # Assign KPIs
        if kpi_ids:
            for kpi_id in kpi_ids:
                agency_kpi = AgencyKPI(
                    agency_id=agency.id,
                    kpi_id=kpi_id,
                    active=True
                )
                db.add(agency_kpi)

        db.commit()
        db.refresh(agency)
        return agency

    except IntegrityError as e:
        db.rollback()
        raise AgencyServiceError(f"Error de integridad: {str(e)}")
    except Exception as e:
        db.rollback()
        raise AgencyServiceError(f"Error al crear agencia: {str(e)}")
    finally:
        db.close()


def list_agencies(active_only: bool = True) -> List[Dict[str, Any]]:
    """
    List all agencies with their active manager.

    Args:
        active_only: If True, only return active agencies

    Returns:
        List of dicts with agency info and active manager
    """
    db = SessionLocal()
    try:
        query = db.query(Agency)
        if active_only:
            query = query.filter(Agency.active == True)

        agencies = query.order_by(Agency.name).all()
        result = []

        for agency in agencies:
            # Get active manager
            active_manager = db.query(AgencyManager).filter(
                AgencyManager.agency_id == agency.id,
                AgencyManager.active == True
            ).first()

            # Get assigned KPIs
            assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
                AgencyKPI.agency_id == agency.id,
                AgencyKPI.active == True
            ).all()

            result.append({
                "id": agency.id,
                "name": agency.name,
                "city": agency.city,
                "active": agency.active,
                "created_at": agency.created_at,
                "manager": {
                    "id": active_manager.id if active_manager else None,
                    "name": active_manager.full_name if active_manager else None,
                    "email": active_manager.email if active_manager else None,
                    "phone": active_manager.phone if active_manager else None,
                } if active_manager else None,
                "kpis": [{"id": k.id, "code": k.code, "label": k.label} for k in assigned_kpis]
            })

        return result
    finally:
        db.close()


def get_agency_detail(agency_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific agency.

    Args:
        agency_id: The agency ID

    Returns:
        Dict with agency details or None if not found
    """
    db = SessionLocal()
    try:
        agency = db.query(Agency).filter(Agency.id == agency_id).first()
        if not agency:
            return None

        # Get all managers (for history)
        managers = db.query(AgencyManager).filter(
            AgencyManager.agency_id == agency_id
        ).order_by(AgencyManager.start_date.desc()).all()

        # Get active manager
        active_manager = next((m for m in managers if m.active), None)

        # Get assigned KPIs
        assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
            AgencyKPI.agency_id == agency_id,
            AgencyKPI.active == True
        ).all()

        return {
            "id": agency.id,
            "name": agency.name,
            "city": agency.city,
            "active": agency.active,
            "created_at": agency.created_at,
            "active_manager": {
                "id": active_manager.id,
                "name": active_manager.full_name,
                "email": active_manager.email,
                "phone": active_manager.phone,
                "start_date": active_manager.start_date,
            } if active_manager else None,
            "manager_history": [
                {
                    "id": m.id,
                    "name": m.full_name,
                    "start_date": m.start_date,
                    "end_date": m.end_date,
                    "active": m.active
                } for m in managers
            ],
            "kpis": [{"id": k.id, "code": k.code, "label": k.label, "unit": k.unit} for k in assigned_kpis]
        }
    finally:
        db.close()


def get_agency_kpis(agency_id: int) -> List[KPI]:
    """
    Get the KPIs assigned to a specific agency.

    Args:
        agency_id: The agency ID

    Returns:
        List of KPI objects
    """
    db = SessionLocal()
    try:
        return db.query(KPI).join(AgencyKPI).filter(
            AgencyKPI.agency_id == agency_id,
            AgencyKPI.active == True
        ).order_by(KPI.code).all()
    finally:
        db.close()


def update_agency_kpis(agency_id: int, kpi_ids: List[int]) -> None:
    """
    Update the KPIs assigned to an agency.
    Deactivates removed KPIs and adds new ones.

    Args:
        agency_id: The agency ID
        kpi_ids: List of KPI IDs to assign
    """
    db = SessionLocal()
    try:
        # Get current assignments
        current = db.query(AgencyKPI).filter(
            AgencyKPI.agency_id == agency_id
        ).all()

        current_kpi_ids = {ak.kpi_id for ak in current}
        new_kpi_ids = set(kpi_ids)

        # Deactivate removed KPIs
        for ak in current:
            if ak.kpi_id not in new_kpi_ids:
                ak.active = False
            else:
                ak.active = True

        # Add new KPIs
        for kpi_id in new_kpi_ids - current_kpi_ids:
            agency_kpi = AgencyKPI(
                agency_id=agency_id,
                kpi_id=kpi_id,
                active=True
            )
            db.add(agency_kpi)

        db.commit()
    except Exception as e:
        db.rollback()
        raise AgencyServiceError(f"Error al actualizar KPIs: {str(e)}")
    finally:
        db.close()


def get_agencies_for_select() -> List[tuple]:
    """
    Get agencies formatted for UI selectbox.

    Returns:
        List of tuples (agency_id, agency_name)
    """
    agencies = list_agencies(active_only=True)
    return [(a["id"], f"{a['name']} ({a['city']})") for a in agencies]


def toggle_agency_active(agency_id: int, active: bool) -> None:
    """
    Toggle the active status of an agency.

    Args:
        agency_id: The agency ID
        active: New active status
    """
    db = SessionLocal()
    try:
        agency = db.query(Agency).filter(Agency.id == agency_id).first()
        if agency:
            agency.active = active
            db.commit()
    except Exception as e:
        db.rollback()
        raise AgencyServiceError(f"Error al cambiar estado: {str(e)}")
    finally:
        db.close()
