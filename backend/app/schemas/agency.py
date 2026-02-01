from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field

class ManagerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None

class ManagerResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    active: bool

    class Config:
        from_attributes = True

class KPIBrief(BaseModel):
    id: int
    code: str
    label: Optional[str]

    class Config:
        from_attributes = True

class AgencyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=255)
    manager_name: str = Field(..., min_length=2, max_length=255)
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None
    kpi_ids: Optional[List[int]] = None

class AgencyResponse(BaseModel):
    id: int
    name: str
    city: Optional[str]
    active: bool
    created_at: datetime
    manager: Optional[ManagerResponse]
    kpis: List[KPIBrief]

    class Config:
        from_attributes = True

class AgencyListItem(BaseModel):
    id: int
    name: str
    city: Optional[str]
    active: bool
    manager_name: Optional[str]
    kpi_count: int

class AgencyDetail(BaseModel):
    id: int
    name: str
    city: Optional[str]
    active: bool
    created_at: datetime
    active_manager: Optional[ManagerResponse]
    manager_history: List[ManagerResponse]
    kpis: List[KPIBrief]

class AgencyKPIsUpdate(BaseModel):
    kpi_ids: List[int]

class AgencyStatusUpdate(BaseModel):
    active: bool
