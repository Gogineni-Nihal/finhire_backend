from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user, require_roles
from ..database import get_db
from ..models import Booking, CAProfile, CAService, User
from ..schemas import BookingPublic, BookingStatusUpdate, CAProfileCreate, CAProfilePublic, CAServiceCreate, CAServicePublic

router = APIRouter(prefix="/cas", tags=["Chartered Accountants"])


@router.get("", response_model=list[CAProfilePublic])
def search_cas(
    location: str | None = None,
    expertise: str | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5),
    verified: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CAProfile).options(joinedload(CAProfile.user), joinedload(CAProfile.services))
    if location:
        query = query.filter(CAProfile.location.ilike(f"%{location}%"))
    if expertise:
        query = query.filter(CAProfile.expertise.ilike(f"%{expertise}%"))
    if min_rating is not None:
        query = query.filter(CAProfile.rating >= min_rating)
    if verified is not None:
        query = query.filter(CAProfile.verified == verified)
    return query.order_by(CAProfile.verified.desc(), CAProfile.rating.desc()).all()


@router.get("/me/profile", response_model=CAProfilePublic)
def my_ca_profile(
    current_user: User = Depends(require_roles("ca")),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(CAProfile)
        .options(joinedload(CAProfile.user), joinedload(CAProfile.services))
        .filter(CAProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="CA profile not found")
    return profile


@router.put("/me/profile", response_model=CAProfilePublic)
def upsert_my_ca_profile(
    payload: CAProfileCreate,
    current_user: User = Depends(require_roles("ca")),
    db: Session = Depends(get_db),
):
    profile = db.query(CAProfile).filter(CAProfile.user_id == current_user.id).first()
    if not profile:
        profile = CAProfile(user_id=current_user.id, location=payload.location)
        db.add(profile)

    profile.professional_title = payload.professional_title
    profile.location = payload.location
    profile.expertise = ", ".join(payload.expertise)
    profile.experience_years = payload.experience_years
    profile.bio = payload.bio
    profile.consultation_fee = payload.consultation_fee
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/me/services", response_model=CAServicePublic, status_code=201)
def add_service(
    payload: CAServiceCreate,
    current_user: User = Depends(require_roles("ca")),
    db: Session = Depends(get_db),
):
    profile = db.query(CAProfile).filter(CAProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Create your CA profile before adding services")

    service = CAService(ca_id=profile.id, title=payload.title, description=payload.description, price=payload.price)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/me/bookings", response_model=list[BookingPublic])
def my_ca_bookings(
    current_user: User = Depends(require_roles("ca")),
    db: Session = Depends(get_db),
):
    profile = db.query(CAProfile).filter(CAProfile.user_id == current_user.id).first()
    if not profile:
        return []
    return (
        db.query(Booking)
        .options(joinedload(Booking.user), joinedload(Booking.service), joinedload(Booking.ca_profile).joinedload(CAProfile.user))
        .filter(Booking.ca_id == profile.id)
        .order_by(Booking.appointment_date.asc())
        .all()
    )


@router.patch("/me/bookings/{booking_id}", response_model=BookingPublic)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    current_user: User = Depends(require_roles("ca")),
    db: Session = Depends(get_db),
):
    profile = db.query(CAProfile).filter(CAProfile.user_id == current_user.id).first()
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.ca_id == profile.id).first() if profile else None
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/{ca_id}", response_model=CAProfilePublic)
def ca_details(ca_id: int, db: Session = Depends(get_db)):
    profile = (
        db.query(CAProfile)
        .options(joinedload(CAProfile.user), joinedload(CAProfile.services))
        .filter(CAProfile.id == ca_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="CA profile not found")
    return profile

