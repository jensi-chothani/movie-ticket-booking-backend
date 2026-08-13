from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db

router = APIRouter(tags=["Cinemas"])


@router.get("/cinemas")
def get_cinemas(db: Session = Depends(get_db)):
    return db.query(models.Cinema).all()
