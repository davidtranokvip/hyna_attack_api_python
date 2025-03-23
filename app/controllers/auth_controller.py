import os
from flask import jsonify, request
from sqlalchemy import and_, or_, func
from app.models.user import User
from app.db import db
import jwt
from app.configs.whitelist import WHITELISTED_IPS
import pytz
from datetime import datetime, timedelta, timezone
from app.models.user_log import UserLog
from cryptography.hazmat.primitives import serialization
from app.utils.decrypt_payload import decrypt_payload
from app.services.response import Response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
private_key_path = os.path.join(BASE_DIR, 'configs', 'private_key.pem')
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')

with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

class AuthController:
    @staticmethod
    def login():
        try:
            clientIp = request.headers.get("X-Forwarded-For", request.remote_addr)
            if clientIp not in WHITELISTED_IPS:
                return Response.error(message=f"{clientIp} IP Access Denied", code=400)

            data = request.get_json()
            
            current_time = datetime.now(vn_timezone).strftime("%H:%M:%S")

            user = User.query.filter(
                func.binary(User.nameAccount) == data['nameAccount'],
                and_(
                    or_(User.entryTime.is_(None), User.entryTime <= current_time),
                    or_(User.exitTime.is_(None), User.exitTime >= current_time)
                )
            ).first()

            if not user or not user.check_password(data['password']):
                return Response.error("Invalid credentials or access time", code=403)

            if not user.isAdmin:
                log_entry = UserLog(
                    ip=clientIp,
                    name_account=user.to_dict()['nameAccount'],
                    detail="LOGIN",
                    time_active=datetime.now(vn_timezone).strftime("%Y-%m-%d %H:%M:%S")
                )
                db.session.add(log_entry)
                db.session.commit()
            
            token_data = AuthController.createToken(user.to_dict())

            if isinstance(token_data, str):
                return Response.error(message=token_data, code=500)

            user_info = user.to_dict()
            user_info.pop("password", None)

            token_data["user"] = user_info

            return Response.success(data=token_data, message="Access Authorized")
        except KeyError as e:
            return Response.error(f"Missing key: {str(e)}", code=400)

        except Exception as e:
            db.session.rollback()
            return Response.error(message=f"Internal Server Error: {str(e)}", code=500)
    
    @staticmethod
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, list):
            return [AuthController.convert_datetime(item) for item in obj]
        if isinstance(obj, dict):
            return {key: AuthController.convert_datetime(value) for key, value in obj.items()}
        return obj

    @staticmethod
    def createToken(user):
        TOKEN_EXPIRATION = 600
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=TOKEN_EXPIRATION)
        
        SECRET_KEY = os.getenv("SECRET_KEY")
        if not SECRET_KEY:
            return "Missing SECRET_KEY in environment variables"
        
        payload = vars(user) if not isinstance(user, dict) else user
        payload.pop("password", None)
        payload["exp"] = expiration_time.timestamp()
        payload = AuthController.convert_datetime(payload)

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {'token': token, 'expires_at': expiration_time.isoformat()}

    @staticmethod
    def updatePassword():
        if not hasattr(request, 'currentUser') or not request.currentUser:
            return Response.error("Unauthorized", code=401)
        
        currentUser = request.currentUser

        payload = request.get_json()

        try:
            payload = decrypt_payload(payload, private_key)
        except Exception as e:
            return Response.error(f"Failed to decrypt payload: {str(e)}", code=400)

        current_password = payload.get('currentPassword')
        new_password = payload.get('newPassword')

        if not current_password or not new_password:
            return Response.error("Current password and new password are required", code=400)

        user = User.query.get(currentUser['id'])
        if not user:
            return Response.error("User not found", code=404)

        if not user.check_password(password=current_password):
            return Response.error("Incorrect current password", code=403)

        if len(new_password) < 8:
            return Response.error("New password must be at least 8 characters long", code=400)

        user.set_password(password=new_password)
        db.session.commit()

        return Response.success("Password updated successfully")

            
