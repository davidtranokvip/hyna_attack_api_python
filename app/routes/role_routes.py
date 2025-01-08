from flask import Blueprint

from app.middleware.auth_middleware import tokenRequired
from ..controllers.role_controller import RoleController
from ..middleware.permission_middleware import checkPermission

role_routes = Blueprint('roles', __name__, url_prefix='/roles')
controller = RoleController()

@role_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createRole():
    return controller.createRole()

@role_routes.route("", methods=['GET'])
@tokenRequired
@checkPermission()
def getRoles():
    return controller.getRoles()

@role_routes.route("/<int:roleId>", methods=['GET'])
@tokenRequired
@checkPermission()
def getRole(roleId):
    return controller.getRole(roleId)

@role_routes.route("/<int:roleId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateRole(roleId):
    return controller.updateRole(roleId)

@role_routes.route("/<int:roleId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteRole(roleId):
    return controller.deleteRole(roleId)