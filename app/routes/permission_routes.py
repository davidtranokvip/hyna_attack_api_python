from flask import Blueprint

from app.middleware.auth_middleware import tokenRequired
from ..controllers.permission_controller import PermissionController
from ..models.permission import Permission
from ..middleware.permission_middleware import checkPermission

permission_routes = Blueprint('permissions', __name__, url_prefix='/permissions')

controller = PermissionController()

@permission_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createPermission():
    return controller.createPermission()

@permission_routes.route("", methods=['GET'])
@tokenRequired
@checkPermission()
def getPermissions():
    return controller.getPermissions()

@permission_routes.route("/<int:permissionId>", methods=['GET'])
@tokenRequired
@checkPermission()
def getPermission(permissionId):
    return controller.getPermission(permissionId)

@permission_routes.route("/<int:permissionId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updatePermission(permissionId):
    return controller.updatePermission(permissionId)

@permission_routes.route("/<int:permissionId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deletePermission(permissionId):
    return controller.deletePermission(permissionId)
