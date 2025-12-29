from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
from database import get_db
from schemas.posts import PostCreate, PostUpdate, PostResponse
from dependencies import get_current_user, get_pagination, Pagination

router = APIRouter(prefix="/posts", tags=["Posts"])

def update_search_index(post_id: int):
    print(f"🔍 Updating search index for post {post_id}")

def notify_followers(author_id: int, post_id: int):
    print(f"🔔 Notifying followers of user {author_id} about post {post_id}")

@router.get("/")
def get_posts(
    pagination: Pagination = Depends(get_pagination),
    author_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of posts with filtering and pagination (authenticated users only)"""
    query = db.query(models.Post)
    
    if author_id:
        query = query.filter(models.Post.author_id == author_id)
    
    if is_published is not None:
        query = query.filter(models.Post.is_published == is_published)
    
    query = query.filter(models.Post.is_deleted == False)
    
    posts = query.offset(pagination.skip).limit(pagination.limit).all()
    
    return posts

@router.get("/{post_id}")
def get_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single post by ID (authenticated users only)"""
    post = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.views += 1
    db.commit()
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "author_username": post.author.username,
        "views": post.views,
        "likes": post.likes,
        "is_published": post.is_published,
        "created_at": post.created_at
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    db_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    background_tasks.add_task(update_search_index, db_post.id)
    background_tasks.add_task(notify_followers, current_user.id, db_post.id)
    
    return {"message": "Post created successfully", "post": db_post}

@router.put("/{post_id}")
def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update post (only author can update)"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own posts")
    
    if post_update.title is not None:
        post.title = post_update.title
    
    if post_update.content is not None:
        post.content = post_update.content
    
    db.commit()
    db.refresh(post)
    
    return {"message": "Post updated successfully", "post": post}

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete post (only author can delete)"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    post.is_deleted = True
    db.commit()
    
    return None

@router.post("/{post_id}/publish")
def publish_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post.is_published = True
    post.published_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Post published successfully"}