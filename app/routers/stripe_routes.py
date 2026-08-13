import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app import models
from app.dependencies import (
    get_db,
    get_current_user,
    admin_required,
    get_booking_or_403,
)

router = APIRouter(tags=["Stripe"])

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid payload",
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        )

    event_type = event["type"]

    print("STRIPE WEBHOOK EVENT:", event_type)

    # =====================================================
    # CHECKOUT SESSION COMPLETED
    # =====================================================

    if event_type == "checkout.session.completed":

        session_data = event["data"]["object"]

        # StripeObject -> directly access metadata
        metadata = session_data["metadata"]

        booking_id = metadata["booking_id"] if metadata else None

        print("BOOKING ID FROM STRIPE:", booking_id)

        if not booking_id:
            return {"status": "ok"}

        booking = (
            db.query(models.Booking)
            .filter(
                models.Booking.id == int(booking_id)
            )
            .first()
        )

        if not booking:
            print(
                "BOOKING NOT FOUND:",
                booking_id,
            )
            return {"status": "ok"}

        payment_status = session_data["payment_status"]

        print(
            "STRIPE PAYMENT STATUS:",
            payment_status,
        )

        # StripeObject can be string OR object
        payment_intent = session_data["payment_intent"]

        if payment_intent:

            if isinstance(payment_intent, str):
                booking.payment_intent_id = payment_intent

            else:
                booking.payment_intent_id = payment_intent["id"]

        # ONLY successful payment -> confirmed
        if payment_status == "paid":

            booking.status = "confirmed"

            print(
                f"✅ BOOKING {booking.id} CONFIRMED"
            )

        db.commit()

        return {"status": "ok"}

    # =====================================================
    # PAYMENT INTENT SUCCEEDED
    # =====================================================

    elif event_type == "payment_intent.succeeded":

        payment_intent = event["data"]["object"]

        payment_intent_id = payment_intent["id"]

        print(
            "PAYMENT INTENT SUCCEEDED:",
            payment_intent_id,
        )

        # StripeObject -> directly access metadata
        metadata = payment_intent["metadata"]

        booking_id = (
            metadata["booking_id"]
            if metadata
            else None
        )

        print(
            "BOOKING ID FROM PAYMENT INTENT:",
            booking_id,
        )

        if not booking_id:
            return {"status": "ok"}

        booking = (
            db.query(models.Booking)
            .filter(
                models.Booking.id == int(booking_id)
            )
            .first()
        )

        if not booking:
            print(
                "BOOKING NOT FOUND:",
                booking_id,
            )
            return {"status": "ok"}

        booking.payment_intent_id = payment_intent_id

        # Payment succeeded -> confirmed
        booking.status = "confirmed"

        db.commit()

        print(
            f"✅ BOOKING {booking.id} "
            f"CONFIRMED FROM PAYMENT INTENT"
        )

        return {"status": "ok"}

    # =====================================================
    # OTHER STRIPE EVENTS
    # =====================================================

    return {"status": "ok"}


# =========================================================
# CREATE PAYMENT INTENT
# =========================================================

@router.post("/create-payment-intent")
def create_payment_intent(
    data: dict,
    current_user: models.User = Depends(
        get_current_user
    ),
):

    intent = stripe.PaymentIntent.create(
        amount=int(data["amount"] * 100),
        currency="inr",
        payment_method_types=["card"],
    )

    return {
        "client_secret": intent.client_secret,
        "payment_intent": intent.id,
    }


# =========================================================
# CREATE UNCAPTURED PAYMENT
# =========================================================

@router.post("/create-uncaptured-payment")
def create_uncaptured_payment(
    data: dict,
    current_user: models.User = Depends(
        get_current_user
    ),
):

    intent = stripe.PaymentIntent.create(
        amount=int(data["amount"] * 100),
        currency="inr",
        capture_method="manual",
        payment_method_types=["card"],
    )

    return {
        "payment_intent_id": intent.id,
        "client_secret": intent.client_secret,
        "status": intent.status,
    }


# =========================================================
# REFUND
# =========================================================

@router.post("/refund/{payment_intent_id}")
def create_refund(
    payment_intent_id: str,
    admin: models.User = Depends(admin_required),
):

    try:

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id
        )

        return {
            "message": "Refund successful",
            "refund_id": refund.id,
            "status": refund.status,
        }

    except stripe.error.StripeError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# =========================================================
# CREATE CHECKOUT SESSION
# =========================================================

@router.post("/create-checkout-session")
def create_checkout_session(
    data: dict,
    current_user: models.User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    booking = get_booking_or_403(
        data["booking_id"],
        current_user,
        db,
    )

    # IMPORTANT:
    # Payment પહેલાં booking ALWAYS pending
    booking.status = "pending"
    booking.total_amount = data["amount"]
  
    db.commit()
    db.refresh(booking)

    session = stripe.checkout.Session.create(

        customer_email=data["email"],

        # Checkout Session metadata
        metadata={
            "booking_id": str(booking.id)
        },

        # Payment Intent metadata
        payment_intent_data={
            "metadata": {
                "booking_id": str(booking.id)
            }
        },

        payment_method_types=["card"],

        line_items=[
            {
                "price_data": {
                    "currency": "inr",

                    "product_data": {
                        "name": data.get(
                            "name",
                            "Movie Ticket",
                        )
                    },

                    "unit_amount": int(
                        data["amount"] * 100
                    ),
                },

                "quantity": 1,
            }
        ],

        mode="payment",

        success_url=(
            "http://localhost:5173/"
            f"payment-success?bookingId={booking.id}"
        ),

        cancel_url=(
            "http://localhost:5173/"
            f"payment-failed?bookingId={booking.id}"
        ),
    )

    return {
        "url": session.url,
        "session_id": session.id,
        "booking_id": booking.id,
        "status": booking.status,
    }