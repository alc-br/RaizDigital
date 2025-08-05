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
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    orders: Mapped[List["SearchOrder"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SearchOrder(Base):
    """Represents a client's request to search for a civil certificate."""

    __tablename__ = "search_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, nullable=False)
    order_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    target_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_dob_approx: Mapped[Optional[str]] = mapped_column(String(50))
    target_city: Mapped[Optional[str]] = mapped_column(String(100))
    target_state: Mapped[Optional[str]] = mapped_column(String(100))
    target_parents_names: Mapped[Optional[str]] = mapped_column(String(255))
    additional_info: Mapped[Optional[str]] = mapped_column(Text) # Use Optional[str] for Text column
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="orders")
    results: Mapped[List["SearchResult"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class SearchResult(Base):
    """Stores the outcome of searching a specific source for an order."""

    __tablename__ = "search_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("search_orders.id"), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text)
    found_data_json: Mapped[Optional[str]] = mapped_column(Text) # Use Optional[str] for Text column
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    order: Mapped["SearchOrder"] = relationship(back_populates="results")


class PasswordResetToken(Base):
    """Stores password reset tokens for users."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship()