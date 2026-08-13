from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils import schemas
from app import models
from app.dependencies import get_db, admin_required

router = APIRouter(tags=["Shows"])


@router.post("/shows")
def create_show(
    show: schemas.ShowCreate,
    admin: models.User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    data = show.model_dump()
    try:
        data["show_time"] = datetime.strptime(data["show_time"].strip(), "%I:%M %p").time()
    except Exception:
        raise HTTPException(status_code=400, detail="Time format: 09:00 AM")
    try:
        data["show_date"] = datetime.strptime(data["show_date"], "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Date format: YYYY-MM-DD")

    existing = db.query(models.Show).filter(
        models.Show.movie_id == data["movie_id"],
        models.Show.screen_id == data["screen_id"],
        models.Show.show_date == data["show_date"],
        models.Show.show_time == data["show_time"]
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This show already exists for the selected screen, date and time")

    db_show = models.Show(**data)
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    return db_show


@router.get("/shows")
def get_shows(db: Session = Depends(get_db)):
    shows = db.query(models.Show).all()
    return [{
        "id": s.id, "movie_id": s.movie_id, "screen_id": s.screen_id,
        "show_date": str(s.show_date), "show_time": s.show_time if s.show_time else None,
        "price": s.price
    } for s in shows]


@router.get("/shows/movie/{movie_id}")
def get_shows_by_movie(movie_id: int, db: Session = Depends(get_db)):
    shows = db.query(models.Show).filter(models.Show.movie_id == movie_id).all()
    return [{
        "id": s.id, "movie_id": s.movie_id, "screen_id": s.screen_id,
        "show_date": str(s.show_date), "show_time": str(s.show_time), "price": s.price
    } for s in shows]


@router.get("/shows/cinema/{cinema_id}/{movie_id}")
def get_cinema_shows(cinema_id: int, movie_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Show)
        .join(models.Screen)
        .filter(models.Screen.cinema_id == cinema_id, models.Show.movie_id == movie_id)
        .all()
    )