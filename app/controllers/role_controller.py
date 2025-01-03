from flask import jsonify, request
from ..models.role import Role
from ..models.permission import Permission
from ..models.role_permission import RolePermission
from app.db import db

class RoleController:
    def __init__(self):
        self.roles = []

    def createRole(self):
        role = request.get_json()
        roleName = role.get('name')
        description = role.get('description')

        isExisted = db.session.query(Role).filter_by(name=roleName).first()
        if isExisted:
            return jsonify({
                "status": "error",
                "message": "Role already exists"
            }), 409

        newRole = Role(name=roleName, description=description)
        db.session.add(newRole)
        db.session.commit()
        roleId = newRole.id

        permissionIds = role.get('permissionIds')
        for permissionId in permissionIds:
            self.addPermissionToRole(roleId, permissionId)

        return jsonify({
            "status": "success",
            "message": "Role created successfully",
            "data": newRole.to_dict(),
        }), 201

    def getRoles(self):
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (int(page) - 1) * int(limit)
        
        search = request.args.get('search', '')

        query = db.session.query(Role)
        if search:
            query = query.filter(Role.name.ilike(f'%{search}%'))
        
        roles = query.limit(limit).offset(skip).all()
        total = query.count()
        return jsonify({
            "status": "success",
            "data": [role.to_dict() for role in roles],
            "meta": {
                "total": total,
                "totalPages": -(-total // int(limit)),
                "currentPage": page,
                "pageSize": limit,
            }
        }), 200

    def getRole(self, roleId):
        role = db.session.query(Role).filter_by(id=roleId).first()

        if not role:
            return jsonify({
                "status": "error",
                "message": "Role not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": role.to_dict()
        }), 200

    def updateRole(self, roleId):
        role = db.session.query(Role).filter_by(id=roleId).first()

        if not role:
            return jsonify({
                "status": "error",
                "message": "Role not found"
            }), 404

        roleData = request.get_json()
        roleName = roleData.get('name')
        isExisted = db.session.query(Role).filter(Role.id != roleId, Role.name == roleName).first()
        if isExisted:
            return jsonify({
                "status": "error",
                "message": "Role already exists"
            }), 409

        role.name = roleName
        db.session.add(role)
        db.session.commit()
        roleId = role.id

        permissionIds = roleData.get('permissionIds')
        for permissionId in permissionIds:
            self.addPermissionToRole(roleId, permissionId)

        return jsonify({
            "status": "success",
            "message": "Role updated successfully",
            "data": role.to_dict()
        }), 200

    def deleteRole(self, roleId):
        role = db.session.query(Role).filter_by(id=roleId).first()

        if not role:
            return jsonify({
                "status": "error",
                "message": "Role not found"
            }), 404
        
        role.permissions.clear()
        
        db.session.delete(role)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Role deleted successfully"
        }), 200

    def addPermissionToRole(self, roleId: int, permissionId: int):
        role = db.session.query(Role).filter_by(id=roleId).first()

        if not role:
            return
        
        permission = db.session.query(Permission).filter_by(id=permissionId).first()
        if not permission:
            return
        
        isExisted = db.session.query(RolePermission).filter_by(
            roleId=roleId,
            permissionId=permissionId
        ).first()
        if isExisted:
            return

        role_permission = RolePermission(roleId=roleId, permissionId=permissionId)
        db.session.add(role_permission)
        db.session.commit()
