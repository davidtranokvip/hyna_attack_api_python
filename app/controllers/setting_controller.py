from flask import jsonify, request
from app.models.setting import Setting
from app.db import db

class SettingController:
    def create(self):
        data = request.get_json()
        
        newSetting = Setting(
            key=data['key'],
            value=data['value'],
            group=data['group']
        )
        
        db.session.add(newSetting)
        db.session.commit()
        
        return jsonify({'message': 'Setting created successfully', 'data': newSetting.toDict()}), 201

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
        setting.key = data.get('key', setting.key)
        setting.value = data.get('value', setting.value)
        setting.group = data.get('group', setting.group)

        db.session.commit()
        return jsonify({'message': 'Setting updated successfully', 'data': setting.toDict()}), 200

    def delete(self, settingId: int):
        setting = Setting.query.filter_by(id=settingId).first()
        if not setting:
            return jsonify({
                "status": "error",
                "message": "Setting not found"
            }), 404
        
        db.session.delete(setting)
        db.session.commit()
        return jsonify({'message': 'Setting deleted successfully'}), 200
