from flask import jsonify, request
import requests
import time
from urllib.parse import urlparse

class CheckHostController:
    def checkHost(self):
        data = request.get_json()
        url = data.get('url')

        # Validate URL is not empty
        if not url:
            return jsonify({
                "status": "error",
                "message": "URL cannot be empty"
            }), 400

        # Validate URL scheme
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                "status": "error", 
                "message": "URL must start with http:// or https://"
            }), 400

        try:
            # Extract hostname from URL
            hostname = urlparse(url).netloc

            # Initialize check on check-host.net
            initResponse = requests.get(
                f'https://check-host.net/check-http?host={hostname}&max_nodes=4&node=vn1.node.check-host.net',
                headers={'Accept': 'application/json'}
            )
           
            if initResponse.status_code != 200:
                return jsonify({
                    "status": "error",
                    "message": "Failed to initialize host check"
                }), 500

            requestId = initResponse.json().get('request_id')
            
            # Wait for results (usually takes a few seconds)
            time.sleep(3)

            # Get results
            resultResponse = requests.get(
                f'https://check-host.net/check-result/{requestId}',
                headers={'Accept': 'application/json'}
            )

            if resultResponse.status_code != 200:
                return jsonify({
                    "status": "error",
                    "message": "Failed to get check results"
                }), 500

            results = resultResponse.json()
            # Process results for Vietnam and Thailand
            vietnamAvailable = False
            thailandAvailable = False

            for server, checks in results.items():
                if 'vn1.node.check-host.net' in server:
                    vietnamAvailable = checks and checks[0] and checks[0][0] == 1
                elif 'Thailand' in server:
                    thailandAvailable = checks and checks[0] and checks[0][0] == 1

            return jsonify({
                "status": "success",
                "data": {
                    "vietnam": vietnamAvailable,
                    "thailand": thailandAvailable
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
