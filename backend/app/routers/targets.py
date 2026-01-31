from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.tracking import TargetCreate, TargetCopyAllRequest, TargetCopyNextRequest
from app.schemas.common import StatusResponse
from app.services import tracking_service, access_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def get_targets(
    agency_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    targets = tracking_service.get_monthly_targets(db, agency_id, year, month)
    return [{"kpi_id": k, "target_value": v} for k, v in targets.items()]

@router.post("/", response_model=StatusResponse)
def set_targets(
    request: TargetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        tracking_service.upsert_monthly_targets(
            db, request.agency_id, request.year, request.month, request.targets
        )
        return StatusResponse(success=True, message="Targets saved")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/copy-all", response_model=StatusResponse)
def copy_targets_to_all(
    request: TargetCopyAllRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        months_updated = tracking_service.copy_targets_to_all_months(
            db, request.agency_id, request.year, request.source_month
        )
        return StatusResponse(success=True, message=f"Targets copied to {months_updated} months")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/copy-next", response_model=StatusResponse)
def copy_targets_to_next(
    request: TargetCopyNextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        tracking_service.copy_targets_to_next_month(
            db, request.agency_id, request.year, request.source_month
        )
        return StatusResponse(success=True, message="Targets copied to next month")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
