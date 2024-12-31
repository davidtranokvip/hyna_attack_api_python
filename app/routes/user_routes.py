from http.client import HTTPException
from flask import Blueprint, jsonify, request, abort
from app.models.user import User
from app.db import db

user_routes = Blueprint('users', __name__, url_prefix='/users')

@user_routes.post("")
def create_user():
    user = request.get_json()

    is_existed = User.query.filter_by(email=user.get('email')).first()
    if is_existed:
        return jsonify({'message': 'Email already registered'}), 409
    
    new_user = User(email=user.get('email'), rawPassword=user.get('password'))
    new_user.set_password(user.get('password'))

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@user_routes.get("")
def get_users():
    limit = request.args.get('limit', 10) 
    skip = request.args.get('skip', 0)
    search = request.args.get('search', '')

    query = User.query

    query = query.filter(User.role == 'user')
    if search:
        query = query.filter(User.email.ilike(f'%{search}%'))

    users = query.limit(limit).offset(skip).all()
    return jsonify([user.to_dict() for user in users])

@user_routes.route('/<int:userId>', methods=['GET'])
def get_user(userId):
    user = User.query.filter_by(id=userId).first()
    
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict())

@user_routes.route("/<int:userId>", methods=['PUT'])
def update_user(userId: int):
    user = User.query.filter_by(id=userId).first() 

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    userData = request.get_json()
    
    user.set_password(userData.get('password'))
    user.rawPassword = userData.get('password')

    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@user_routes.route("/<int:userId>", methods=['DELETE'])
def delete_user(userId: int):
    user = User.query.filter_by(id=userId).first()
    
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})