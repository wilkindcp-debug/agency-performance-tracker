from typing import Optional
from pydantic import BaseModel

class KPIResponse(BaseModel):
    id: int
    code: str
    label: Optional[str]
    unit: Optional[str]
    active: bool

    class Config:
        from_attributes = True

class KPICreate(BaseModel):
    code: str
    label: Optional[str] = None
    unit: Optional[str] = None

class KPIUpdate(BaseModel):
    label: Optional[str] = None
    unit: Optional[str] = None
    active: Optional[bool] = None
