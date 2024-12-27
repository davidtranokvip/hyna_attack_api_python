from flask import Blueprint, jsonify, url_for
from .auth_routes import auth_routes
from .user_routes import user_routes

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

def init_routes(app):
    api.register_blueprint(auth_routes)
    api.register_blueprint(user_routes)
    app.register_blueprint(api)
