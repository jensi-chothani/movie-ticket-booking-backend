"""
app/models package

Split into per-domain files (movie, show, screen, booking, payment, offer, user, cinema)
with NO logic/field/relationship changes from the original single models.py.
Everything is re-exported here so existing imports keep working unchanged:

    from app import models
    models.Movie
    models.Booking
    ...

Import order matters only in that all classes must be imported somewhere before
SQLAlchemy configures mappers (e.g. Base.metadata.create_all / first query) since
relationship() references classes by string name — importing them all here
guarantees that.
"""

from .movie import Movie
from .show import Show
from .screen import Screen
from .booking import Booking
from .payment import PaymentModel
from .offer import Offer
from .user import User
from .cinema import Cinema

__all__ = [
    "Movie",
    "Show",
    "Screen",
    "Booking",
    "PaymentModel",
    "Offer",
    "User",
    "Cinema",
]
