from datetime import datetime
from pydantic import BaseModel, Field


# ================= PAYMENT ===
class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    payment_intent_id: str = Field(
        min_length=1,
        max_length=255
    )