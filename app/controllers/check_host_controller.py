from flask import jsonify, request

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

        return jsonify({
            "status": "success",
            "data": {
                "vietnam": True,
                "thailand": True,
            }
        }), 200
