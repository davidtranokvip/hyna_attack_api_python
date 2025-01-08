from flask import Blueprint
from ..controllers.role_controller import RoleController

role_routes = Blueprint('roles', __name__, url_prefix='/roles')

controller = RoleController()

@role_routes.route("", methods=['POST'])
def createRole():
    return controller.createRole()

@role_routes.route("", methods=['GET'])
def getRoles():
    return controller.getRoles()

@role_routes.route("/<int:roleId>", methods=['GET'])
def getRole(roleId):
    return controller.getRole(roleId)

@role_routes.route("/<int:roleId>", methods=['PUT'])
def updateRole(roleId):
    return controller.updateRole(roleId)

@role_routes.route("/<int:roleId>", methods=['DELETE'])
def deleteRole(roleId):
    return controller.deleteRole(roleId)