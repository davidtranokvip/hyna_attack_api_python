from flask import Blueprint
from app.controllers.setting_controller import SettingController
from app.middleware.auth_middleware import tokenRequired
from app.middleware.permission_middleware import checkPermission

setting_routes = Blueprint('settings', __name__, url_prefix='/settings')

controller = SettingController()

@setting_routes.route("", methods=['POST'])
@tokenRequired
@checkPermission()
def createSetting():
    return controller.create()

@setting_routes.route("", methods=['GET'])
@tokenRequired
# @checkPermission()
def getSettings():
    return controller.getAll()

@setting_routes.route("/<int:settingId>", methods=['GET'])
@tokenRequired
@checkPermission()
def getSetting(settingId):
    return controller.getOne(settingId)

@setting_routes.route("/<int:settingId>", methods=['PUT'])
@tokenRequired
@checkPermission()
def updateSetting(settingId):
    return controller.update(settingId)

@setting_routes.route("/<int:settingId>", methods=['DELETE'])
@tokenRequired
@checkPermission()
def deleteSetting(settingId):
    return controller.delete(settingId)
