from flask import Blueprint
from ..controllers.permission_controller import PermissionController
from ..models.permission import Permission

permission_routes = Blueprint('permissions', __name__, url_prefix='/permissions')

controller = PermissionController()

@permission_routes.route("", methods=['POST'])
def createPermission():
    return controller.createPermission()

@permission_routes.route("", methods=['GET'])
def getPermissions():
    return controller.getPermissions()

@permission_routes.route("/<int:permissionId>", methods=['GET'])
def getPermission(permissionId):
    return controller.getPermission(permissionId)

@permission_routes.route("/<int:permissionId>", methods=['PUT'])
def updatePermission(permissionId):
    return controller.updatePermission(permissionId)

@permission_routes.route("/<int:permissionId>", methods=['DELETE'])
def deletePermission(permissionId):
    return controller.deletePermission(permissionId)
