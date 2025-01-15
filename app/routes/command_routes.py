from flask import Blueprint
from app.controllers.command_controller import CommandController
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission

command_routes = Blueprint('commands', __name__, url_prefix='/commands')

controller = CommandController()

@command_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createCommand():
    return controller.create()

@command_routes.route("", methods=['GET'])
@tokenRequired
@checkPermission()
def getCommands():
    return controller.getAll()

@command_routes.route("/<int:commandId>", methods=['GET'])
@tokenRequired
@checkPermission()
def getCommand(commandId):
    return controller.getOne(commandId)

@command_routes.route("/<int:commandId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateCommand(commandId):
    return controller.update(commandId)

@command_routes.route("/<int:commandId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteCommand(commandId):
    return controller.delete(commandId)

@command_routes.route("/<int:commandId>/run", methods=['POST'])
@tokenRequired
@checkPermission()
def runCommand(commandId):
    return controller.run(commandId)
