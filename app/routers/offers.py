from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils import schemas
from app import models
from app.models import Offer
from app.dependencies import get_db, admin_required

router = APIRouter(tags=["Offers"])


@router.post("/offers")
def create_offer(
    offer: schemas.OfferCreate,
    admin: models.User = Depends(admin_required),  # FIX: was missing
    db: Session = Depends(get_db)
):
    existing = db.query(models.Offer).filter(
        models.Offer.code.ilike(offer.code.strip())
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Offer with this code already exists")
    db_offer = Offer(**offer.dict())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


@router.get("/offers")
def get_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).all()


@router.get("/offers/movie/{movie_id}")
def get_movie_offers(movie_id: int, db: Session = Depends(get_db)):
    return db.query(models.Offer).filter(models.Offer.movie_id == movie_id).all()


@router.delete("/offers/{id}")
def delete_offer(
    id: int,
    admin: models.User = Depends(admin_required),  # FIX: was missing
    db: Session = Depends(get_db)
):
    offer = db.query(models.Offer).filter(models.Offer.id == id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted"}


@router.get("/user-offers")
def get_user_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).filter(models.Offer.status == "Active").all()
