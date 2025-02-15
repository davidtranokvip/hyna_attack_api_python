from functools import wraps
from flask import request, jsonify
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.models.user import User
from app.db import db
import re




# def checkPermission():
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             if not hasattr(request, 'currentUser'):
#                 return jsonify({'message': 'Unauthorized'}), 401
#             try:
#                 currentUser = request.currentUser
#                 userId = currentUser.get('id')
#                 user = User.query.get(userId)
#                 if user and user.isAdmin:
#                     return f(*args, **kwargs)
                
#                 # Get current path and method
#                 path = request.path.replace('api/', '', 1)
#                 method = request.method

#                 # Query permissions for the user's role
#                 userPermissions = db.session.query(Permission)\
#                     .join(UserPermission, UserPermission.permissionId == Permission.id)\
#                     .filter(UserPermission.userId == userId)\
#                     .all()
                
#                 # Convert API path pattern to regex 
#                 hasPermission = any(
#                     (
#                         p.route.replace(':id', '[^/]+').replace('/', '\\/') == path or 
#                         re.match(
#                             fr"^{p.route.replace(':id', '[^/]+').replace('/', '/')}$",
#                             path
#                         )
#                     ) and p.method == method
#                     for p in userPermissions
#                     if p and p.route
#                 )

#                 if not hasPermission:
#                     return jsonify({'message': 'Permission denied'}), 403

#                 return f(*args, **kwargs)
#             except Exception as e:
#                 print(f"Permission check error: {str(e)}")
#                 return jsonify({'message': 'Error checking permissions'}), 500
                
#         return decorated
#     return decorator


def checkPermission():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'currentUser'):
                return jsonify({'message': 'Unauthorized'}), 401
            try:
                currentUser = request.currentUser
                userId = currentUser.get('id')
                
                # Check if user exists and is admin
                user = User.query.get(userId)
                if not user:
                    return jsonify({'message': 'User not found'}), 404
                    
                if user.isAdmin:
                    return f(*args, **kwargs)
                
                # Get current path and method
                path = request.path.replace('api/', '', 1)  # Remove api/ prefix
                method = request.method
                
                print(f"Checking permission for path: {path}, method: {method}")  # Debug log

                # Query permissions for the user
                userPermissions = db.session.query(Permission)\
                    .join(UserPermission, UserPermission.permissionId == Permission.id)\
                    .filter(UserPermission.userId == userId)\
                    .all()
                
                print(f"User permissions: {[p.to_dict() for p in userPermissions]}")  # Debug log

                if not userPermissions:
                    return jsonify({'message': 'No permissions found'}), 403

                # Convert API path pattern to regex 
                hasPermission = False
                for p in userPermissions:
                    if not p or not p.route:
                        continue
                        
                    # Create pattern for route matching
                    route_pattern = p.route.replace(':id', '[^/]+')
                    
                    # Check if paths match and methods match
                    path_matches = (
                        route_pattern == path or 
                        re.match(fr"^{route_pattern}$", path)
                    )
                    method_matches = p.method == method
                    
                    print(f"Checking route: {p.route} -> pattern: {route_pattern}")  # Debug log
                    print(f"Against path: {path}, method: {method}")  # Debug log
                    print(f"Path matches: {path_matches}, Method matches: {method_matches}")  # Debug log
                    
                    if path_matches and method_matches:
                        hasPermission = True
                        break

                if not hasPermission:
                    return jsonify({
                        'message': 'Permission denied',
                        'path': path,
                        'method': method,
                        'available_permissions': [p.to_dict() for p in userPermissions]
                    }), 403

                return f(*args, **kwargs)
                
            except Exception as e:
                print(f"Permission check error: {str(e)}")
                return jsonify({'message': f'Error checking permissions: {str(e)}'}), 500
                
        return decorated
    return decorator
