from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db, admin_required
from utils import schemas

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)
@router.get("")
def get_movies(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100"
        )

    offset = (page - 1) * limit

    movies = (
        db.query(models.Movie)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return movies


# CREATE MOVIE (ADMIN ONLY)
@router.post("")
def create_movie(
    movie: schemas.MovieCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
   
    new_movie = models.Movie(
    name=movie.name,
    category=movie.category,
    image=movie.image,
    description=movie.description,
    rating=movie.rating
)

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return new_movie