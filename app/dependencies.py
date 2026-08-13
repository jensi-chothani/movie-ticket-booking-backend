from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config import SECRET_KEY, ALGORITHM
from app.db import SessionLocal
from app.models.user import User
from app.models.booking import Booking

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# ==========================
# Database
# ==========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# Current User
# ==========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ==========================
# Admin Required
# ==========================

from fastapi import Depends, HTTPException, status   


def admin_required(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
def get_booking_or_403(
    booking_id: int,
    current_user: User,
    db: Session
):
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Admin can access any booking
    if current_user.role == "admin":
        return booking

    # Normal user can access only their own booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this booking"
        )

    return booking