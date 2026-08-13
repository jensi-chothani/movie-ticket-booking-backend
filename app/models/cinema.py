from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db import Base

class Cinema(Base):
    __tablename__ = "cinemas"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))

    city = Column(String(100))

    address = Column(String(255))

    latitude = Column(Float)
    longitude = Column(Float)

    screens = relationship(
        "Screen",
        back_populates="cinema"
    )
