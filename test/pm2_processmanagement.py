
# <!-- Managing processes -->
# pm2 restart app_name
# pm2 reload app_name
# pm2 stop app_name
# pm2 delete app_name
# pm2 [list|ls|status]
# <!-- Setup startup script -->
# pm2 startup
# pm2 save
# Watch and Restart app when files change
# --watch
import os
import time
import json
import random
import subprocess
import sys
import json
# <!-- call file python and Rename the Process -->


def run_module_with_pm2(name):
    os.system(f'pm2 start appPM2.py --name {name}')


# <--- Read status of all processes  --->
shellscript = subprocess.Popen(["pm2", "jlist"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
print("------------------------------")
# data = json.loads(raw)status
out, err = shellscript.communicate()
result = json.loads(out)
# print(result[0]['name'])
# print(result[0]['pm2_env']['status'])
# print(result[0]['pm2_env']['pm_uptime'])

# print(result[0]['pm2_env']['namespace'])
# print(result[0]['pm2_env']['env']['unique_id'])
# print(result[0]['pm2_env']['exec_mode'])

# print(result[0]['pm2_env']['pm_id'])
# print(result[0]['monit'])

for item in range(len(result)):
    print("+++++++++++++++++++++++++++++")

    name = result[item]['name']
    namespace = result[item]['pm2_env']['namespace']
    mode = result[item]['pm2_env']['exec_mode']
    pid = result[item]['pid']
    uptime = result[item]['pm2_env']['pm_uptime']
    status = result[item]['pm2_env']['status']
    cpu = result[item]['monit']['cpu']
    mem = result[item]['monit']['memory']/1000000

    print(f'name: {name}')
    print(f'namespace: {namespace}')
    print(f'mode: {mode}')
    print(f'pid: {pid}')
    print(f'uptime: {uptime}')
    print(f'status: {status}')
    print(f'cpu: {cpu}')
    print(f'mem: {mem}')
