from pydantic import BaseModel, ConfigDict


# ================= BOOKING =================
class BookingBase(BaseModel):
    show_id: int
    movie_id: int
    screen_id: int
    customer_name: str = "Guest"
    seats: str
    total_amount: float
    payment_intent_id: str | None = None


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int

    class Config:
        from_attributes = True
