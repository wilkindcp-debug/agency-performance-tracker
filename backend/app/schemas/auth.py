from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    role: str = Field(default="NORMAL", pattern="^(ADMIN|NORMAL)$")

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    active: bool
    created_at: datetime
    has_security: bool = False

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    role: Optional[str] = Field(None, pattern="^(ADMIN|NORMAL)$")
    active: Optional[bool] = None

class SecurityCountriesRequest(BaseModel):
    country_ids: List[int] = Field(..., min_length=5, max_length=5)

class ForgotPasswordRequest(BaseModel):
    username: str

class VerifySecurityRequest(BaseModel):
    username: str
    country_ids: List[int]

class ResetPasswordRequest(BaseModel):
    username: str
    country_ids: List[int]
    new_password: str = Field(..., min_length=8)

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class CurrentUserResponse(BaseModel):
    id: int
    username: str
    role: str
    needs_security_setup: bool
    onboarding_completed: bool = False

    class Config:
        from_attributes = True
