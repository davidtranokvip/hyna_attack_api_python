from app.services.response import Response
from app.models.server import Server
from app.models.team import Team
from flask import request
from app.db import db

class ServerController:
    def create(self):
        try:
            server = request.get_json()

            if not server.get('ip') and not server.get('username') and not server.get('password'):
                return Response.error({
                    'ip': 'Ip is required',
                    'password': 'Password is required',
                    'username': 'Username is required',
                    'thread': 'Thread is required',
                }, code=400)

            if not server.get('thread'):
                return Response.error({
                    'thread': 'Thread is required'
                }, code=400)
            
            if not server.get('ip'):
                return Response.error({
                    'ip': 'Ip is required'
                }, code=400)
            
            if not server.get('username'):
                return Response.error({
                    'username': 'Username is required',
                }, code=400)
            
            if not server.get('password'):
                return Response.error({
                    'password': 'Password is required',
                }, code=400)
            
            is_existed = Server.query.filter(Server.ip == server.get('ip')).first()
            if is_existed:  
                return Response.error({
                    'ip': 'Ip already registered'
                }, code=400)
            
            newServer= Server(
                ip=server.get('ip'),
                username=server.get('username'),
                name=server.get('name'),
                password=server.get('password'),
                thread=server.get('thread'),
            )
            db.session.add(newServer)
            db.session.commit()
            return Response.success(data=[], message="Created Server Success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)

    def getAll(self):
        try:
            query = db.session.query(Server)
            servers = query.order_by(Server.updatedAt.desc()).all()
                
            result = [server.to_dict() for server in servers]

            return Response.success(data=result, message="Get Servers Success")

        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def getServersForTeam(self):
        try:
            
            team_id = request.args.get('team_id')
            if not team_id:
                 return Response.error('Team ID is required', code=400)
            
            query = db.session.query(Team).filter(Team.id == team_id).first()
            server_ids = query.servers
        
            servers = db.session.query(Server).filter(Server.id.in_(server_ids)).all()
            
            result = [server.to_dict() for server in servers]
            return Response.success(data=result, message="Get Servers Team Success")

        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def update(self, serverId: int):
        try:
            server = Server.query.filter_by(id=serverId).first()
            if not server:
                return Response.error('Server Not found', code=404)

            data = request.get_json()

            if not data.get('ip') and not data.get('username') and not data.get('password') and not data.get('thread'):
                return Response.error({
                    'ip': 'Ip is required',
                    'password': 'Password is required',
                    'username': 'Username is required',
                    'thread': 'Thread is required',
                }, code=400)

            if not data.get('ip'):
                return Response.error({
                    'ip': 'Ip is required'
                }, code=400)
            
            if not data.get('thread'):
                return Response.error({
                    'thread': 'Thread is required'
                }, code=400)
            
            if not data.get('username'):
                return Response.error({
                    'username': 'Username is required',
                }, code=400)
        
            if not data.get('password'):
                return Response.error({
                    'password': 'Password is required',
                }, code=400)
            
            is_existed = Server.query.filter(Server.ip == data.get('ip'), Server.id != serverId).first()
            if is_existed:  
                return Response.error({
                    'ip': 'Ip already registered'
                }, code=400)
            
            server.username = data.get('username', server.username)
            server.ip = data.get('ip', server.ip)
            server.password = data.get('password', server.password)
            server.name = data.get('name', server.name)
            server.thread = data.get('thread', server.thread)
            db.session.commit()
            return Response.success(data=[], message="Updated Server Success")
            
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def delete(self, serverId):
        try:
            server = db.session.query(Server).filter_by(id=serverId).first()

            if not server:
                return Response.error('Server not found', code=400)
            
            db.session.delete(server)
            db.session.commit()
            return Response.success(data=[], message="Server Deleted Success")
 
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)