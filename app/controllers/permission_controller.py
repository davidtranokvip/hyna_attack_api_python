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
            
            existing_permission = Permission.query.filter_by(
                # method=permission['method'],
                module=permission['module'],
                route=permission['route'],
            ).first()
            
            if existing_permission:
                return jsonify({
                    "status": "error",
                    "message": f"Permission already exists"
                }), 400

            newPermission = Permission(
                name=permission.get('name'),
                # method=permission.get('method'),
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
            permission = request.get_json()
            permissionName = permission.get('name')
            # permissionMethod = permission.get('method')
            permissionModule = permission.get('module')
            permissionroute = permission.get('route')

            permission = db.session.query(Permission).filter_by(id=permissionId).first()

            if not permission:
                return jsonify({
                    "status": "error",
                    "message": "Permission not found"
                }), 404

            permission.name = permissionName
            # permission.method = permissionMethod
            permission.module = permissionModule
            permission.route = permissionroute
            permission.updatedAt = datetime.now()

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