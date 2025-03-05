from flask import jsonify, request
from app.db import db
from app.models.server import Server

class ServerController:
    def create(self):
        try:
            server = request.get_json()

            if not server.get('ip') and not server.get('username') and not server.get('password'):
                return jsonify({
                    'message': {
                        'ip': 'Ip is required',
                        'password': 'Password is required',
                        'username': 'Username is required'
                    }, 'status': 'error'
                }), 400

            if not server.get('ip'):
                return jsonify({
                    'message': {
                        'ip': 'Ip is required',
                    },'status': 'error'
                }), 400
            if not server.get('username'):
                return jsonify({
                    'message': {
                        'username': 'Username is required',
                    },'status': 'error'
                }), 400
            if not server.get('password'):
                return jsonify({
                    'message': {
                        'password': 'Password is required',
                    },'status': 'error'
                }), 400
            is_existed = Server.query.filter(Server.ip == server.get('ip')).first()
            if is_existed:  
                return jsonify({
                    'message': {
                        'ip': 'Ip already registered'
                    },'status': 'error'
                }), 400
            
            newServer= Server(
                ip=server.get('ip'),
                username=server.get('username'),
                name=server.get('name'),
                password=server.get('password'),
            )
            db.session.add(newServer)
            db.session.commit()
            
            return jsonify({
                'message': 'Server created successfully', 
                'status': 'success'
            }), 202
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)   
            }), 400

    def getAll(self):
        try: 
            query = db.session.query(Server)
            servers = query.order_by(Server.updatedAt.desc()).all()

            return jsonify({
                'data': [server.to_dict() for server in servers],
                'status': 'success'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        
    def update(self, serverId: int):
        try:
            server = Server.query.filter_by(id=serverId).first()
            if not server:
                return jsonify({
                    "status": "error",
                    "message": "Server not found"
                }), 404

            data = request.get_json()

            if not data.get('ip') and not data.get('username') and not data.get('password'):
                return jsonify({
                    'message': {
                        'ip': 'Ip is required',
                        'password': 'Password is required',
                        'username': 'Username is required'
                    }, 'status': 'error'
                }), 400

            if not data.get('ip'):
                return jsonify({
                    'message': {
                        'ip': 'Ip is required',
                    },'status': 'error'
                }), 400
            if not data.get('username'):
                return jsonify({
                    'message': {
                        'username': 'Username is required',
                    },'status': 'error'
                }), 400
            if not data.get('password'):
                return jsonify({
                    'message': {
                        'password': 'Password is required',
                    },'status': 'error'
                }), 400
            is_existed = Server.query.filter(Server.ip == data.get('ip'), Server.id != serverId).first()
            if is_existed:  
                return jsonify({
                    'message': {
                        'ip': 'Ip already registered'
                    },'status': 'error'
                }), 400 
            
            server.username = data.get('username', server.username)
            server.ip = data.get('ip', server.ip)
            server.password = data.get('password', server.password)
            server.name = data.get('name', server.name)
            db.session.commit()
            
            return jsonify({
                'message': 'Server created successfully', 
                'status': 'success'
            }), 202
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)   
            }), 400
        
    def delete(self, serverId):
        try:
            server = db.session.query(Server).filter_by(id=serverId).first()

            if not server:
                return jsonify({
                    "status": "error",
                    "message": "Server not found"
                }), 404
            
            db.session.delete(server)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Server deleted successfully"
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400