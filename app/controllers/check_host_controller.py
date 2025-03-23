from flask import jsonify, request
import requests
import time
from urllib.parse import urlparse
from app.services.response import Response

class CheckHostController:
    def get_list(self):
        data = request.get_json()

        if not data or "host" not in data:
            return Response.error("Missing 'host' parameter in JSON.", code=400)

        host = data["host"]
        max_nodes = data.get("max_nodes")

        check_url = "https://check-host.net/check-http"
        payload = {"host": host, **({"max_nodes": max_nodes} if max_nodes else {})}
        headers = {"Accept": "application/json"}

        response = requests.post(check_url, data=payload, headers=headers)
        if response.status_code != 200:
            return Response.error("Unable to send check request.", code=401)

        response_data = response.json()
        request_id = response_data.get("request_id")
        if not request_id:
            return Response.error("Did not receive request_id.", code=401)

        time.sleep(5)

        result_url = f"https://check-host.net/check-result/{request_id}"
        result_response = requests.post(result_url, headers=headers)
        if result_response.status_code != 200:
            return Response.error("Unable to retrieve check results.", code=401)

        result_data = result_response.json()

        http_data = {
            node: {
                "country": details[1],
                "capital_city": details[2],
                "ip": details[3]
            }
            for node, details in response_data.get("nodes", {}).items()
        }

        result_list = {
            node: {
                "statusCode": str(details[0][3]) if str(details[0][3]) == "200" else None,
                "statusText": details[0][2] if details[0][2] == "OK" else None,
                "ip": details[0][4]
            }
            for node, details in result_data.items() if details
        }

        merged_data = []
        for node, http_info in http_data.items():
            if node in result_list:
                merged_data.append({
                    "node": node,
                    "country": http_info["country"],
                    "capital_city": http_info["capital_city"],
                    "ip_http": http_info["ip"],
                    "ip_result": result_list[node]["ip"],
                    "statusCode": result_list[node]["statusCode"],
                    "statusText": result_list[node]["statusText"]
                })

        return Response.success(data=merged_data)