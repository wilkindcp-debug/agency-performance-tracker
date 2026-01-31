"""
KPI Service - Business logic for KPI operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import KPI


def list_kpis(active_only: bool = True) -> List[KPI]:
    """
    List all KPIs.

    Args:
        active_only: If True, only return active KPIs

    Returns:
        List of KPI objects
    """
    db = SessionLocal()
    try:
        query = db.query(KPI)
        if active_only:
            query = query.filter(KPI.active == True)
        return query.order_by(KPI.code).all()
    finally:
        db.close()


def get_kpi_by_id(kpi_id: int) -> Optional[KPI]:
    """
    Get a KPI by its ID.

    Args:
        kpi_id: The KPI ID

    Returns:
        KPI object or None if not found
    """
    db = SessionLocal()
    try:
        return db.query(KPI).filter(KPI.id == kpi_id).first()
    finally:
        db.close()


def get_kpi_by_code(code: str) -> Optional[KPI]:
    """
    Get a KPI by its code.

    Args:
        code: The KPI code (e.g., "Capital Services", "RIA")

    Returns:
        KPI object or None if not found
    """
    db = SessionLocal()
    try:
        return db.query(KPI).filter(KPI.code == code).first()
    finally:
        db.close()


def get_kpis_dict() -> dict:
    """
    Get a dictionary mapping KPI id to KPI object.

    Returns:
        Dict of {kpi_id: KPI}
    """
    kpis = list_kpis(active_only=True)
    return {kpi.id: kpi for kpi in kpis}


def get_kpi_options() -> List[tuple]:
    """
    Get KPIs formatted for UI selectbox/multiselect.

    Returns:
        List of tuples (kpi_id, display_text)
    """
    kpis = list_kpis(active_only=True)
    return [(kpi.id, f"{kpi.code} - {kpi.label}") for kpi in kpis]
