from pydantic import BaseModel


# ================= SHOW =================
class ShowCreate(BaseModel):
    movie_id: int
    screen_id: int
    show_date: str   # "2026-07-02"
    show_time: str   # "09:00 AM"
    price: int
