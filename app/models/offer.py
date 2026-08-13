from sqlalchemy import Column, Integer, String, ForeignKey

from app.db import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)

    movie_id = Column(Integer, ForeignKey("movies.id"))

    title = Column(String, nullable=False)

    code = Column(
        String,
        nullable=False,
        unique=True
    )

    discount_value = Column(Integer, nullable=False)

    discount_type = Column(String, default="percent")

    status = Column(String, default="Active")