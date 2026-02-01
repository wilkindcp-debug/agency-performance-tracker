from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, get_current_admin_user
from app.schemas.agency import (
    AgencyCreate, AgencyResponse, AgencyDetail,
    AgencyKPIsUpdate, AgencyStatusUpdate
)
from app.schemas.common import StatusResponse
from app.services import agency_service, access_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def list_agencies(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agencies = agency_service.list_agencies(db, active_only=active_only)
    return access_service.filter_agencies_for_user(db, current_user, agencies)

@router.post("/", response_model=dict)
def create_agency(
    request: AgencyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        agency = agency_service.create_agency(
            db,
            name=request.name,
            city=request.city,
            manager_name=request.manager_name,
            manager_email=request.manager_email,
            manager_phone=request.manager_phone,
            kpi_ids=request.kpi_ids
        )
        return {"id": agency.id, "name": agency.name}
    except agency_service.AgencyServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{agency_id}")
def get_agency(
    agency_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    agency = agency_service.get_agency_detail(db, agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")

    return agency

@router.patch("/{agency_id}/status", response_model=StatusResponse)
def update_agency_status(
    agency_id: int,
    request: AgencyStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        agency_service.toggle_agency_active(db, agency_id, request.active)
        return StatusResponse(success=True, message="Agency status updated")
    except agency_service.AgencyServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{agency_id}/kpis", response_model=StatusResponse)
def update_agency_kpis(
    agency_id: int,
    request: AgencyKPIsUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        agency_service.update_agency_kpis(db, agency_id, request.kpi_ids)
        return StatusResponse(success=True, message="Agency KPIs updated")
    except agency_service.AgencyServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{agency_id}/kpis")
def get_agency_kpis(
    agency_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    kpis = agency_service.get_agency_kpis(db, agency_id)
    return [{"id": k.id, "code": k.code, "label": k.label, "unit": k.unit} for k in kpis]
