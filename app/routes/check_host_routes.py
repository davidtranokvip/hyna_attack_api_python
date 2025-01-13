from flask import Blueprint
from ..controllers.check_host_controller import CheckHostController

check_host_routes = Blueprint('check-hosts', __name__, url_prefix='/check-hosts')

controller = CheckHostController()

@check_host_routes.route("", methods=['POST'])
def checkHost():
    return controller.checkHost()