from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import Booking, CAProfile, CAService, User
from ..schemas import BookingCreate, BookingPublic

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingPublic, status_code=201)
def create_booking(payload: BookingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only user accounts can book CA appointments")

    ca_profile = db.query(CAProfile).filter(CAProfile.id == payload.ca_id).first()
    if not ca_profile:
        raise HTTPException(status_code=404, detail="CA profile not found")
    if not ca_profile.verified:
        raise HTTPException(status_code=400, detail="This CA profile is not verified yet")

    if payload.service_id:
        service = db.query(CAService).filter(CAService.id == payload.service_id, CAService.ca_id == ca_profile.id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Selected service was not found for this CA")

    booking = Booking(
        user_id=current_user.id,
        ca_id=payload.ca_id,
        service_id=payload.service_id,
        appointment_date=payload.appointment_date,
        meeting_mode=payload.meeting_mode,
        notes=payload.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/my", response_model=list[BookingPublic])
def my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.service),
        joinedload(Booking.ca_profile).joinedload(CAProfile.user),
        joinedload(Booking.ca_profile).joinedload(CAProfile.services),
    )
    if current_user.role == "user":
        query = query.filter(Booking.user_id == current_user.id)
    elif current_user.role == "ca":
        profile = db.query(CAProfile).filter(CAProfile.user_id == current_user.id).first()
        query = query.filter(Booking.ca_id == profile.id) if profile else query.filter(False)
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unsupported account role")

    return query.order_by(Booking.appointment_date.desc()).all()

