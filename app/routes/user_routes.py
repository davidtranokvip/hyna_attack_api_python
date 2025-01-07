from http.client import HTTPException
from flask import Blueprint, jsonify, request, abort
from app.models.user import User
from app.db import db
from app.services.email_service import EmailService
import os

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
    
    emailService = EmailService()
    subject = "Welcome to Hyna Platform - Your Account Details"
    content = [
        """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Welcome to Hyna Platform!</h2>
            
            <p>Your account has been successfully created. Here are your login credentials:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Email:</strong> {}</p>
                <p><strong>Password:</strong> {}</p>
            </div>

            <p>For security reasons, we recommend changing your password after your first login.</p>
            
            <p>Login here: <a href="{}/login">{}/login</a></p>

            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated message, please do not reply to this email.<br>
                If you need assistance, please contact our support team.
            </p>
        </div>
        """.format(user.get('email'), user.get('password'), os.getenv('FRONTEND_URL'), os.getenv('FRONTEND_URL'))
    ]
    emailService.send_email(user.get('email'), subject, content)


    return jsonify({'message': 'User created successfully'}), 201

@user_routes.get("")
def get_users():
    limit = int(request.args.get('limit', 10))
    page = int(request.args.get('page', 1))
    skip = (int(page) - 1) * int(limit)
    
    search = request.args.get('search', '')

    query = User.query

    query = query.filter(User.role == 'user')
    if search:
        query = query.filter(User.email.ilike(f'%{search}%'))

    users = query.limit(limit).offset(skip).all()
    total = query.count()
    
    return jsonify({
        "status": "success",
        "data": [user.to_dict() for user in users],
        "meta": {
            "total": total,
            "totalPages": -(-total // int(limit)),
            "currentPage": page,
            "pageSize": limit,
        }
    }), 200

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