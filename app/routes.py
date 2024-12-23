from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

def init_routes(app):
    app.register_blueprint(api, url_prefix='/api')
