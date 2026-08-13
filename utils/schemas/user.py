from typing import Optional
from pydantic import BaseModel, EmailStr


# ================= USER =================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str = "user"
    status: str = "active"


# RESPONSE USER

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    status: str

    class Config:
        from_attributes = True


# LOGIN

class UserLogin(BaseModel):
    email: EmailStr
    password: str