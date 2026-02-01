from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.tracking import ActionItemCreate, ActionItemUpdate, ActionItemResponse
from app.schemas.common import StatusResponse
from app.services import tracking_service, access_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def get_actions(
    agency_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return tracking_service.get_action_items(db, agency_id, year, month)

@router.post("/", response_model=dict)
def create_action(
    request: ActionItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not access_service.user_can_access_agency(db, current_user.id, request.agency_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        item = tracking_service.add_action_item(
            db, request.agency_id, request.year, request.month, request.title
        )
        return {"id": item.id, "title": item.title, "done": item.done}
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{action_id}", response_model=StatusResponse)
def update_action(
    action_id: int,
    request: ActionItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tracking_service.toggle_action_item_done(db, action_id, request.done)
        return StatusResponse(success=True, message="Action item updated")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{action_id}", response_model=StatusResponse)
def delete_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tracking_service.delete_action_item(db, action_id)
        return StatusResponse(success=True, message="Action item deleted")
    except tracking_service.TrackingServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
