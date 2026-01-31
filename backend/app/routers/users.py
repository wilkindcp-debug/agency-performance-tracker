from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, get_current_admin_user
from app.schemas.auth import UserCreate, UserResponse, UserUpdate
from app.schemas.common import StatusResponse
from app.services import auth_service, access_service
from app.models.orm import User, UserSecurityCountry
from app.config import settings

router = APIRouter()

@router.get("/")
def list_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = auth_service.list_users(db)
    result = []
    for u in users:
        has_security = db.query(UserSecurityCountry).filter(
            UserSecurityCountry.user_id == u.id
        ).count() >= settings.REQUIRED_SECURITY_COUNTRIES

        assigned_agencies = access_service.get_assigned_agency_ids(db, u.id)

        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "active": u.active,
            "created_at": u.created_at,
            "has_security": has_security,
            "assigned_agency_ids": assigned_agencies
        })

    return result

@router.post("/", response_model=dict)
def create_user(
    request: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        user = auth_service.create_user(
            db, request.username, request.password, request.role
        )
        return {"id": user.id, "username": user.username}
    except auth_service.AuthServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{user_id}", response_model=StatusResponse)
def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        if request.role is not None:
            auth_service.update_user_role(db, user_id, request.role)
        if request.active is not None:
            auth_service.toggle_user_active(db, user_id, request.active)
        return StatusResponse(success=True, message="User updated")
    except auth_service.AuthServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{user_id}/status", response_model=StatusResponse)
def update_user_status(
    user_id: int,
    active: bool,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        auth_service.toggle_user_active(db, user_id, active)
        return StatusResponse(success=True, message="User status updated")
    except auth_service.AuthServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{user_id}/agencies", response_model=StatusResponse)
def set_user_agencies(
    user_id: int,
    agency_ids: List[int],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        access_service.set_user_agencies(db, user_id, agency_ids)
        return StatusResponse(success=True, message="User agencies updated")
    except access_service.AccessServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}/agencies")
def get_user_agencies(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return access_service.get_user_agencies(db, user_id)
