from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config
from app.models.user import User
from app.services.response import Response

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        if not token:
            return Response.error(message='Token is missing', code=401)

        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

            user = User.query.get(payload.get('id'))
            
            if not user:
                return Response.error(message='User not found', code=401)

            request.currentUser = user 
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return Response.error(message='Token has expired', code=401)

        except jwt.InvalidTokenError:
            return Response.error(message='Invalid token', code=401)


    return decorated
