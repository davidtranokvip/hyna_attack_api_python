import paramiko
from concurrent.futures import ThreadPoolExecutor

class ServerManager:

    #  attack for user only server
    @staticmethod
    def server_only(server_ip, server_username, server_password, command):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            # sshClient.exec_command("pkill -9 xvfb-run; pkill -9 Xvfb")
            # sshClient.exec_command("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
            # sshClient.exec_command(command)

            stdin, stdout, stderr = sshClient.exec_command("pkill -9 xvfb-run; pkill -9 Xvfb")
            stdout.read()  # Đợi lệnh hoàn thành
            # mở full luồng cpu
            stdin, stdout, stderr = sshClient.exec_command("echo performance | sudo -S tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
            if "password for" in stderr.read().decode():
                stdin.write(server_password + "\n")
                stdin.flush()
            stdout.read()

            stdin, stdout, stderr = sshClient.exec_command(command)
            sshClient.close()

            return {"server": server_ip, "status": "success", "message": "Command executed successfully"}
        except Exception as e:
            return {"server": server_ip, "status": "error", "message": str(e)}

    #  attack for admin multi server
    @staticmethod
    def server_multi(servers, command):
        results = []
        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            futures = [executor.submit(ServerManager.server_only, server["ip"], server["username"], server["password"], command) for server in servers]
            for future in futures:
                results.append(future.result())
        return results
    
    # get server attack single
    @staticmethod
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
                    "attack_time": parts[13] if len(parts) > 13 else "N/A",
                    "remaining_time": parts[9] if len(parts) > 9 else "N/A",
                    "concurrents": int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else 0,
                    "pid": int(parts[1]) if parts[1].isdigit() else -1,
                    "server_id": server_id,
                    "server_name": server_name,
                }
                process_list.append(process_info)

            return process_list
        except Exception as e:
            return str(e)
    
    # get server attack multi
    @staticmethod
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
    
    # stop multi pids attack
    @staticmethod
    def server_stop_multi(server_ip, server_username, server_password, pids):
        sshClient = paramiko.SSHClient()
        try:
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(server_ip, username=server_username, password=server_password)

            if not pids:
                return []
                
            pids_str = " ".join(str(pid) for pid in pids)
            command = f"kill -9 {pids_str}"
            
            stdin, stdout, stderr = sshClient.exec_command(command)
            error_output = stderr.read().decode().strip()

            if error_output:
                return {"status": "error", "message": error_output}

            return {"status": "success", "message": f"Terminated processes: {pids_str}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            sshClient.close()

    # def server_get_single(server_id, server_name, server_ip, server_username, server_password):
    #     try:
    #         sshClient = paramiko.SSHClient()
    #         sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         sshClient.connect(server_ip, username=server_username, password=server_password)

    #         # Lệnh để lấy các tiến trình [h]yna.js, ./phimsex, ./vkl, hoặc xvfb-run node
    #         cmd = (
    #         "ps aux | grep -E '(node.*hyna.js|\./phimsex|\./vkl)' | "
    #         "grep -v 'xvfb-run.*node' | grep -v 'grep'"
    #         )
    #         stdin, stdout, stderr = sshClient.exec_command(cmd)
    #         raw_process_list = stdout.read().decode().strip().split("\n")
    #         sshClient.close()
    #         # print(raw_process_list)
    #         process_list = []
    #         for process in raw_process_list:
    #             if not process.strip():  # Bỏ qua dòng trống
    #                 continue
    #             parts = process.split(maxsplit=15)  # Chia nhỏ dòng thành các phần
    #             if len(parts) < 11:  # Đảm bảo dòng có đủ thông tin
    #                 continue

    #             # Phân tích thông tin từ lệnh
    #             command_str = " ".join(parts[10:])  # Lấy toàn bộ phần lệnh
    #             process_info = {
    #                 "domain": "N/A",
    #                 "attack_time": parts[8] if len(parts) > 8 else "N/A",
    #                 "remaining_time": parts[9] if len(parts) > 9 else "N/A",
    #                 "concurrents": 0,  # Mặc định là 0, sẽ cập nhật sau nếu tìm thấy
    #                 "pid": int(parts[1]) if parts[1].isdigit() else -1,
    #                 "server_id": server_id,
    #                 "server_name": server_name,
    #                 "command": command_str  # Lưu toàn bộ lệnh để debug hoặc phân tích thêm
    #             }

    #             # Phân tích domain và concurrents dựa trên định dạng lệnh
    #             args = command_str.split()
    #             if "hyna.js" in command_str:
    #                 process_info["domain"] = parts[12] if len(parts) > 12 else "N/A"
    #                 process_info["concurrents"] = int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else 0
    #             elif "./phimsex" in command_str or "./vkl" in command_str:
    #                 for i, arg in enumerate(args):
    #                     if arg == "-u" and i + 1 < len(args):
    #                         process_info["domain"] = args[i + 1]
    #                     if arg == "-t" and i + 1 < len(args) and args[i + 1].isdigit():
    #                         process_info["concurrents"] = int(args[i + 1])

    #             process_list.append(process_info)

    #         return process_list

    #     except Exception as e:
    #         return {"message": str(e)}
