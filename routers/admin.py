from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from dependencies import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]
)

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    total_users = db.query(models.User).count()
    total_posts = db.query(models.Post).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    published_posts = db.query(models.Post).filter(models.Post.is_published == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_posts": total_posts,
        "published_posts": published_posts
    }

@router.get("/users")
def admin_get_all_users(db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    users = db.query(models.User).all()
    return users

@router.patch("/users/{user_id}/toggle-active")
def admin_toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    """Activate/deactivate user account"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'}",
        "user": user
    }

@router.delete("/posts/{post_id}")
def admin_delete_post(post_id: int, db: Session = Depends(get_db)):
    """Admin can delete any post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted by admin"}