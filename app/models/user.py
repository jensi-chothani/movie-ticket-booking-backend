from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    phone = Column(String, nullable=True)

    role = Column(
        String,
        default="user"
    )
    # user / admin

    status = Column(
        String,
        default="active"
    )

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan"
    )