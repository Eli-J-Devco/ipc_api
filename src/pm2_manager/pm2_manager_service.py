

import json
import os
import subprocess
import sys


class Pm2ManagerService:
    def __init__(self,
                **kwargs):
        pass
    async def restart_program_pm2_many(app_name=[]):
        status=None
        try:
            print(f"List app pm2: {app_name}")
            cmd_list = ""
            if sys.platform == "win32":
                cmd_list = "pm2 jlist"
            else:
                cmd_list = "sudo pm2 jlist"
            shellscript = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
            )

            out, err = shellscript.communicate()
            result = json.loads(out)
            app_detect = 0
            pid_list = []
            # print(f"result: {result}")
            for item in result:
                name = item["name"]
                for item_app in app_name:
                    if name.find(item_app) == 0:
                        pid = item["pm_id"]
                        pid_list.append(pid)
            print(f"List id app pm2: {pid_list}")
            cmd_pm2 = ""
            if sys.platform == "win32":
                cmd_pm2 = f"pm2 restart "
            else:
                cmd_pm2 = f"sudo pm2 restart "
            join_pid = ""
            if pid_list:
                for item in pid_list:
                    join_pid = join_pid + " " + str(item)
                cmd_pm2 = cmd_pm2 + join_pid
                print(f"cmd_pm2: {cmd_pm2}")
                os.system(f"{cmd_pm2}")
                app_detect = 1
            if app_detect == 1:
                status= 0
            else:
                status= 1
        except Exception as err:
            print("Error restart pm2 : ", err)
            status=2
        finally:
            return status