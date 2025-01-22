from flask import jsonify, request
import subprocess

class AttackController:
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
        
        command = f"xvfb-run node scam.js {domain} {time} {concurrents} {requests} proxy.txt --debug true --auth true"

        return jsonify({
            "status": "success",
            "message": f"Command '{command}' timeout after {time} seconds as expected"
        }), 200
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