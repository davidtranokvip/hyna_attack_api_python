from flask import Blueprint

from app.middleware.auth_middleware import tokenRequired
from ..controllers.server_controller import ServerController

server_routes = Blueprint('servers', __name__, url_prefix='/servers')
controller = ServerController()

@server_routes.route("", methods=['POST'])
@tokenRequired
def createServer():
    return controller.create()

@server_routes.route("", methods=['GET'])
@tokenRequired
def getServers():
    return controller.getAll()

@server_routes.route("/team", methods=['GET'])
@tokenRequired
def getServersForTeam():
    return controller.getServersForTeam()

@server_routes.route("/<int:serverId>", methods=['PUT'])
@tokenRequired
def updateServer(serverId):
    return controller.update(serverId)

@server_routes.route("/<int:serverId>", methods=['DELETE'])
@tokenRequired
def deleteServer(serverId):
    return controller.delete(serverId)  

