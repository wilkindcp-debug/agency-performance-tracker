from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.tracking import ReviewCreate, ReviewResponse
from app.schemas.common import StatusResponse
from app.services import tracking_service, access_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def get_review(
    agency_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    review = tracking_service.get_monthly_review(db, agency_id, year, month)
    return review

@router.post("/", response_model=StatusResponse)
def set_review(
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        tracking_service.upsert_monthly_review(
            db, request.agency_id, request.year, request.month,
            request.review_date, request.what_happened, request.improvement_plan
        )
        return StatusResponse(success=True, message="Review saved")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
