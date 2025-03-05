from flask import jsonify, request
from ..models.permission import Permission
from datetime import datetime
from app.db import db
from app.models.user_permission import UserPermission
from app.models.user import User
from sqlalchemy import or_, exists

class PermissionController:
    def __init__(self):
        self.permissions = []

    def createPermission(self):
        try:
            permission = request.get_json()
            
            if not permission.get('name') and not permission.get('module') and not permission.get('route'):
                return jsonify({
                    'message': {
                        'name': 'Name is required',
                        'route': 'Route is required',
                        'module': 'Module is required'
                    }, 'status': 'error'
                }), 400
            if not permission.get('name'):
                return jsonify({
                    'message': {
                        'name': 'Name is required'
                    }, 'status': 'error'
                }), 400
            elif not permission.get('module'):
                return jsonify({
                    'message': {
                        'module': 'Module is required'
                    }, 'status': 'error'
                }), 400
            elif not permission.get('route'):
                return jsonify({
                    'message': {
                        'route': 'Route is required'
                    }, 'status': 'error'
                }), 400
            
            existing_permission = Permission.query.filter_by(
                route=permission['route'],
            ).first()
            if existing_permission:
                return jsonify({
                    'message': {
                        'route': 'Route already exists'
                    }, 'status': 'error'
                }), 400

            newPermission = Permission(
                name=permission.get('name'),
                module=permission.get('module'),
                route=permission.get('route')
            )
            db.session.add(newPermission)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Permission created successfully",
                "data": newPermission.to_dict()
            }), 201 
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

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
    
            return jsonify({
                "status": "success",
                "data": [permission.to_dict() for permission in permissions]
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error", 
                "message": str(e)
            }), 400
    def getPermissions(self):
        try: 
            limit = int(request.args.get('limit', 10))
            page = int(request.args.get('page', 1))
            skip = (int(page) - 1) * int(limit)
            
            search = request.args.get('search', '')
            method = request.args.get('method', '')
            module = request.args.get('module', '')
            route = request.args.get('route', '')

            query = db.session.query(Permission)
            if search:
                query = query.filter(Permission.name.ilike(f'%{search}%'))
            if method:
                query = query.filter(Permission.method.ilike(f'%{method}%'))
            if module:
                query = query.filter(Permission.module.ilike(f'%{module}%'))
            if route:
                query = query.filter(Permission.route.ilike(f'%{route}%'))
            
            permissions = query.order_by(Permission.updatedAt.desc()).limit(limit).offset(skip).all()
            total = query.count()

            return jsonify({
                "status": "success",
                "data": [permission.to_dict() for permission in permissions],
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
    def getPermission(self, permissionId):
        try:
            permission = db.session.query(Permission).filter_by(id=permissionId).first()

            if not permission:
                return jsonify({
                    "status": "error",
                    "message": "Permission not found"
                }), 404
            
            return jsonify({
                "status": "success",
                "data": permission.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    def updatePermission(self, permissionId):
        try: 
            permissionData = request.get_json()
            permission = Permission.query.filter_by(id=permissionId).first() 
            if not permission:
                return jsonify({
                    "status": "error",
                    "message": "Permission not found"
                }), 404
            if not permissionData.get('name') and not permissionData.get('module') and not permissionData.get('route'):
                return jsonify({
                    'message': {
                        'name': 'Name is required',
                        'route': 'Route is required',
                        'module': 'Module is required'
                    }, 'status': 'error'
                }), 400
            elif not permissionData.get('route'):
                return jsonify({
                    'message': {
                        'route': 'Route is required'
                    }, 'status': 'error'
                }), 400
            
            elif not permissionData.get('name'):
                return jsonify({
                    'message': {
                        'name': 'Name is required'
                    }, 'status': 'error'
                }), 400
            elif not permissionData.get('module'):
                return jsonify({
                    'message': {
                        'module': 'Module is required'
                    }, 'status': 'error'
                }), 400
            
            existing_route = Permission.query.filter(
            Permission.route == permissionData['route'],
            Permission.id != permissionId  # Add this condition
            ).first()
            if existing_route:
                return jsonify({
                    'message': {
                        'route': 'Route already exists'
                    },
                    'status': 'error'
                }), 409
            existing_name = Permission.query.filter(
            Permission.name == permissionData['name'],
            Permission.id != permissionId  # Add this condition
            ).first()
            if existing_name:
                return jsonify({
                    'message': {
                        'name': 'Name already exists'
                    }, 'status': 'error'
                }), 400
            existing_module = Permission.query.filter(
            Permission.module == permissionData['module'],
            Permission.id != permissionId  # Add this condition
            ).first()
            if existing_module:
                return jsonify({
                    'message': {
                        'module': 'Module already exists'
                    }, 'status': 'error'
                }), 400
            
            permission.name = permissionData.get('name')
            # permission.method = ppermission.get('method')
            permission.module = permissionData.get('module')
            permission.route = permissionData.get('route')
            permission.updatedAt = datetime.now()
            db.session.add(permission)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Permission updated successfully",
                "data": permission.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        
    def deletePermission(self, permissionId):
        try:
            permission = db.session.query(Permission).filter_by(id=permissionId).first()

            if not permission:
                return jsonify({
                    "status": "error",
                    "message": "Permission not found"
                }), 404
            
            db.session.delete(permission)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Permission deleted successfully"
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400