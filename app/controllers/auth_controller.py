import os
from flask import jsonify, request
from app.models.user import User
from app.db import db
import jwt
from app.configs.whitelist import WHITELISTED_IPS
from datetime import datetime, timedelta
import re
from cryptography.hazmat.primitives import serialization
from app.utils.decrypt_payload import decrypt_payload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
private_key_path = os.path.join(BASE_DIR, 'configs', 'private_key.pem')

with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

class AuthController:
    @staticmethod
    def register():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Enter email or password'}), 400

        # Validate email format
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'message': 'Invalid email format'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 409

        # Validate password strength (min 8 chars)
        if len(data['password']) < 8:
            return jsonify({'message': 'Password must be at least 8 characters'}), 400

        # Create new user
        new_user = User(email=data['email'])
        new_user.set_password(data['password'])

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'User registered successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Registration failed'}), 500

    @staticmethod
    def login():    
        data = request.get_json()
        
        clientIp = request.remote_addr
        if clientIp not in WHITELISTED_IPS:
            return jsonify({
                "status": "error",
                "message": "Access Denied"
            }), 400

        try:
            payload = decrypt_payload(data, private_key)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        
        if not payload or not payload.get('nameAccount') or not payload.get('password'):
            return jsonify({'message': 'Enter email or password'}), 400

        user = User.query.filter_by(nameAccount=payload['nameAccount']).first()

        if not user or not user.check_password(payload['password']):
            return jsonify({'message': 'Access Denied ', 'status': 'error'}), 401
        expiration_time = datetime.utcnow() + timedelta(minutes=100)

        token = jwt.encode({
            'id': user.id,
            'email': user.email,
            'team_id': user.team_id,
            'nameAccount': user.nameAccount,
            'isAdmin': user.isAdmin,
            'exp': expiration_time
        }, os.getenv("SECRET_KEY"), algorithm='HS256')

        return jsonify({
            'status': "success",
            'message': "Access Authorized",
            'data': {
                'token' : token,
            }
        })

