from app.services.response import Response
from app.models.setting import Setting
from flask import request
from app.db import db

class SettingController:
    def create(self):
        try:
            data_list = request.get_json()
            
            if not isinstance(data_list, list):
                data_list = [data_list]
            
            created_settings = []
            for data in data_list:
                
                if not data.get('input'):
                    return Response.error({"input": "Input type is required"}, code=400)

                existing_setting = Setting.query.filter_by(
                    group=data['group'],
                    type=data['type']
                ).first()   
                
                if existing_setting:
                    return Response.error({"group": "group type in mode attack already exists"}, code=400)
                
                stt_setting = Setting.query.filter_by(
                    stt=data['stt'],
                ).first()
                
                if stt_setting:
                    return Response.error({'stt': 'STT already exists'}, code=400)

                if not isinstance(data['value'], list):
                    return Response.error('Value must be an array', code=400)

                for item in data['value']:
                    if not isinstance(item, dict):
                        return Response.error('Each item in value must be an object', code=400)
                
                new_setting = Setting(
                    value=data['value'],
                    group=data['group'],
                    type=data['type'],  
                    input=data['input'],  
                    description=data['description'],
                    stt=data['stt'],
                )
                
                db.session.add(new_setting)
                created_settings.append(new_setting)
            
            db.session.commit()
            return Response.success(data=[], message="Settings Created Success")
            
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def getAll(self):
        try:

            query = db.session.query(Setting)
            settings = query.order_by(Setting.updatedAt.desc()).all()
            
            result = [setting.toDict() for setting in settings]
            return Response.success(data=result, message="Get field attack success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def update(self, settingId: int):
        try: 
            setting = Setting.query.filter_by(id=settingId).first()
            if not setting:
                return Response.error('Setting not found', code=404)
            
            data = request.get_json()

            if 'value' not in data or not data['value']:
                return Response.error({'group': 'Value is required'}, code=400)
            
            if 'input' not in data or not data['input']:
                return Response.error({'input': 'Input is required'}, code=400)
        
            new_value = data.get('value')
            new_type = data.get('type', setting.type)
            new_group = data.get('group', setting.group)
            new_input = data.get('input')
            new_description = data.get('description', setting.description)
            new_stt = data.get('stt', setting.stt)
            
            if new_stt is not None:
                existing_stt = Setting.query.filter(Setting.stt == new_stt, Setting.id != settingId).first()
                if existing_stt:
                    return Response.error({'stt': 'STT already exists'}, code=400)
                
            if new_group and new_type:
                existing_group_in_type = Setting.query.filter(
                    Setting.group == new_group, 
                    Setting.type == new_type,
                    Setting.id != settingId
                ).first()
                if existing_group_in_type:
                    return Response.error({'group': f"Group {new_group.upper()} already exists in type {new_type.upper()}"}, code=400)
                
            setting.value = new_value
            setting.type = new_type
            setting.group = new_group
            setting.input = new_input
            setting.description = new_description
            setting.stt = new_stt

            db.session.commit()
            return Response.success(data=[], message="Updated Setting Success")
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def delete(self, settingId: int):
        try:
            setting = Setting.query.filter_by(id=settingId).first()
            if not setting:
                return Response.error('Setting not found', code=400)
            
            db.session.delete(setting)
            db.session.commit()
            return Response.success(data=[], message="Delete Setting Success")
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
