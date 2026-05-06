from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["user", "ca"] = "user"
    location: str | None = None
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    location: str | None = None
    phone: str | None = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class CAServiceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str | None = None
    price: float = Field(ge=0)


class CAServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ca_id: int
    title: str
    description: str | None = None
    price: float


class CAProfileCreate(BaseModel):
    professional_title: str = "Chartered Accountant"
    location: str = Field(min_length=2, max_length=120)
    expertise: list[str] = Field(default_factory=lambda: ["ITR"])
    experience_years: int = Field(default=0, ge=0, le=60)
    bio: str | None = None
    consultation_fee: float = Field(default=999, ge=0)


class CAProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    professional_title: str
    location: str
    expertise: str
    experience_years: int
    rating: float
    bio: str | None = None
    consultation_fee: float
    verified: bool
    created_at: datetime
    user: UserPublic | None = None
    services: list[CAServicePublic] = []


class BookingCreate(BaseModel):
    ca_id: int
    service_id: int | None = None
    appointment_date: datetime
    meeting_mode: Literal["video", "phone", "office"] = "video"
    notes: str | None = None


class BookingStatusUpdate(BaseModel):
    status: Literal["scheduled", "confirmed", "completed", "cancelled"]


class BookingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    ca_id: int
    service_id: int | None = None
    appointment_date: datetime
    status: str
    meeting_mode: str
    notes: str | None = None
    created_at: datetime
    user: UserPublic | None = None
    ca_profile: CAProfilePublic | None = None
    service: CAServicePublic | None = None


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=140)
    category: str = "General"
    amount: float = Field(gt=0)
    spent_on: date | None = None
    notes: str | None = None


class ExpensePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    category: str
    amount: float
    spent_on: date
    notes: str | None = None
    created_at: datetime


class DashboardSummary(BaseModel):
    total_expenses: float
    month_expenses: float
    total_bookings: int
    upcoming_bookings: int
    recent_expenses: list[ExpensePublic]
    upcoming_appointments: list[BookingPublic]


class TaxCalculatorRequest(BaseModel):
    annual_income: float = Field(gt=0)
    deductions_80c: float = Field(default=0, ge=0)
    medical_80d: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)
    other_deductions: float = Field(default=0, ge=0)


class TaxCalculatorResponse(BaseModel):
    taxable_old_regime: float
    taxable_new_regime: float
    old_regime_tax: float
    new_regime_tax: float
    recommended_regime: str
    savings_difference: float
    note: str


class TaxSavingSuggestionRequest(BaseModel):
    annual_income: float = Field(gt=0)
    invested_80c: float = Field(default=0, ge=0)
    medical_80d: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)


class TaxSavingSuggestion(BaseModel):
    title: str
    message: str
    potential_deduction: float


class VerifyCARequest(BaseModel):
    verified: bool = True


class AdminStats(BaseModel):
    users: int
    ca_profiles: int
    pending_ca_verifications: int
    bookings: int

