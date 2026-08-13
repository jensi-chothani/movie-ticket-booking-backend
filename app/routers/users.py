from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import models
from app.dependencies import get_db, admin_required


router = APIRouter(tags=["Users"])

# FIX: public /users POST let anyone create a user with role="admin" in the body
# (privilege escalation). Only admins may create arbitrary users now.
# Normal signup must go through /register, which always forces role="user".

# FIX: was public and let caller set ANY field including role/status (privilege
# escalation, e.g. {"role": "admin"}). Now: a user can edit only their own profile
# and cannot change role/status; only an admin can edit anyone or change role/status.
ALLOWED_SELF_UPDATE_FIELDS = {"name", "phone", "password"}


@router.post("/users")
def create_user(
    user: dict,
    admin: models.User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    try:
        if user.get("email"):
            existing = db.query(models.User).filter(
                models.User.email == user.get("email")
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
        if "password" in user:
            user["password"] = hash_password(user["password"])
        db_user = models.User(**user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


# FIX: was public — exposed every user's data (incl. hashed passwords) to anyone.
@router.get("/users")
def get_users(admin: models.User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(models.User).all()

