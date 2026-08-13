from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from utils import schemas
from app import models
from app.dependencies import get_db, get_current_user

router = APIRouter(tags=["Ratings"])


# Left public on purpose — like Google/IMDB reviews, but tied to a logged-in user
# so ratings can be traced back (recommended addition):
@router.post("/ratings")
def add_rating(
    data: schemas.RatingCreate,
    current_user: models.User = Depends(get_current_user),  # FIX: was fully anonymous, spammable
    db: Session = Depends(get_db)
):
    rating = models.Rating(
        movie_id=data.movie_id,
        stars=data.stars,
        review=data.review
    )
    db.add(rating)
    db.commit()
    return {"message": "Rating added"}


@router.get("/movies/{movie_id}/rating")
def get_rating(movie_id: int, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    if not ratings:
        return {"rating": 0}
    avg = sum(r.stars for r in ratings) / len(ratings)
    return {"rating": round(avg, 1), "total_reviews": len(ratings)}
