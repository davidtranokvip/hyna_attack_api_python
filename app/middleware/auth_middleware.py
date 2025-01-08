from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            currentUser = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            request.currentUser = currentUser
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated
