from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for creating a new user (Registration)
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Pydantic will automatically check if this is a valid email format
    password: str
    area_id: Optional[int] = None

# Schema for logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for returning user data (Notice: NO password hash!)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    area_id: Optional[int]

    class Config:
        from_attributes = True # Tells Pydantic to read data from SQLAlchemy models