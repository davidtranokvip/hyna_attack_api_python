from app.controllers.auth_controller import AuthController
from flask import Blueprint, jsonify, request
from app.models.user import User
from app.middleware.auth_middleware import tokenRequired

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

@auth_routes.route('/login', methods=['POST'])
def login():
    return AuthController.login()

@auth_routes.get("/me")
@tokenRequired
def get_current_user():
    currentUser = request.currentUser

    user = User.query.filter_by(id=currentUser['id']).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    return jsonify({
        'id': user.id,
        'email': user.email
    })