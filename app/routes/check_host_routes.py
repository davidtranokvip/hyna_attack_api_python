from ..controllers.check_host_controller import CheckHostController
from flask import Blueprint

check_host_routes = Blueprint('check_host', __name__, url_prefix='/check_host')

controller = CheckHostController()

@check_host_routes.route("/get_list", methods=['POST'])
def get_list():
    return controller.get_list()