from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", index=True)
    location = Column(String(120), nullable=True)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ca_profile = relationship("CAProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class CAProfile(Base):
    __tablename__ = "ca_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    professional_title = Column(String(140), default="Chartered Accountant")
    location = Column(String(120), nullable=False)
    expertise = Column(String(255), default="ITR")
    experience_years = Column(Integer, default=0)
    rating = Column(Float, default=4.0)
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Float, default=999.0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="ca_profile")
    services = relationship("CAService", back_populates="ca_profile", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="ca_profile")


class CAService(Base):
    __tablename__ = "ca_services"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(Integer, ForeignKey("ca_profiles.id"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)

    ca_profile = relationship("CAProfile", back_populates="services")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ca_id = Column(Integer, ForeignKey("ca_profiles.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("ca_services.id"), nullable=True)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String(30), default="scheduled", index=True)
    meeting_mode = Column(String(40), default="video")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookings")
    ca_profile = relationship("CAProfile", back_populates="bookings")
    service = relationship("CAService")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(140), nullable=False)
    category = Column(String(80), default="General")
    amount = Column(Float, nullable=False)
    spent_on = Column(Date, default=date.today, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="expenses")

