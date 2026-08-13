import random
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from utils import schemas
from app import models
from app.models import PaymentModel
from app.dependencies import get_db, get_current_user, admin_required, get_booking_or_403

router = APIRouter(tags=["Payments"])


@router.post("/payments", response_model=schemas.PaymentResponse)
def create_payment(
    payment: schemas.PaymentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = get_booking_or_403(payment.booking_id, current_user, db)

    txn = "TXN" + str(random.randint(100000, 999999))
    db_payment = PaymentModel(
        booking_id=payment.booking_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        transaction_id=txn,
        status="SUCCESS",
        created_at=datetime.utcnow()
    )
    db.add(db_payment)

    # NEW: mark booking as confirmed after successful payment
    booking.status = "confirmed"
    db.add(booking)

    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/payments")
def get_payments(admin: models.User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(PaymentModel).all()