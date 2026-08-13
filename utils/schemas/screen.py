from typing import Optional
from pydantic import BaseModel


# ================= SCREEN =================
class ScreenCreate(BaseModel):
    name: str
    location: str
    total_seats: int
    screen_type: str
    status: str
    description: Optional[str] = None


class ScreenUpdate(BaseModel):
    name: Optional[str] = None
    total_seats: Optional[int] = None
    screen_type: Optional[str] = None
    status: Optional[str] = None


class ScreenResponse(ScreenCreate):
    id: int

    class Config:
        from_attributes = True
