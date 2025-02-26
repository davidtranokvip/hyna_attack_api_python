from flask import Blueprint

from app.middleware.auth_middleware import tokenRequired
from ..controllers.attack_controller import AttackController

attack_routes = Blueprint('attacks', __name__, url_prefix='/attacks')
controller = AttackController()

@attack_routes.route("", methods=['POST'])
@tokenRequired
def attack():
    return controller.attack()

@attack_routes.route("", methods=['GET'])
@tokenRequired
def getAttacks():
    return controller.getLogs()

@attack_routes.route('/terminate/<int:logId>', methods=['POST'])
@tokenRequired
def terminate_attack(logId):
    return controller.terminate_attack(logId)

@attack_routes.route('/terminate/<int:logId>/server/<string:serverHostname>', methods=['POST'])
@tokenRequired
def terminate_server_attack(logId, serverHostname):
    return controller.terminate_server_attack(logId, serverHostname)
