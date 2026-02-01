from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.tracking import ResultCreate
from app.schemas.common import StatusResponse
from app.services import tracking_service, access_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def get_results(
    agency_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    results = tracking_service.get_monthly_results(db, agency_id, year, month)
    return [{"kpi_id": k, "actual_value": v} for k, v in results.items()]

@router.post("/", response_model=StatusResponse)
def set_results(
    request: ResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        tracking_service.upsert_monthly_results(
            db, request.agency_id, request.year, request.month,
            request.results, recorded_by=current_user.username
        )
        return StatusResponse(success=True, message="Results saved")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
