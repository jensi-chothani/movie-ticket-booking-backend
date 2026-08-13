from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship

from app.db import Base


# ================= MOVIE =================
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    category = Column(String(100))
    image = Column(String(255))
    description = Column(Text)

    rating = Column(Float, default=0)

    shows = relationship(
        "Show",
        back_populates="movie"
    )

    bookings = relationship(
        "Booking",
        back_populates="movie",
        cascade="all, delete"
    )
