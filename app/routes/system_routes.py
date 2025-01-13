from flask import Blueprint
from app.controllers.system_controller import SystemController
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission

system_routes = Blueprint('systems', __name__, url_prefix='/systems')

controller = SystemController()

@system_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createSystem():
    return controller.create()

@system_routes.route("", methods=['GET'])
@tokenRequired
@checkPermission()
def getSystems():
    return controller.getAll()

@system_routes.route("/<int:systemId>", methods=['GET'])
@tokenRequired
@checkPermission()
def getSystem(systemId):
    return controller.getOne(systemId)

@system_routes.route("/<int:systemId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateSystem(systemId):
    return controller.update(systemId)

@system_routes.route("/<int:systemId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteSystem(systemId):
    return controller.delete(systemId)
