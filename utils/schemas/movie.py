

from pydantic import BaseModel, ConfigDict

# ================= MOVIE ================

# CREATE MOVIE
class MovieCreate(BaseModel):
    name: str
    category: str
    image: str
    description: str
    rating: float = 0


# RESPONSE MOVIE
class MovieResponse(BaseModel):
    id: int
    name: str
    category: str
    image: str
    description: str
    rating: float = 0

   
    model_config = ConfigDict(
        from_attributes=True
    )

class MovieUpdate(BaseModel):
    name: str
    image: str
    category: str
    description: str


class RatingCreate(BaseModel):
    movie_id: int
    stars: float
    review: str | None = None
