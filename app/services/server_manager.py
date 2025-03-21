import paramiko
from concurrent.futures import ThreadPoolExecutor

class ServerManager:
    @staticmethod
    #  attack for user only server
    def server_only(server_ip, server_username, server_password, command):
        try:
            print(server_ip)
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
    #  attack for admin multi server
    def server_multi(servers, command):
        results = []
        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            futures = [executor.submit(ServerManager.server_only, server["ip"], server["username"], server["password"], command) for server in servers]
            for future in futures:
                results.append(future.result())
        return results

    @staticmethod
    # get only proccess attack for user
    def server_get_single(server_id, server_name, server_ip, server_username, server_password):
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
                    "domain": parts[12] if len(parts) > 12 else "N/A",
                    "attack_time": parts[8] if len(parts) > 8 else "N/A",
                    "remaining_time": parts[9] if len(parts) > 9 else "N/A",
                    "concurrents": int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else 0,
                    "pid": int(parts[1]) if parts[1].isdigit() else -1,
                    "server_id": server_id,
                    "server_name": server_name,
                }
                process_list.append(process_info)

            return process_list
        except Exception as e:
            return {"message": str(e)}

    @staticmethod
     # get multi proccess attack for superadmin
    def server_get_multi(servers):
        results = []
 
        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            futures = [
                executor.submit(
                    ServerManager.server_get_single,
                    server["id"],
                    server["name"],
                    server["ip"],
                    server["username"],
                    server["password"]
                ) for server in servers
            ]
            for future in futures:
                server_result = future.result()
                if isinstance(server_result, list):
                    results.extend(server_result)
                elif isinstance(server_result, dict) and "message" in server_result:
                    print(f"Lỗi từ server: {server_result['message']}")

        return results

    @staticmethod
    # stop proccess single
    def server_stop_single(server_ip, server_username, server_password, pid=None):
        sshClient = paramiko.SSHClient()
        try:
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            command = f"kill -9 {pid}" if pid else "kill -9 -1"
            stdin, stdout, stderr = sshClient.exec_command(command)
            error_output = stderr.read().decode().strip()

            if error_output:
                return []

            return []
        except Exception as e:
            return []
        finally:
            sshClient.close()

    # @staticmethod
    # def server_stop_multi(servers):
    #     with ThreadPoolExecutor(max_workers=min(10, len(servers))) as executor:
    #         results = list(executor.map(
    #             lambda server: ServerManager.server_stop_single(
    #                 server["ip"], server["username"], server["password"], None
    #             ),
    #             servers
    #         ))

    #     return results
    # def server_stop_mulit_user

        
        