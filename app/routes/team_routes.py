from flask import Blueprint

from app.controllers.team_controller import TeamController
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission

team_routes = Blueprint('teams', __name__, url_prefix='/teams')

controller = TeamController()

@team_routes.route("", methods=['GET'])
@tokenRequired 
@checkPermission()
def getTeams():
    return controller.getAll()

@team_routes.route("/parent", methods=['GET'])
@tokenRequired 
@checkPermission()
def getParent():
    return controller.getParentAll()

@team_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createTeam():
    return controller.create()

@team_routes.route("/<int:teamId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateTeam(teamId):
    return controller.update(teamId)

@team_routes.route("/<int:teamId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteTeam(teamId):
    return controller.delete(teamId)
