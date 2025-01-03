from flask import jsonify, request
from ..models.permission import Permission
from datetime import datetime
from app.db import db
from app.models.role_permission import RolePermission

class PermissionController:
    def __init__(self):
        self.permissions = []

    def createPermission(self):
        permission = request.get_json()

        newPermission = Permission(
            name=permission.get('name'),
            method=permission.get('method'),
            module=permission.get('module'),
            apiPath=permission.get('apiPath')
        )
        db.session.add(newPermission)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Permission created successfully",
            "data": newPermission.to_dict()
        }), 201

    def getPermissions(self):
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (int(page) - 1) * int(limit)
        
        search = request.args.get('search', '')
        method = request.args.get('method', '')
        module = request.args.get('module', '')
        apiPath = request.args.get('apiPath', '')

        query = db.session.query(Permission)
        if search:
            query = query.filter(Permission.name.ilike(f'%{search}%'))
        if method:
            query = query.filter(Permission.method.ilike(f'%{method}%'))
        if module:
            query = query.filter(Permission.module.ilike(f'%{module}%'))
        if apiPath:
            query = query.filter(Permission.apiPath.ilike(f'%{apiPath}%'))
        
        permissions = query.limit(limit).offset(skip).all()
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
       

    def getPermission(self, permissionId):
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

    def updatePermission(self, permissionId):
        permission = request.get_json()
        permissionName = permission.get('name')
        permissionMethod = permission.get('method')
        permissionModule = permission.get('module')
        permissionApiPath = permission.get('apiPath')

        permission = db.session.query(Permission).filter_by(id=permissionId).first()

        if not permission:
            return jsonify({
                "status": "error",
                "message": "Permission not found"
            }), 404

        permission.name = permissionName
        permission.method = permissionMethod
        permission.module = permissionModule
        permission.apiPath = permissionApiPath
        permission.updatedAt = datetime.now()

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Permission updated successfully",
            "data": permission.to_dict()
        }), 200

    def deletePermission(self, permissionId):
        permission = db.session.query(Permission).filter_by(id=permissionId).first()

        if not permission:
            return jsonify({
                "status": "error",
                "message": "Permission not found"
            }), 404
        
        db.session.query(RolePermission).filter_by(permissionId=permissionId).delete()

        db.session.delete(permission)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Permission deleted successfully"
        }), 200