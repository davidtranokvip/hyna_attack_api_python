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

@attack_routes.route('/cancel_all_processes', methods=['POST'])
@tokenRequired
def cancel_all_processes():
    return controller.cancel_all_processes()

@attack_routes.route('/terminate/<int:logId>', methods=['POST'])
@tokenRequired
def terminate_attack(logId):
    return controller.terminate_attack(logId)

@attack_routes.route('/terminate/<int:logId>/server/<string:serverHostname>', methods=['POST'])
@tokenRequired
def terminate_server_attack(logId, serverHostname):
    return controller.terminate_server_attack(logId, serverHostname)

# API NEW
@attack_routes.route('/start_process', methods=['POST'])
@tokenRequired
def start_process():
    return controller.start_process()

@attack_routes.route('/list_processes', methods=['GET'])
@tokenRequired
def list_processes():
    return controller.list_processes()

@attack_routes.route('/stop_process/<int:pid>', methods=['POST'])
@tokenRequired
def stop_process(pid):
    return controller.stop_process(pid)