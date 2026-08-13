from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


# ================= BOOKING =================

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    show_id = Column(
        Integer,
        ForeignKey("shows.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    screen_id = Column(
        Integer,
        ForeignKey("screens.id"),
        nullable=True,
        index=True
    )

    customer_name = Column(
        String(100),
        nullable=False
    )

    seats = Column(
        String(200),
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    status = Column(
    String(20),
    default="pending",
    nullable=False
)

    # Stripe refund
    payment_intent_id = Column(
        String(100),
        nullable=True
    )

    # ================= RELATIONSHIPS =================

    user = relationship(
        "User",
        back_populates="bookings"
    )

    show = relationship(
        "Show",
        back_populates="bookings"
    )

    movie = relationship(
        "Movie",
        back_populates="bookings"
    )

    screen = relationship(
        "Screen",
        back_populates="bookings"
    )