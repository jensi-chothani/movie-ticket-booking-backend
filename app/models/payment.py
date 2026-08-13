from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime

from app.db import Base


# ================= PAYMENTS =================

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(
        String(50),
        nullable=False
    )

    transaction_id = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(20),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )