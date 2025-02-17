import os
from flask import jsonify, request
from app.models.user import User
from app.db import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
import re

class AuthController:
    @staticmethod
    def register():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400

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
            print(e)
            return jsonify({'message': 'Registration failed'}), 500

    @staticmethod
    def login():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401

        token = jwt.encode({
            'id': user.id,
            'email': user.email,
            'isAdmin': user.isAdmin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, os.getenv("SECRET_KEY"), algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'email': user.email,
            }
        })

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'message': 'Token is missing'}), 401

            try:
                # Split token to remove 'Bearer ' prefix if present
                token_value = token.split()[1] if len(token.split()) > 1 else token
                data = jwt.decode(token_value, os.getenv("SECRET_KEY"), algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
            except:
                return jsonify({'message': 'Token is invalid'}), 401

            return f(current_user, *args, **kwargs)
        return decorated
