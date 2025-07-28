"""
SQLAlchemy ORM models for the RaizDigital backend.

Defines tables for users, search orders, and search results.  Enum
classes capture the various states an order or result can be in.  If
you need to alter the schema, consider creating a database migration
instead of editing this file directly in production.
"""
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class OrderStatus(enum.Enum):
    """Enumeration of possible states for a search order."""

    PENDING_PAYMENT = "PENDING_PAYMENT"
    PROCESSING = "PROCESSING"
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_FAILURE = "COMPLETED_FAILURE"


class ResultStatus(enum.Enum):
    """Enumeration of possible states for an individual search result."""

    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    ERROR = "ERROR"


class User(Base):
    """A registered user of the system."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    password_hash: str = Column(String(255), nullable=False)
    full_name: Optional[str] = Column(String(255))
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    orders: List["SearchOrder"] = relationship(
        "SearchOrder", back_populates="user", cascade="all, delete-orphan"
    )


class SearchOrder(Base):
    """Represents a client's request to search for a civil certificate."""

    __tablename__ = "search_orders"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    status: OrderStatus = Column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, nullable=False)
    order_price: float = Column(Float, default=0.0, nullable=False)
    target_name: str = Column(String(255), nullable=False)
    target_dob_approx: Optional[str] = Column(String(50))
    target_city: Optional[str] = Column(String(100))
    target_state: Optional[str] = Column(String(100))
    target_parents_names: Optional[str] = Column(String(255))
    additional_info: Optional[Text] = Column(Text)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Column(DateTime)
    stripe_session_id: Optional[str] = Column(String(255))

    user: User = relationship("User", back_populates="orders")
    results: List["SearchResult"] = relationship(
        "SearchResult", back_populates="order", cascade="all, delete-orphan"
    )


class SearchResult(Base):
    """Stores the outcome of searching a specific source for an order."""

    __tablename__ = "search_results"

    id: int = Column(Integer, primary_key=True, index=True)
    order_id: int = Column(Integer, ForeignKey("search_orders.id"), nullable=False)
    source_name: str = Column(String(255), nullable=False)
    status: ResultStatus = Column(Enum(ResultStatus), nullable=False)
    found_data_json: Optional[Text] = Column(Text)
    screenshot_path: Optional[str] = Column(String(255))
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    order: SearchOrder = relationship("SearchOrder", back_populates="results")


class PasswordResetToken(Base):
    """Stores password reset tokens for users."""

    __tablename__ = "password_reset_tokens"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    token: str = Column(String(255), unique=True, nullable=False)
    expires_at: datetime = Column(DateTime, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    user: User = relationship("User")
