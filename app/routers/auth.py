from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import SECRET_KEY, ALGORITHM
from utils.schemas.user import UserCreate, UserLogin
from datetime import datetime, timedelta
from jose import jwt


from app.dependencies import get_db, get_current_user
from app import models

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta


router = APIRouter(
    tags=["Auth"]
)


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(
        password,
        hashed_password
    )


def create_token(data: dict):

    expire = datetime.utcnow() + timedelta(minutes=30)

    payload = data.copy()
    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone,
        role="user",
        status="active"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()


    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid login"
        )


    # password check (important)
    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )


    token = create_token(
        {
            "sub": str(db_user.id),
            "role": db_user.role,
            "email": db_user.email,
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "role": db_user.role
    }

    
@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
        "status": current_user.status
    }
    