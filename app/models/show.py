from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)

    movie_id = Column(
        Integer,
        ForeignKey("movies.id"),
        nullable=False,
        index=True
    )

    screen_id = Column(
        Integer,
        ForeignKey("screens.id"),
        nullable=False,
        index=True
    )

    show_date = Column(Date, nullable=False)
    show_time = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)

    movie = relationship("Movie", back_populates="shows")
    screen = relationship("Screen", back_populates="shows")
    bookings = relationship(
        "Booking",
        back_populates="show",
        cascade="all, delete-orphan"
    )