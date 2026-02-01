from pydantic import BaseModel

class CountryResponse(BaseModel):
    id: int
    name: str
    region: str

    class Config:
        from_attributes = True
