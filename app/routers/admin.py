from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, admin_required
from app.models.user import User
from app.db import get_db
from app import models
from app.routers.auth import hash_password


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):

    # Only admin can update role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # update role
    user.role = role

    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated successfully",
        "user_id": user.id,
        "name": user.name,
        "role": user.role
    }