from ..controllers.attack_controller import AttackController
from app.middleware.auth_middleware import tokenRequired
from flask import Blueprint

attack_routes = Blueprint('attacks', __name__, url_prefix='/attacks')
controller = AttackController()

@attack_routes.route("", methods=['POST'])
@tokenRequired
def attack():
    return controller.attack()

@attack_routes.route('/stop_processes', methods=['POST'])
@tokenRequired
def stop_process():
    return controller.stop_process()

@attack_routes.route('/list_processes', methods=['GET'])
@tokenRequired
def list_processes():
    return controller.list_processes()

@attack_routes.route('/terminate/<int:logId>/server/<string:serverHostname>', methods=['POST'])
@tokenRequired
def terminate_server_attack(logId, serverHostname):
    return controller.terminate_server_attack(logId, serverHostname)