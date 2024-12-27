# from flask import Blueprint
from app.controllers.auth_controller import AuthController
from flask import Blueprint, jsonify

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

@auth_routes.route('/login', methods=['POST'])
def login():
    return AuthController.login()
