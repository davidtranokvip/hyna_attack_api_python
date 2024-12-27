from flask import Blueprint, jsonify, request
from app.models.user import UserModel
from app.db import db

user_routes = Blueprint('users', __name__, url_prefix='/users')

@user_routes.post("/")
def create_user():
    user = request.get_json()

    is_existed = UserModel.query.filter_by(email=user.get('email')).first()
    if is_existed:
        return jsonify({'message': 'Email already registered'}), 409
    
    new_user = UserModel(email=user.get('email'))
    new_user.set_password(user.get('password'))

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

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
