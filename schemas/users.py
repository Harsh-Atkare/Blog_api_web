from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str
    
    class Config:
        from_attributes = True