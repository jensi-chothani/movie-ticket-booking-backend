from pydantic import BaseModel, ConfigDict
from typing import Optional


class OfferBase(BaseModel):
    title: str
    code: str
    discount_value: float
    discount_type: str
    status: str


class OfferCreate(OfferBase):
    pass


class OfferResponse(OfferBase):
    id: int

    model_config = ConfigDict(from_attributes=True)