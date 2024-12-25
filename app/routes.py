from flask import Blueprint, jsonify
from app.controllers.auth_controller import AuthController

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@api.route('/auth/login', methods=['POST'])
def login():
    return AuthController.login()

@api.route('/auth/register', methods=['POST'])
def register():
    return AuthController.register()

# @api.route('/protected', methods=['GET'])
# @AuthController.token_required
# def protected(current_user):
#     return jsonify({'message': f'Hello {current_user.email}'}), 200

def init_routes(app):
    app.register_blueprint(api, url_prefix='/api')
