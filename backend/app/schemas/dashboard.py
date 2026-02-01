from typing import Optional, List
from pydantic import BaseModel
from app.schemas.tracking import KPISummary

class AgencySummary(BaseModel):
    agency_id: int
    agency_name: str
    city: Optional[str]
    manager_name: Optional[str]
    avg_pct: float
    red_count: int
    yellow_count: int
    green_count: int
    kpi_details: List[KPISummary]

class DashboardResponse(BaseModel):
    year: int
    month: int
    agencies: List[AgencySummary]
    total_agencies: int
    avg_performance: float
    alerts_count: int
