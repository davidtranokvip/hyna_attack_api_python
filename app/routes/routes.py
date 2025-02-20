from flask import Blueprint, jsonify
from .auth_routes import auth_routes
from .user_routes import user_routes
from .permission_routes import permission_routes
from .check_host_routes import check_host_routes
from .system_routes import system_routes
from .command_routes import command_routes
from .attack_routes import attack_routes
from .setting_routes import setting_routes
from .team_routes import team_routes

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

def init_routes(app):
    api.register_blueprint(auth_routes)
    api.register_blueprint(user_routes)
    api.register_blueprint(permission_routes)
    api.register_blueprint(check_host_routes)
    api.register_blueprint(system_routes)
    api.register_blueprint(command_routes)
    api.register_blueprint(attack_routes)
    api.register_blueprint(team_routes)
    api.register_blueprint(setting_routes)
    app.register_blueprint(api)