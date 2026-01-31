from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.country import CountryResponse
from app.services import country_service
from app.models.orm import User

router = APIRouter()

@router.get("/")
def list_countries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return country_service.list_all_countries(db)

@router.get("/for-setup")
def get_countries_for_setup(
    limit: int = Query(15),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return country_service.get_countries_for_setup(db, limit=limit)
