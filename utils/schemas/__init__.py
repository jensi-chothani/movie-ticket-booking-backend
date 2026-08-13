"""
util/schemas package

Split into per-domain files (movie, screen, show, booking, user, payment, offer)
with NO logic/field changes from the original single schemas.py.
Everything is re-exported here so existing imports keep working unchanged:

    from utils import schemas
    schemas.MovieCreate
    schemas.BookingCreate
    ...
"""

from .movie import MovieCreate, MovieResponse, MovieUpdate, RatingCreate
from .screen import ScreenCreate, ScreenUpdate, ScreenResponse
from .show import ShowCreate
from .booking import BookingBase, BookingCreate, Booking
from .user import UserCreate, UserOut, UserLogin
from .payment import PaymentCreate, PaymentResponse, PaymentUpdate
from .offer import OfferBase, OfferCreate, OfferResponse

__all__ = [
    "MovieCreate", "MovieResponse", "MovieUpdate", "RatingCreate",
    "ScreenCreate", "ScreenUpdate", "ScreenResponse",
    "ShowCreate",
    "BookingBase", "BookingCreate", "Booking",
    "UserCreate", "UserOut", "UserLogin",
    "PaymentCreate", "PaymentResponse",
    "OfferBase", "OfferCreate", "OfferResponse",
]
