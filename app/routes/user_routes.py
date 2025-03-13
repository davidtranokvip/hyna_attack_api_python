from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.user_log import UserLog
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.db import db
from app.services.email_service import EmailService
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission
import re
from sqlalchemy import func

user_routes = Blueprint('users', __name__, url_prefix='/users')
PASSWORD_MIN_LENGTH = 8

@user_routes.post("")
@tokenRequired
@checkPermission()
def createUser():
    try:
        user = request.get_json()

        if not user.get('email') and not user.get('password') and not user.get('nameAccount'):
             return jsonify({
                'message': {
                    'email': 'Email is required',
                    'password': 'Password is required',
                    'nameAccount': 'Name is required',
                }, 'status': 'error'
            }), 400
        elif not user.get('email'):
            return jsonify({
                'message': {
                    'email': 'Email is required'
                }, 'status': 'error'
            }), 400
        elif not user.get('password'):
            return jsonify({
                'message': {
                    'password': 'Password is required'
                }, 'status': 'error'
            }), 400
        elif not user.get('nameAccount'):
            return jsonify({
                'message': {
                    'nameAccount': 'Name is required'
                }, 'status': 'error'
            }), 400
        
        if len(user.get('password')) < PASSWORD_MIN_LENGTH:
            return jsonify({
                'message': {
                    'password': 'Password must be at least 8 characters long'
                }, 'status': 'error'
            }), 400
                
        # Validate email format
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, user['email']):
            return jsonify({
                'message': {
                    'email': 'Invalid email format'
                }, 'status': 'error'
            }), 400
        
        if User.query.filter_by(email=user.get('email')).first():
            return jsonify({
                'message': {
                    'email': 'Email already registered'
                }, 'status': 'error'
            }), 409
    
        if User.query.filter(func.binary(User.nameAccount) == user.get('nameAccount')).first():
            return jsonify({
                    'message': {
                        'nameAccount': 'Account already registered'
                    }, 'status': 'error'
                }), 409
        entry_time = None if user.get('entryTime') == 'Invalid Date' else user.get('entryTime')
        exit_time = None if user.get('exitTime') == 'Invalid Date' else user.get('exitTime')

        new_user = User(
            email=user.get('email'), 
            rawPassword=user.get('password'), 
            team_id=user.get('team_id'), 
            nameAccount=user.get('nameAccount'),
            server_id=user.get('server_id'),
            thread=user.get('thread'),
            entryTime=entry_time,
            exitTime=exit_time
        )
        new_user.set_password(user.get('password'))
        
        db.session.add(new_user)
        db.session.commit()

        if user.get('permissions'):
            for permission_obj in user['permissions']:
                permission_id = permission_obj.get('id')
                if permission_id:
                    user_permission = UserPermission(
                        userId=new_user.id,
                        permissionId=permission_id
                    )
                    db.session.add(user_permission)
            
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'status': 'success'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
@user_routes.get("")
@tokenRequired
@checkPermission()
def getUsers():
    try:
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (int(page) - 1) * int(limit)
        search = request.args.get('search', '')

        query = User.query.filter(User.isAdmin != True)

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
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
@user_routes.get("/log")
@tokenRequired
@checkPermission()
def getUserLog():
    try:
        query = db.session.query(UserLog)
        users_log = query.order_by(UserLog.time_active.desc()).all()
                
        result = {
            'data': [user_log.to_dict() for user_log in users_log],
            'status': 'success'
        }
            
        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@user_routes.route('/<int:userId>', methods=['GET'])
@tokenRequired
@checkPermission()
def getUser(userId):
    try:
        user = User.query.filter_by(id=userId).first()
        
        if user is None:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
@user_routes.route("/<int:userId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateUser(userId: int):
    try:
        user = User.query.filter_by(id=userId).first() 
        userData = request.get_json()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not userData.get('email') and not userData.get('password') and not userData.get('nameAccount'):
             return jsonify({
                'message': {
                    'email': 'Email is required',
                    'password': 'Password is required',
                    'nameAccount': 'Name is required'
                }, 'status': 'error'
            }), 400
        
        elif not userData.get('email'):
            return jsonify({
                'message': {
                    'email': 'Email is required'
                }, 'status': 'error'
            }), 400
        
        elif not userData.get('password'):
            return jsonify({
                'message': {
                    'password': 'Password is required'
                }, 'status': 'error'
            }), 400
        elif not userData.get('nameAccount'):
            return jsonify({
                'message': {
                    'nameAccount': 'Name is required'
                }, 'status': 'error'
            }), 400

        # Validate email format
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, userData['email']):
            return jsonify({
                'message': {
                    'email': 'Invalid email format'
                },
                'status': 'error'
            }), 400
        
        existing_email = User.query.filter(
            User.email == userData['email'],
            User.id != userId  # Add this condition
        ).first()
        if existing_email:
            return jsonify({
                'message': {
                    'email': 'Email already registered'
                },
                'status': 'error'
            }), 409
        existing_account = User.query.filter(
            User.nameAccount == userData['nameAccount'],
            User.id != userId  # Add this condition
        ).first()
        if existing_account:
            return jsonify({
                'message': {
                    'nameAccount': 'Account already registered'
                },
                'status': 'error'
            }), 409

        if len(userData['password']) < PASSWORD_MIN_LENGTH:
            return jsonify({
                'message': {
                    'password': 'Password must be at least 8 characters long'
                }, 'status': 'error'
            }), 400

        user.email = userData.get('email')
        user.set_password(userData.get('password'))
        user.rawPassword = userData.get('password')
        user.nameAccount = userData.get('nameAccount')
        user.team_id = userData.get('team_id')
        user.server_id = userData.get('server_id')
        user.thread = userData.get('thread')
        if userData.get('entryTime') == 'Invalid Date':
            user.entryTime = None
        else:
            user.entryTime = userData.get('entryTime')

        if userData.get('exitTime') == 'Invalid Date':
            user.exitTime = None
        else:
            user.exitTime = userData.get('exitTime')

        db.session.add(user)
        UserPermission.query.filter_by(userId=userId).delete()
        db.session.commit()
        if userData.get('permissions'):
            for permission_obj in userData.get('permissions'):  
                permission_id = permission_obj.get('id')
                if permission_id:
                    user_permission = UserPermission(
                        userId=userId,
                        permissionId=permission_id
                    )
                    db.session.add(user_permission)
            db.session.commit()
        return jsonify({'message': 'User updated successfully', 'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
@user_routes.route("/<int:userId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteUser(userId: int):
    try:
        user = User.query.filter_by(id=userId).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully', 'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400