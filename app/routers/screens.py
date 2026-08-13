from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db, admin_required

router = APIRouter(tags=["Screens"])


@router.post("/screens")
def create_screen(
    screen: dict,
    admin: models.User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    if screen.get("name") and screen.get("cinema_id"):
        existing = db.query(models.Screen).filter(
            models.Screen.name == screen.get("name"),
            models.Screen.cinema_id == screen.get("cinema_id")
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Screen with this name already exists in this cinema")
    db_screen = models.Screen(**screen)
    db.add(db_screen)
    db.commit()
    db.refresh(db_screen)
    return db_screen


@router.get("/screens")
def get_screens(db: Session = Depends(get_db)):
    return db.query(models.Screen).all()


@router.put("/screens/{screen_id}")
def update_screen(
    screen_id: int,
    data: dict,
    admin: models.User = Depends(admin_required),  # FIX: was missing
    db: Session = Depends(get_db)
):
    screen = db.query(models.Screen).filter(models.Screen.id == screen_id).first()
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")
    for k, v in data.items():
        setattr(screen, k, v)
    db.commit()
    db.refresh(screen)
    return screen


@router.delete("/screens/{screen_id}")
def delete_screen(
    screen_id: int,
    admin: models.User = Depends(admin_required),  # FIX: was missing
    db: Session = Depends(get_db)
):
    screen = db.query(models.Screen).filter(models.Screen.id == screen_id).first()
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")

    # FIX: original code deleted the screen and returned BEFORE this cleanup ran
    # (dead code after `return`). Now cleanup happens first, in the right order.
    db.query(models.Booking).filter(models.Booking.screen_id == screen_id).delete()
    db.query(models.Show).filter(models.Show.screen_id == screen_id).delete()
    db.delete(screen)
    db.commit()

    return {"message": "Screen deleted successfully"}
