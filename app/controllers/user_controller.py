from app.models.user_permission import UserPermission
from app.services.response import Response
from app.models.user_log import UserLog
from flask import request
from app.models.user import User
from sqlalchemy import func
from app.db import db
import re

PASSWORD_MIN_LENGTH = 8

class UserController:
    def getAll(self):
        try:

            query = db.session.query(User)

            users = query.order_by(User.updatedAt.desc()).all()
            users = User.query.filter(User.isAdmin != True)
                
            result = [user.to_dict() for user in users]

            return Response.success(data=result, message='Get Users Success')
           
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def create(self):
        try:
            user = request.get_json()

            if not user.get('email') and not user.get('password') and not user.get('nameAccount'):
                return Response.error({
                    'email': 'Email is required',
                    'password': 'Password is required',
                    'nameAccount': 'Name is required',
                }, code=400)
            
            elif not user.get('email'):
                return Response.error({
                    'email': 'Email is required'
                }, code=400)
            
            elif not user.get('password'):
                return Response.error({
                    'password': 'Password is required'
                }, code=400)
            
            elif not user.get('nameAccount'):
                return Response.error({
                        'nameAccount': 'Name is required'
                }, code=400)
            
            if len(user.get('password')) < PASSWORD_MIN_LENGTH:
                return Response.error({
                    'password': 'Password must be at least 8 characters long'
                }, code=400)
                    
            # Validate email format
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, user['email']):
                return Response.error({
                    'email': 'Invalid email format'
                }, code=400)
            
            if User.query.filter_by(email=user.get('email')).first():
                return Response.error({
                     'email': 'Email already registered'
                }, code=409)
            
            if User.query.filter(func.binary(User.nameAccount) == user.get('nameAccount')).first():
                return Response.error({
                    'nameAccount': 'Account already registered'
                }, code=409)
            
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
            return Response.success(data=[], message="User created successfully")
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
    
    def update(self, userId):
        try:
            user = User.query.filter_by(id=userId).first() 
            userData = request.get_json()
            if not user:
                return Response.error('User not found', code=404)
            
            if not userData.get('email') and not userData.get('password') and not userData.get('nameAccount'):
                return Response.error({
                    'email': 'Email is required',
                    'password': 'Password is required',
                    'nameAccount': 'Name is required',
                }, code=400)
            
            elif not userData.get('email'):
                return Response.error({
                    'email': 'Email is required'
                }, code=400)
            
            elif not userData.get('password'):
                return Response.error({
                    'password': 'Password is required'
                }, code=400)
            
            elif not userData.get('nameAccount'):
                return Response.error({
                    'nameAccount': 'Name is required'
                }, code=400)

            # Validate email format
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, userData['email']):
                return Response.error({
                    'email': 'Invalid email format'
                }, code=400)
            
            existing_email = User.query.filter(
                User.email == userData['email'],
                User.id != userId  # Add this condition
            ).first()
            if existing_email:
                return Response.error({
                     'email': 'Email already registered'
                }, code=409)
            
            existing_account = User.query.filter(
                User.nameAccount == userData['nameAccount'],
                User.id != userId  # Add this condition
            ).first()
            if existing_account:
                return Response.error({
                    'nameAccount': 'Account already registered'
                }, code=409)

            if len(userData['password']) < PASSWORD_MIN_LENGTH:
                return Response.error({
                    'password': 'Password must be at least 8 characters long'
                }, code=400)

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
            return Response.success(data=[], message="User updated successfully")
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def delete(self, userId):
        try:
            user = User.query.filter_by(id=userId).first()
            
            if not user:
                return Response.error('User not found', code=404)
            
            db.session.delete(user)
            db.session.commit()
            return Response.success(data=[], message="User Deleted Success")
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def userLog():
        try:
            query = db.session.query(UserLog)
            users_log = query.order_by(UserLog.time_active.desc()).all()
                    
            result = [user_log.to_dict() for user_log in users_log]
            return Response.success(data=result, message="Get User Log Success")
                
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)