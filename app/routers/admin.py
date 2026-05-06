from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..auth import require_roles
from ..database import get_db
from ..models import Booking, CAProfile, User
from ..schemas import AdminStats, BookingPublic, CAProfilePublic, UserPublic, VerifyCARequest

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
def stats(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return {
        "users": db.query(User).filter(User.role == "user").count(),
        "ca_profiles": db.query(CAProfile).count(),
        "pending_ca_verifications": db.query(CAProfile).filter(CAProfile.verified.is_(False)).count(),
        "bookings": db.query(Booking).count(),
    }


@router.get("/users", response_model=list[UserPublic])
def users(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/cas", response_model=list[CAProfilePublic])
def ca_profiles(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return (
        db.query(CAProfile)
        .options(joinedload(CAProfile.user), joinedload(CAProfile.services))
        .order_by(CAProfile.verified.asc(), CAProfile.rating.desc())
        .all()
    )


@router.patch("/cas/{ca_id}/verify", response_model=CAProfilePublic)
def verify_ca(
    ca_id: int,
    payload: VerifyCARequest,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    profile = db.query(CAProfile).filter(CAProfile.id == ca_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="CA profile not found")

    profile.verified = payload.verified
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/bookings", response_model=list[BookingPublic])
def bookings(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return (
        db.query(Booking)
        .options(joinedload(Booking.user), joinedload(Booking.service), joinedload(Booking.ca_profile).joinedload(CAProfile.user))
        .order_by(Booking.appointment_date.desc())
        .all()
    )

