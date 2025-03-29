from app.services.response import Response
from flask import request
import requests
import time

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
        result_list = {}
        for node, details in result_data.items():
            if node == "nodes":
                continue
            
            try:
                if details and isinstance(details, list) and len(details) > 0:
                    first_detail = details[0]
                    
                    if first_detail and isinstance(first_detail, list):
                        status_code = None
                        if len(first_detail) > 3 and first_detail[3] is not None:
                            status_code = str(first_detail[3]) if str(first_detail[3]) == "200" else None
                        
                        status_text = None
                        if len(first_detail) > 2 and first_detail[2] is not None:
                            status_text = first_detail[2] if first_detail[2] == "OK" else None
                        
                        ip = None
                        if len(first_detail) > 4 and first_detail[4] is not None:
                            ip = first_detail[4]
                        
                        result_list[node] = {
                            "statusCode": status_code,
                            "statusText": status_text,
                            "ip": ip
                        }
            except Exception as e:
                print(f"Error processing node {node}: {str(e)}")
                continue
            
        merged_data = []
        for node, http_info in http_data.items():
            if node in result_list:
                merged_data.append({
                    "country": http_info["country"],
                    "capital_city": http_info["capital_city"],
                    "ip_http": http_info["ip"],
                    "ip_result": result_list[node]["ip"],
                    "statusCode": result_list[node]["statusCode"],
                    "statusText": result_list[node]["statusText"]
                })

        return Response.success(data=merged_data)