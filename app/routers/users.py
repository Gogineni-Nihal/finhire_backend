from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import Booking, CAProfile, Expense, User
from ..schemas import DashboardSummary, UserPublic

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
def my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    month_start = date(today.year, today.month, 1)

    total_expenses = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == current_user.id)
        .scalar()
    )
    month_expenses = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == current_user.id, Expense.spent_on >= month_start)
        .scalar()
    )
    booking_query = db.query(Booking).filter(Booking.user_id == current_user.id)
    upcoming_query = booking_query.filter(Booking.appointment_date >= datetime.utcnow())

    recent_expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .order_by(Expense.spent_on.desc(), Expense.id.desc())
        .limit(5)
        .all()
    )
    upcoming_appointments = (
        upcoming_query.options(
            joinedload(Booking.ca_profile).joinedload(CAProfile.user),
            joinedload(Booking.service),
        )
        .order_by(Booking.appointment_date.asc())
        .limit(5)
        .all()
    )

    return {
        "total_expenses": float(total_expenses or 0),
        "month_expenses": float(month_expenses or 0),
        "total_bookings": booking_query.count(),
        "upcoming_bookings": upcoming_query.count(),
        "recent_expenses": recent_expenses,
        "upcoming_appointments": upcoming_appointments,
    }
