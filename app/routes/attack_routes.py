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
