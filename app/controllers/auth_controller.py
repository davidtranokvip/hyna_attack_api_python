from app.utils.decrypt_payload import decrypt_payload
from datetime import datetime, timedelta, timezone
from app.configs.whitelist import WHITELISTED_IPS
from app.services.response import Response
from app.models.user_log import UserLog
from sqlalchemy import and_, or_, func
from app.models.user import User
from flask import request
from app.db import db
import pytz
import jwt
import os

vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')

class AuthController:
    @staticmethod
    def login():
        try:
            clientIp = request.headers.get("X-Forwarded-For", request.remote_addr)
            if clientIp not in WHITELISTED_IPS:
                return Response.error(message="Access Denied", code=400)

            data = decrypt_payload(request.get_json())
            current_time = datetime.now(vn_timezone).time()

            user = User.query.filter(
                func.binary(User.nameAccount) == data['nameAccount'],
                and_(
                    or_(User.entryTime.is_(None), User.entryTime <= current_time),
                    or_(User.exitTime.is_(None), User.exitTime >= current_time)
                )
            ).first()

            if not user or not user.check_password(data['password']):
                return Response.error("Access Denied", code=403)

            if not user.status:
                return Response.error("User Blocked", code=403)

            if not user.isAdmin:
                log_entry = UserLog(
                    ip=clientIp,
                    name_account=user.to_dict()['nameAccount'],
                    detail="LOGIN",
                    time_active=datetime.now(vn_timezone)
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
            return Response.error("REQUIRED VALUE", code=400)

        except Exception as e:
            db.session.rollback()
            return Response.error(message=f"Internal Server Error: {str(e)}", code=500)

    @staticmethod
    def createToken(user):
        TOKEN_EXPIRATION = 10
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION)
        
        SECRET_KEY = os.getenv("SECRET_KEY")
        user_data = vars(user) if not isinstance(user, dict) else user
    
        payload = { 
            'id': user_data.get('id'),
            'email': user_data.get('email'),
            'team_id': user_data.get('team_id'),
            'nameAccount': user_data.get('nameAccount'),
            'isAdmin': user_data.get('isAdmin'),
            'expires_at': int(expiration_time.timestamp())
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {'token': token}

    @staticmethod
    def updatePassword():
        if not hasattr(request, 'currentUser') or not request.currentUser:
            return Response.error("Unauthorized", code=401)
        
        currentUser = request.currentUser
        payload = decrypt_payload(request.get_json())

        current_password = payload.get('currentPassword')
        new_password = payload.get('newPassword')

        if not currentUser.check_password(password=current_password):
            return Response.error({"currentPassword": "Incorrect current password"}, code=400)
        
        currentUser.set_password(password=new_password)
        db.session.commit()

        return Response.success(data=[], message="Updated Success")

            
