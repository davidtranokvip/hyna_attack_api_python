from flask import Blueprint, jsonify, request
from app.models.user import User
from app.db import db

user_routes = Blueprint('users', __name__, url_prefix='/users')

@user_routes.post("/")
def create_user():
    user = request.get_json()

    is_existed = User.query.filter_by(email=user.get('email')).first()
    if is_existed:
        return jsonify({'message': 'Email already registered'}), 409
    
    new_user = User(email=user.get('email'), raw_password=user.get('password'))
    new_user.set_password(user.get('password'))

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@user_routes.get("/")
def get_users():
    limit = request.args.get('limit', 10) 
    skip = request.args.get('skip', 0)

    users = db.session.query(User).limit(limit).offset(skip).all()
    return jsonify([user.to_dict() for user in users])

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
