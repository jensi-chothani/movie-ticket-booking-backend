from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Movie, Booking
from app.dependencies import get_db

router = APIRouter(tags=["Trending"])

@router.get("/movies/trending")
def trending_movies(db: Session = Depends(get_db)):
    movies = (
        db.query(
            Movie,
            func.count(Booking.id).label("booking_count")
        )
        .outerjoin(
            Booking,
            Movie.id == Booking.movie_id
        )
        .group_by(Movie.id)
        .order_by(
            func.count(Booking.id).desc()
        )
        .limit(3)
        .all()
    )

    result = []

    for movie, count in movies:
        result.append({
            "id": movie.id,
            "name": movie.name,
            "image": movie.image,
            "category": movie.category,
            "rating": movie.rating,
            "booking_count": count
        })

    return result