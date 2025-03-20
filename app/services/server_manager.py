import paramiko
from concurrent.futures import ThreadPoolExecutor

class ServerManager:
    @staticmethod
    def server_only(server_ip, server_username, server_password, command):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            sshClient.exec_command("pkill -9 xvfb-run; pkill -9 Xvfb")
            sshClient.exec_command(command)
            sshClient.close()

            return {"server": server_ip, "status": "success", "message": "Command executed successfully"}
        except Exception as e:
            return {"server": server_ip, "status": "error", "message": str(e)}

    @staticmethod
    def server_multi(servers, command):
        results = []
        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            futures = [executor.submit(ServerManager.server_only, server["ip"], server["username"], server["password"], command) for server in servers]
            for future in futures:
                results.append(future.result())
        return results

    @staticmethod
    def server_get_single(server_ip, server_username, server_password):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            stdin, stdout, stderr = sshClient.exec_command("ps aux | grep '[h]yna.js' | grep -v 'xvfb'")
            raw_process_list = stdout.read().decode().strip().split("\n")
            sshClient.close()

            process_list = []
            for process in raw_process_list:
                parts = process.split(maxsplit=15)
                if len(parts) < 11:
                    continue

                process_info = {
                    "origin_data": process,
                    "domain": parts[12] if len(parts) > 12 else "N/A",
                    "attack_time": parts[8] if len(parts) > 8 else "N/A",
                    "remaining_time": parts[9] if len(parts) > 9 else "N/A",
                    "concurrents": int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else 0,
                    "pid": int(parts[1]) if parts[1].isdigit() else -1,
                    "server_ip": server_ip
                }
                process_list.append(process_info)

            return {"server": server_ip, "status": "success", "processes": process_list}
        except Exception as e:
            return {"server": server_ip, "status": "error", "message": str(e)}

    @staticmethod
    def server_get_multi(servers):
        results = []

        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            futures = [
                executor.submit(
                    ServerManager.server_get_single,
                    server["ip"],
                    server["username"],
                    server["password"]
                ) for server in servers
            ]

            for future in futures:
                server_result = future.result()
                if "processes" in server_result and isinstance(server_result["processes"], list):
                    results.extend(server_result["processes"])

        return results

    @staticmethod
    def server_stop_single(server_ip, server_username, server_password, pid=None):
        sshClient = paramiko.SSHClient()
        try:
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            command = f"kill -9 {pid}" if pid else "kill -9 -1"
            stdin, stdout, stderr = sshClient.exec_command(command)
            error_output = stderr.read().decode().strip()

            if error_output:
                return {"server": server_ip, "status": "error", "message": error_output}

            return {"server": server_ip, "status": "success", "message": f"Stopped {'PID ' + str(pid) if pid else 'all user processes'}"}
        except Exception as e:
            return {"server": server_ip, "status": "error", "message": str(e)}
        finally:
            sshClient.close()

    @staticmethod
    def server_stop_multi(servers):
        with ThreadPoolExecutor(max_workers=min(10, len(servers))) as executor:
            results = list(executor.map(
                lambda server: ServerManager.server_stop_single(
                    server["ip"], server["username"], server["password"], None
                ),
                servers
            ))

        return results

        
        