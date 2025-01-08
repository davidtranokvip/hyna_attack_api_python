from functools import wraps
from flask import request, jsonify
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.db import db
import re

def checkPermission():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'currentUser'):
                return jsonify({'message': 'Unauthorized'}), 401

            currentUser = request.currentUser
            roleId = currentUser.get('roleId')
            
            # Get current path and method
            path = request.path
            method = request.method

            # Query permissions for the user's role
            rolePermissions = db.session.query(Permission)\
                .join(RolePermission, RolePermission.permissionId == Permission.id)\
                .filter(RolePermission.roleId == roleId)\
                .all()
            
            print(rolePermissions)

            
            # Convert API path pattern to regex 
            hasPermission = any(
            (
                p.apiPath.replace(':id', '[^/]+').replace('/', '\\/') == path or 
                re.match(
                    fr"^{p.apiPath.replace(':id', '[^/]+').replace('/', '/')}$",
                    path
                )
            ) and p.method == method
            for p in rolePermissions
            )

            if not hasPermission:
                return jsonify({'message': 'Permission denied'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
