from flask import Blueprint
from app.middleware.permission_middleware import checkPermission
from app.controllers.user_controller import UserController
from app.middleware.auth_middleware import tokenRequired

user_routes = Blueprint('users', __name__, url_prefix='/users')
controller = UserController()

@user_routes.route("", methods=['POST'])
# @checkPermission()
@tokenRequired
def createUser():
    return controller.create()
    
@user_routes.get("")
@tokenRequired
# @checkPermission()
def getUsers():
    return controller.getAll()

@user_routes.get("/log")
@tokenRequired
# @checkPermission()
def getUserLog():
    return controller.userLog()

@user_routes.route("/<int:userId>", methods=['PUT'])
@tokenRequired
# @checkPermission()
def updateUser(userId: int):
    return controller.update(userId)

@user_routes.route("/<int:userId>", methods=['DELETE'])
@tokenRequired
# @checkPermission()
def deleteUser(userId: int):
    return controller.delete(userId)