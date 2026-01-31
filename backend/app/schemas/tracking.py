from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field

class TargetCreate(BaseModel):
    agency_id: int
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    targets: Dict[int, float]

class TargetResponse(BaseModel):
    kpi_id: int
    target_value: float

class TargetCopyAllRequest(BaseModel):
    agency_id: int
    year: int
    source_month: int = Field(..., ge=1, le=12)

class TargetCopyNextRequest(BaseModel):
    agency_id: int
    year: int
    source_month: int = Field(..., ge=1, le=12)

class ResultCreate(BaseModel):
    agency_id: int
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    results: Dict[int, float]

class ResultResponse(BaseModel):
    kpi_id: int
    actual_value: float

class ReviewCreate(BaseModel):
    agency_id: int
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    review_date: Optional[date] = None
    what_happened: Optional[str] = None
    improvement_plan: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    review_date: Optional[date]
    what_happened: Optional[str]
    improvement_plan: Optional[str]

class ActionItemCreate(BaseModel):
    agency_id: int
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    title: str = Field(..., min_length=1)

class ActionItemUpdate(BaseModel):
    done: bool

class ActionItemResponse(BaseModel):
    id: int
    title: str
    done: bool
    done_at: Optional[datetime]

    class Config:
        from_attributes = True

class KPISummary(BaseModel):
    kpi_id: int
    kpi_code: str
    kpi_label: Optional[str]
    kpi_unit: Optional[str]
    target: float
    actual: float
    diff: float
    pct: float
    status: str

class MonthlySummaryResponse(BaseModel):
    agency_id: int
    year: int
    month: int
    kpis: List[KPISummary]
    review: Optional[ReviewResponse]
    action_items: List[ActionItemResponse]
