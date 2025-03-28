from app.controllers.auth_controller import AuthController
from app.middleware.auth_middleware import tokenRequired
from flask import Blueprint

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

@auth_routes.route('/login', methods=['POST'])
def login():
    return AuthController.login()

@auth_routes.route("/change_password", methods=['POST'])
@tokenRequired
def updatePassword():
    return AuthController.updatePassword()