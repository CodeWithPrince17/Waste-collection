from __future__ import annotations


from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Date, Time, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# 1. AREA TABLE
class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    ward: Mapped[Optional[str]] = mapped_column(String(50))
    landmark: Mapped[Optional[str]] = mapped_column(String(150))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships (Python-side only)
    users: Mapped[List["User"]] = relationship(back_populates="area")
    collection_events: Mapped[List["CollectionEvent"]] = relationship(back_populates="area")
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="area")

# 2. USER TABLE
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="resident") # "resident" or "admin"
    area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("areas.id"))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    area: Mapped[Optional["Area"]] = relationship(back_populates="users")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    collection_reports: Mapped[List["CollectionReport"]] = relationship(back_populates="user")

# 3. COLLECTION EVENT TABLE (Historical Data)
class CollectionEvent(Base):
    __tablename__ = "collection_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
    collection_date: Mapped[date] = mapped_column(Date)
    expected_time: Mapped[Optional[time]] = mapped_column(Time)
    actual_time: Mapped[Optional[time]] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(20), default="completed")

    # Relationships
    area: Mapped["Area"] = relationship(back_populates="collection_events")
    reports: Mapped[List["CollectionReport"]] = relationship(back_populates="collection_event")

# 4. PREDICTION TABLE (Algorithm Output)
class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
    prediction_date: Mapped[date] = mapped_column(Date)
    predicted_time: Mapped[time] = mapped_column(Time)
    lower_bound: Mapped[time] = mapped_column(Time)
    upper_bound: Mapped[time] = mapped_column(Time)
    confidence: Mapped[str] = mapped_column(String(20)) # e.g., "High", "Low", "Insufficient Data"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    area: Mapped["Area"] = relationship(back_populates="predictions")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="prediction")

# 5. NOTIFICATION TABLE
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"))
    message: Mapped[str] = mapped_column(String(500))
    notification_type: Mapped[str] = mapped_column(String(50), default="in_app")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="sent")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notifications")
    prediction: Mapped["Prediction"] = relationship(back_populates="notifications")

# 6. COLLECTION REPORT TABLE (User Feedback)
class CollectionReport(Base):
    __tablename__ = "collection_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    collection_event_id: Mapped[int] = mapped_column(ForeignKey("collection_events.id"))
    status: Mapped[str] = mapped_column(String(20)) # "collected" or "missed"
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="collection_reports")
    collection_event: Mapped["CollectionEvent"] = relationship(back_populates="reports")

# Resolve forward references for SQLAlchemy
from sqlalchemy.orm import configure_mappers
configure_mappers()