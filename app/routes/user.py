from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from app.models import User
from schemas.user import UserCreate, UserUpdate, User as UserSchema
from utils.auth import get_password_hash, verify_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    db_user = User(
        email=user.email,
        password=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# @router.get("/", response_model=List[UserSchema])
# def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
#     users = db.query(User).offset(skip).limit(limit).all()
#     return users

# @router.get("/{user_id}", response_model=UserSchema)
# def get_user(user_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @router.put("/{user_id}", response_model=UserSchema)
# def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
#     db_user = db.query(User).filter(User.id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     update_data = user.dict(exclude_unset=True)
#     if "password" in update_data:
#         update_data["password"] = get_password_hash(update_data["password"])
    
#     for key, value in update_data.items():
#         setattr(db_user, key, value)
    
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @router.delete("/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}
