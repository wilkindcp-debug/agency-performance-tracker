from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.kpi import KPIResponse
from app.services import kpi_service
from app.models.orm import User

router = APIRouter()

@router.get("/", response_model=List[KPIResponse])
def list_kpis(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return kpi_service.list_kpis(db, active_only=active_only)
