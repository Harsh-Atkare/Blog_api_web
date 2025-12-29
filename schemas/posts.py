from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    content: str = Field(min_length=10)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    views: int
    likes: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True