"""
Pydantic schemas for request and response bodies.

These classes define the shape of data exchanged with the API.  Using
Pydantic models helps ensure that incoming data is validated and that
outgoing data is serialised in a predictable manner.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class OrderStatusEnum(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PROCESSING = "PROCESSING"
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_FAILURE = "COMPLETED_FAILURE"


class ResultStatusEnum(str, Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    ERROR = "ERROR"


class UserCreate(BaseModel):
    """Schema used when registering a new user."""

    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    """Public representation of a user."""

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema returned when a user logs in successfully."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token information used for authentication."""

    user_id: Optional[int] = None


class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for resetting a password with a token."""

    token: str
    new_password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating user profile information."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class SearchResultCreate(BaseModel):
    """Schema used by the robot to submit search results."""

    order_id: int
    source_name: str
    status: ResultStatusEnum
    found_data_json: Optional[str] = None
    screenshot_path: Optional[str] = None


class SearchResultOut(BaseModel):
    """Public representation of a search result."""

    id: int
    source_name: str
    status: ResultStatusEnum
    found_data_json: Optional[str]
    screenshot_path: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


class SearchOrderCreate(BaseModel):
    """Schema used when a user creates a new search order."""

    target_name: str
    order_price: float
    target_dob_approx: Optional[str] = None
    target_city: Optional[str] = None
    target_state: Optional[str] = None
    target_parents_names: Optional[str] = None
    additional_info: Optional[str] = None


class SearchOrderOut(BaseModel):
    """Public representation of a search order, including results."""

    id: int
    status: OrderStatusEnum
    order_price: float
    target_name: str
    target_dob_approx: Optional[str]
    target_city: Optional[str]
    target_state: Optional[str]
    target_parents_names: Optional[str]
    additional_info: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    results: List[SearchResultOut] = []

    class Config:
        orm_mode = True
