from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.auth import (
    LoginRequest, TokenResponse, CurrentUserResponse,
    SecurityCountriesRequest, ForgotPasswordRequest,
    VerifySecurityRequest, ResetPasswordRequest
)
from app.schemas.common import StatusResponse
from app.services import auth_service, onboarding_service
from app.services.jwt_service import create_access_token, create_refresh_token
from app.services.country_service import get_countries_for_setup, get_countries_for_recovery
from app.models.orm import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate_user(db, request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        onboarding_service.update_last_login(db, user.id)

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except auth_service.AuthServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    needs_setup = auth_service.needs_security_setup(db, current_user.id)
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        needs_security_setup=needs_setup,
        onboarding_completed=current_user.onboarding_completed
    )

@router.get("/security-countries")
def get_security_countries_for_setup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_countries_for_setup(db, limit=15)

@router.post("/security-countries", response_model=StatusResponse)
def set_security_countries(
    request: SecurityCountriesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        auth_service.assign_security_countries(db, current_user.id, request.country_ids)
        return StatusResponse(success=True, message="Security countries configured")
    except auth_service.AuthServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/forgot-password/countries")
def get_recovery_countries(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = auth_service.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_country_ids = auth_service.get_user_security_country_ids(db, user.id)
    if not user_country_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not configured security countries"
        )

    return get_countries_for_recovery(db, user_country_ids, total=10)

@router.post("/forgot-password/verify", response_model=StatusResponse)
def verify_security_for_reset(
    request: VerifySecurityRequest,
    db: Session = Depends(get_db)
):
    user = auth_service.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_valid = auth_service.verify_security_countries(db, user.id, request.country_ids)
    return StatusResponse(success=is_valid, message="Verification " + ("successful" if is_valid else "failed"))

@router.post("/forgot-password/reset", response_model=StatusResponse)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = auth_service.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_valid = auth_service.verify_security_countries(db, user.id, request.country_ids)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security verification failed"
        )

    auth_service.reset_password(db, user.id, request.new_password)
    return StatusResponse(success=True, message="Password reset successful")
