from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.db import db
from app.services.email_service import EmailService
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission
import os

user_routes = Blueprint('users', __name__, url_prefix='/users')
PASSWORD_MIN_LENGTH = 8

@user_routes.post("")
@tokenRequired
@checkPermission()
def createUser():
    user = request.get_json()

    if user.get('email') is None or user.get('password') is None:
        return jsonify({'message': 'Email and password are required'}), 400
    
    if len(user.get('password')) < PASSWORD_MIN_LENGTH:
        return jsonify({'message': 'Password must be at least 8 characters long'}), 400

    is_existed = User.query.filter_by(email=user.get('email')).first()
    if is_existed:
        return jsonify({'message': 'Email already registered'}), 409
    new_user = User(email=user.get('email'), rawPassword=user.get('password'))
    new_user.set_password(user.get('password'))

    db.session.add(new_user)
    db.session.commit()

    if user.get('permissionIds'):
    # Tạo các bản ghi trong bảng user_permissions
        for permission_id in user.get('permissionIds'):
            user_permission = UserPermission(
                userId=new_user.id,
                permissionId=permission_id
            )
            db.session.add(user_permission)
        
    db.session.commit()

    # send email smtp
    # emailService = EmailService()
    # subject = "Welcome to Hyna Platform - Your Account Details"
    # content = [
    #     f"""
    #     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    #         <h2 style="color: #333;">Welcome to Hyna Platform!</h2>
            
    #         <p>Your account has been successfully created. Here are your login credentials:</p>
            
    #         <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
    #             <p><strong>Email:</strong> {user.get('email')}</p>
    #             <p><strong>Password:</strong> {user.get('password')}</p>
    #         </div>

    #         <p>For security reasons, we recommend changing your password after your first login.</p>
            
    #         <p>Login here: <a href="{os.getenv('FRONTEND_URL')}/login">{os.getenv('FRONTEND_URL')}/login</a></p>

    #         <p style="color: #666; font-size: 12px; margin-top: 30px;">
    #             This is an automated message, please do not reply to this email.<br>
    #             If you need assistance, please contact our support team.
    #         </p>
    #     </div>
    #     """
    # ]
    # emailService.send_email(user.get('email'), subject, content)

    return jsonify({'message': 'User created successfully', 'status': 'success'}), 201

@user_routes.get("")
@tokenRequired
@checkPermission()
def getUsers():
    limit = int(request.args.get('limit', 10))
    page = int(request.args.get('page', 1))
    skip = (int(page) - 1) * int(limit)
    
    search = request.args.get('search', '')

    query = User.query

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
@tokenRequired
@checkPermission()
def getUser(userId):
    user = User.query.filter_by(id=userId).first()
    
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict())

@user_routes.route("/<int:userId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateUser(userId: int):
    user = User.query.filter_by(id=userId).first() 
    userData = request.get_json()

    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    if userData.get('password') is None:
        return jsonify({'message': 'Password are required'}), 400

    user.set_password(userData.get('password'))
    user.rawPassword = userData.get('password')

    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'status': 'success'})

@user_routes.route("/<int:userId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteUser(userId: int):
    user = User.query.filter_by(id=userId).first()
    
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully', 'status': 'success'})