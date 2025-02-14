from flask import jsonify, request
from app.models.setting import Setting
from app.db import db

class SettingController:
    def create(self):
        try:
            data_list = request.get_json()
            if not isinstance(data_list, list):
                data_list = [data_list]
            
            created_settings = []
            for data in data_list:
                
                existing_setting = Setting.query.filter_by(
                    group=data['group'],
                    type=data['type']
                ).first()
                
                if existing_setting:
                    return jsonify({
                        "status": "error",
                        "message": f"Setting with group '{data['group']}' and type '{data['type']}' already exists"
                    }), 400
            

                if not isinstance(data['value'], list):
                    return jsonify({
                        "status": "error",
                        "message": "Value must be an array"
                    }), 400

                for item in data['value']:
                    if not isinstance(item, dict):
                        return jsonify({
                            "status": "error",
                            "message": "Each item in value must be an object"
                        }), 400
                
                new_setting = Setting(
                    value=data['value'],
                    group=data['group'],
                    type=data['type']
                )
                
                db.session.add(new_setting)
                created_settings.append(new_setting)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Settings created successfully', 
                'status': 'success'
            }), 202
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    def getAll(self):
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (page - 1) * limit

        search = request.args.get('search', '')
        group = request.args.get('group', '')

        query = db.session.query(Setting)
        if search:
            query = query.filter(Setting.key.ilike(f'%{search}%'))
        if group:
            query = query.filter(Setting.group == group)
        
        settings = query.order_by(Setting.updatedAt.desc()).limit(limit).offset(skip).all()
        total = query.count()
        
        return jsonify({
            'settings': [setting.toDict() for setting in settings],
            'meta': {
                'total': total,
                'totalPages': -(-total // limit),
                'currentPage': page,
                'pageSize': limit
            }
        }), 200

    def getOne(self, settingId: int):
        setting = Setting.query.filter_by(id=settingId).first()
        if not setting:
            return jsonify({
                "status": "error",
                "message": "Setting not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": setting.toDict()
        }), 200

    def update(self, settingId: int):
        setting = Setting.query.filter_by(id=settingId).first()
        if not setting:
            return jsonify({
                "status": "error",
                "message": "Setting not found"
            }), 404
        
        data = request.get_json()
        setting.value = data.get('value', setting.value)
        setting.type = data.get('type', setting.type)
        setting.group = data.get('group', setting.group)

        db.session.commit()
        return jsonify({'message': 'Setting updated successfully', 'data': setting.toDict(), 'status': 'success'}), 200

    def delete(self, settingId: int):
        setting = Setting.query.filter_by(id=settingId).first()
        if not setting:
            return jsonify({
                "status": "error",
                "message": "Setting not found"
            }), 404
        
        db.session.delete(setting)
        db.session.commit()
        return jsonify({'message': 'System deleted successfully', 'status': 'success'}), 200
