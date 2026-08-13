from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Screen(Base):
    __tablename__ = "screens"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))
    location = Column(String(100))
    total_seats = Column(Integer)
    screen_type = Column(String(50))
    status = Column(String(50))

    cinema_id = Column(Integer, ForeignKey("cinemas.id"))

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    cinema = relationship(
        "Cinema",
        back_populates="screens"
    )

    shows = relationship(
        "Show",
        back_populates="screen"
    )
    bookings = relationship(
        "Booking",
        back_populates="screen",
        cascade="all, delete-orphan"
    )