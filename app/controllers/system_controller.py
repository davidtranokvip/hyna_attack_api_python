from flask import jsonify, request
from app.models.system import System
from app.db import db
from typing import Dict, Any

class SystemController:
    def create(self):
        currentUser = request.currentUser
        data = request.get_json()
        
        newSystem = System(
            name=data['name'],
            status=data.get('status', True),
            createdBy=currentUser['id'],
            updatedBy=currentUser['id']
        )
        
        db.session.add(newSystem)
        db.session.commit()
        
        return jsonify({'message': 'System created successfully', 'data': newSystem.toDict()}), 201

    def getAll(self):
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (int(page) - 1) * int(limit)

        search = request.args.get('search', '')
        status = request.args.get('status', '')

        query = db.session.query(System)
        if search:
            query = query.filter(System.name.ilike(f'%{search}%'))
        if status:
            # Convert status string to boolean
            statusBool = status.lower() == 'true'
            query = query.filter(System.status == statusBool)
        
        systems = query.order_by(System.updatedAt.desc()).limit(limit).offset(skip).all()
        total = query.count()
        return jsonify({
            'systems': [system.toDict() for system in systems],
            'meta': {
                'total': total,
                'totalPages': -(-total // int(limit)),
                'currentPage': page,
                'pageSize': limit
            }
        }), 200
        
    def getOne(self, systemId: int):
        system = System.query.filter_by(id=systemId).first()
        if not system:
            return jsonify({
                "status": "error",
                "message": "System not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": system.toDict()
        }), 200

    def update(self, systemId: int):
        currentUser = request.currentUser
        system = System.query.filter_by(id=systemId).first()
        if not system:
            return jsonify({
                "status": "error",
                "message": "System not found"
            }), 404
        
        data = request.get_json()
        system.name = data.get('name', system.name)
        system.status = data.get('status', system.status)
        system.updatedBy = currentUser['id']

        db.session.commit()
        return jsonify({'message': 'System updated successfully', 'data': system.toDict()}), 200

    def delete(self, systemId: int):
        system = System.query.filter_by(id=systemId).first()
        if not system:
            return jsonify({
                "status": "error",
                "message": "System not found"
            }), 404
        
        db.session.delete(system)
        db.session.commit()
        return jsonify({'message': 'System deleted successfully', 'status': 'success'}), 200
