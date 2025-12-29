from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from database import get_db
from schemas.auth import UserResponse
from schemas.users import UserUpdate
from dependencies import get_current_user, get_pagination, Pagination

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(pagination: Pagination = Depends(get_pagination), db: Session = Depends(get_db)):
    """Get list of users with pagination"""
    users = db.query(models.User).offset(pagination.skip).limit(pagination.limit).all()
    return users

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Get your own profile"""
    return current_user

@router.put("/me")
def update_my_profile(
    user_update: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update your own profile"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        existing = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully", "user": current_user}

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user