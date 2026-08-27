from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    phone = Column(String(20), nullable=True)

    role = Column(
        String(20),
        default="user"
    )
    # user / admin

    status = Column(
        String(20),
        default="active"
    )

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan"
    )
