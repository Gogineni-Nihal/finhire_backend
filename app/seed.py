from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import Booking, CAProfile, CAService, Expense, User


def seed_demo_data(db: Session) -> None:
    if db.query(User).first():
        return

    admin = User(
        name="FinHire Admin",
        email="admin@finhire.demo",
        password_hash=get_password_hash("admin123"),
        role="admin",
        location="Mumbai",
    )
    user = User(
        name="Aarav Sharma",
        email="user@finhire.demo",
        password_hash=get_password_hash("password123"),
        role="user",
        location="Delhi",
        phone="+91 98765 43210",
    )
    ca_user = User(
        name="Priya Mehta",
        email="ca@finhire.demo",
        password_hash=get_password_hash("password123"),
        role="ca",
        location="Mumbai",
        phone="+91 99887 77665",
    )
    ca_user_two = User(
        name="Rohan Iyer",
        email="rohan.ca@finhire.demo",
        password_hash=get_password_hash("password123"),
        role="ca",
        location="Bengaluru",
        phone="+91 90000 11122",
    )
    db.add_all([admin, user, ca_user, ca_user_two])
    db.flush()

    ca_one = CAProfile(
        user_id=ca_user.id,
        professional_title="GST and ITR Specialist",
        location="Mumbai",
        expertise="GST, ITR, Business",
        experience_years=8,
        rating=4.8,
        bio="Helps salaried professionals, freelancers, and MSMEs file returns and manage GST compliance.",
        consultation_fee=1499,
        verified=True,
    )
    ca_two = CAProfile(
        user_id=ca_user_two.id,
        professional_title="Business Finance Consultant",
        location="Bengaluru",
        expertise="Business, Audit, ITR",
        experience_years=11,
        rating=4.6,
        bio="Works with founders on bookkeeping, business taxation, audit readiness, and compliance planning.",
        consultation_fee=1999,
        verified=True,
    )
    db.add_all([ca_one, ca_two])
    db.flush()

    services = [
        CAService(ca_id=ca_one.id, title="ITR Filing", description="Salary, freelance, and capital gains return filing.", price=999),
        CAService(ca_id=ca_one.id, title="GST Monthly Filing", description="GSTR-1 and GSTR-3B support for small businesses.", price=2499),
        CAService(ca_id=ca_two.id, title="Startup Finance Review", description="One-hour review of books, compliance, and tax exposure.", price=2999),
        CAService(ca_id=ca_two.id, title="Business ITR", description="ITR filing for proprietors and small businesses.", price=3999),
    ]
    expenses = [
        Expense(user_id=user.id, title="Accounting software", category="Business", amount=1800, spent_on=date.today() - timedelta(days=2)),
        Expense(user_id=user.id, title="Office rent", category="Operations", amount=22000, spent_on=date.today() - timedelta(days=8)),
        Expense(user_id=user.id, title="Internet bill", category="Utilities", amount=999, spent_on=date.today() - timedelta(days=15)),
    ]
    booking = Booking(
        user_id=user.id,
        ca_id=ca_one.id,
        service_id=1,
        appointment_date=datetime.utcnow() + timedelta(days=2),
        status="confirmed",
        meeting_mode="video",
        notes="Need help comparing old and new tax regime.",
    )
    db.add_all(services + expenses + [booking])
    db.commit()

