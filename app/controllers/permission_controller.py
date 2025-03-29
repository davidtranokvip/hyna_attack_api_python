from app.models.user_permission import UserPermission
from ..models.permission import Permission
from app.services.response import Response
from sqlalchemy import or_, exists
from app.models.user import User
from datetime import datetime
from flask import request
from app.db import db

class PermissionController:
    def __init__(self):
        self.permissions = []

    def createPermission(self):
        try:
            permission = request.get_json()
            
            if not permission.get('name') and not permission.get('module') and not permission.get('route'):
                return Response.error({
                    'name': 'Name is required',
                    'route': 'Route is required',
                    'module': 'Module is required'
                }, code=400)
            
            if not permission.get('name'):
                return Response.error({
                    'name': 'Name is required'
                }, code=400)
            
            elif not permission.get('module'):
                return Response.error({
                    'module': 'Module is required'
                }, code=400)
            
            elif not permission.get('route'):
                return Response.error({
                    'route': 'Route is required'
                }, code=400)
            
            existing_permission = Permission.query.filter_by(
                route=permission['route'],
            ).first()

            if existing_permission:
                return Response.error({
                    'route': 'Route already exists'
                }, code=400)

            newPermission = Permission(
                name=permission.get('name'),
                module=permission.get('module'),
                route=permission.get('route')
            )
            db.session.add(newPermission)
            db.session.commit()
            return Response.success(data=[], message="Created Permission Success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def getUserPermissions(self):
        try:
            current_user = request.currentUser
            current_user_id = current_user.get('id')

            # Single query using OR condition
            permissions = db.session.query(Permission)\
                .distinct()\
                .outerjoin(UserPermission)\
                .filter(
                    or_(
                        exists().where(User.id == current_user_id).where(User.isAdmin == True),
                        UserPermission.userId == current_user_id
                    )
                ).all()
    
            result = [permission.to_dict() for permission in permissions]
    
            return Response.success(data=result, message="Get Permission User Success")
        except Exception as e:
            return Response.error(str(e), code=400)
        
    def getPermissions(self):
        try:
            
            query = db.session.query(Permission)
            permissions = query.order_by(Permission.updatedAt.desc()).all()
                
            result = [permission.to_dict() for permission in permissions]

            return Response.success(data=result, message="Get Permissions Success")
       
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def updatePermission(self, permissionId):
        try: 
            permissionData = request.get_json()
            permission = Permission.query.filter_by(id=permissionId).first() 
            if not permission:
                return Response.error("Permission not found", code=404)
            if not permissionData.get('name') and not permissionData.get('module') and not permissionData.get('route'):
                return Response.error({
                   'name': 'Name is required',
                    'route': 'Route is required',
                    'module': 'Module is required'
                }, code=400)
            
            elif not permissionData.get('route'):
                return Response.error({
                    'route': 'Route is required'
                }, code=400)
            
            elif not permissionData.get('name'):
                return Response.error({
                    'name': 'Name is required'
                }, code=400)
            
            elif not permissionData.get('module'):
                return Response.error({
                    'module': 'Module is required'
                }, code=400)
            
            existing_route = Permission.query.filter(
            Permission.route == permissionData['route'],
            Permission.id != permissionId  # Add this condition
            ).first()
            if existing_route:
                return Response.error({
                    'route': 'Route already exists'
                }, code=400)
            
            existing_name = Permission.query.filter(
            Permission.name == permissionData['name'],
            Permission.id != permissionId  # Add this condition
            ).first()
            if existing_name:
                return Response.error({
                    'name': 'Name already exists'
                }, code=400)
            
            existing_module = Permission.query.filter(
            Permission.module == permissionData['module'],
            Permission.id != permissionId
            ).first()
            if existing_module:
                return Response.error({
                    'module': 'Module already exists'
                }, code=400)
            
            permission.name = permissionData.get('name')
            permission.module = permissionData.get('module')
            permission.route = permissionData.get('route')
            permission.updatedAt = datetime.now()
            db.session.add(permission)
            db.session.commit()
            
            return Response.success(data=[], message="Updated Permission Success")
            
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def deletePermission(self, permissionId):
        try:
            permission = db.session.query(Permission).filter_by(id=permissionId).first()

            if not permission:
                return Response.error("Permission not found", code=400)
            
            db.session.delete(permission)
            db.session.commit()
            return Response.success(data=[], message="Permission Deleted Success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)