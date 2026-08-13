from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils import schemas
from app import models
from app.dependencies import get_db, get_current_user


router = APIRouter(tags=["Bookings"])


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post("/bookings")
def create_booking(
    booking: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Validation 1: Show exists
    # --------------------------------------------------------
    show = (
        db.query(models.Show)
        .filter(models.Show.id == booking.show_id)
        .first()
    )

    if show is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "SHOW_NOT_FOUND",
                "message": "Show not found",
            },
        )

    # --------------------------------------------------------
    # Validation 2: Movie exists
    # --------------------------------------------------------
    movie = (
        db.query(models.Movie)
        .filter(models.Movie.id == booking.movie_id)
        .first()
    )

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "MOVIE_NOT_FOUND",
                "message": "Movie not found",
            },
        )

    # --------------------------------------------------------
    # Validation 3: Screen exists
    # --------------------------------------------------------
    screen = (
        db.query(models.Screen)
        .filter(models.Screen.id == booking.screen_id)
        .first()
    )

    if screen is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "SCREEN_NOT_FOUND",
                "message": "Screen not found",
            },
        )

    # --------------------------------------------------------
    # Validation 4: Show belongs to selected movie
    # --------------------------------------------------------
    if show.movie_id != booking.movie_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "SHOW_MOVIE_MISMATCH",
                "message": "Selected show does not belong to this movie",
            },
        )

    # --------------------------------------------------------
    # Validation 5: Show belongs to selected screen
    # --------------------------------------------------------
    if show.screen_id != booking.screen_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "SHOW_SCREEN_MISMATCH",
                "message": "Selected show does not belong to this screen",
            },
        )

    # --------------------------------------------------------
    # Validation 6: Seats required
    # --------------------------------------------------------
    if not booking.seats or not booking.seats.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "SEATS_REQUIRED",
                "message": "At least one seat is required",
            },
        )

    # --------------------------------------------------------
    # Normalize seats
    # --------------------------------------------------------
    requested_seats = [
        seat.strip().upper()
        for seat in booking.seats.split(",")
        if seat.strip()
    ]

    if not requested_seats:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_SEATS",
                "message": "Invalid seat selection",
            },
        )

    # --------------------------------------------------------
    # Validation 7: Duplicate seats
    # --------------------------------------------------------
    if len(requested_seats) != len(set(requested_seats)):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "DUPLICATE_SEATS",
                "message": "Duplicate seats are not allowed",
            },
        )

    # --------------------------------------------------------
    # Validation 8: Check already booked seats
    # --------------------------------------------------------
    existing_bookings = (
        db.query(models.Booking)
        .filter(
            models.Booking.show_id == booking.show_id,
            models.Booking.status != "cancelled",
        )
        .all()
    )

    booked_seats = set()

    for existing_booking in existing_bookings:
        if existing_booking.seats:
            booked_seats.update(
                seat.strip().upper()
                for seat in existing_booking.seats.split(",")
                if seat.strip()
            )

    already_booked = [
        seat
        for seat in requested_seats
        if seat in booked_seats
    ]

    if already_booked:
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "SEATS_ALREADY_BOOKED",
                "message": "One or more selected seats are already booked",
                "seats": already_booked,
            },
        )

    # --------------------------------------------------------
    # Validation 9: Amount
    # --------------------------------------------------------
    if booking.total_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_AMOUNT",
                "message": "Total amount must be greater than zero",
            },
        )

    # --------------------------------------------------------
    # Create booking
    # --------------------------------------------------------
    db_booking = models.Booking(
        user_id=current_user.id,
        show_id=booking.show_id,
        movie_id=booking.movie_id,
        screen_id=booking.screen_id,
        customer_name=booking.customer_name or "Guest",
        seats=",".join(requested_seats),
        total_amount=booking.total_amount,
        status="pending",
        payment_intent_id=booking.payment_intent_id,
    )

    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    return db_booking


# ============================================================
# GET CURRENT USER BOOKINGS
# ============================================================

@router.get("/bookings")
def get_bookings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .all()
    )

    result = []

    for b in bookings:
        movie = (
            db.query(models.Movie)
            .filter(models.Movie.id == b.movie_id)
            .first()
        )

        result.append(
            {
                "id": b.id,
                "movie_name": movie.name if movie else "Movie",
                "image": movie.image if movie else "",
                "seats": b.seats,
                "total_amount": b.total_amount,
                "status": b.status,
            }
        )

    return result


# ============================================================
# GET BOOKED SEATS FOR SHOW
# ============================================================

@router.get("/bookings/seats/{show_id}")
def get_booked_seats(
    show_id: int,
    db: Session = Depends(get_db),
):
    # Validation: Show exists
    show = (
        db.query(models.Show)
        .filter(models.Show.id == show_id)
        .first()
    )

    if show is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "SHOW_NOT_FOUND",
                "message": "Show not found",
            },
        )

    bookings = (
        db.query(models.Booking)
        .filter(
            models.Booking.show_id == show_id,
            models.Booking.status != "cancelled",
        )
        .all()
    )

    booked = []

    for booking in bookings:
        if booking.seats:
            booked.extend(
                seat.strip().upper()
                for seat in booking.seats.split(",")
                if seat.strip()
            )

    return booked


# ============================================================
# GET SINGLE BOOKING
# ============================================================

@router.get("/bookings/{id}")
def get_booking(
    id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = get_booking_or_403(
        id,
        current_user,
        db,
    )

    show = (
        db.query(models.Show)
        .filter(models.Show.id == booking.show_id)
        .first()
    )

    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "show_id": booking.show_id,
        "movie_id": booking.movie_id,
        "screen_id": booking.screen_id,
        "customer_name": booking.customer_name,
        "seats": booking.seats,
        "total_amount": booking.total_amount,
        "status": booking.status,
        "payment_intent_id": booking.payment_intent_id,

        # Date & Time
        "show_date": str(show.show_date) if show else None,
        "show_time": str(show.show_time) if show else None,
    }


# ============================================================
# DELETE BOOKING
# ============================================================

@router.delete("/bookings/{id}")
def delete_booking(
    id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = get_booking_or_403(
        id,
        current_user,
        db,
    )

    db.delete(booking)
    db.commit()

    return {
        "message": "Deleted",
    }


# ============================================================
# MY BOOKINGS
# ============================================================
@router.get("/my-bookings")
def my_bookings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .all()
    )

    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "seats": b.seats,
            "total_amount": b.total_amount,
            "status": b.status,
            "movie_name": b.movie.name if b.movie else None,
            "image": b.movie.image if b.movie else None,
        })

    return result

# ============================================================
# UPDATE PAYMENT
# ============================================================

@router.put("/bookings/{booking_id}/payment")
def update_booking_payment(
    booking_id: int,
    data: schemas.PaymentUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = get_booking_or_403(
        booking_id,
        current_user,
        db,
    )

    booking.payment_intent_id = data.payment_intent_id

    db.commit()
    db.refresh(booking)

    return {
        "message": "Payment ID updated",
        "booking_id": booking.id,
        "payment_intent_id": booking.payment_intent_id,
    }


# ============================================================
# BOOKING AUTHORIZATION HELPER
# ============================================================

def get_booking_or_403(
    booking_id: int,
    current_user: models.User,
    db: Session,
):
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "BOOKING_NOT_FOUND",
                "message": "Booking not found",
            },
        )

    # Admin can access any booking
    if current_user.role == "admin":
        return booking

    # Normal user can access only own booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error_code": "BOOKING_NOT_AUTHORIZED",
                "message": "Not authorized to access this booking",
            },
        )

    return booking