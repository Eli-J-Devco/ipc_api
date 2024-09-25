# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import subprocess
import sys
import time

path=os.path.dirname(__file__)+"/src/"
from src.database.sql.device import all_query as device_query
from src.database.sql.upload_channel import all_query as upload_channel_query
from src.utils.libMySQL import *
from src.utils.logger_manager import setup_logger

LOGGER = setup_logger(module_name='main')
LOGGER.warn(f'--- init ---')
# Describe functions before writing code
# /**
# 	 * @description init all driver
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */

def init_driver():
    try:
        absDirname=path
        query_all=device_query.select_all_device
        # 
        LOGGER.warn(f'query_all: {query_all}')
        results = MySQL_Select(query_all, ())
        if type(results) == list and len(results)>=1:
            pass
        else:           
            print("Error not found data device")
            LOGGER.warn("Error not found data device")
            return -1
        result_rs485_group=[]
        for item in results:
            if item['type']==0:
                # call driver ModbusTCP
                if item["connect_type"] == "Modbus/TCP":
                    # name of pid pm2=Dev|id_communication|connect_type|id|name
                    id_communication=item["id_communication"]
                    id = item["id"]
                    name = item["name"]
                    connect_type=item["connect_type"]
                    pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                    print(f'pid: {pid}')
                    if sys.platform == 'win32':
                        # use run with window
                        subprocess.Popen(
                            f'pm2 start {absDirname}/deviceDriver/ModbusTCP.py -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
                    else:
                        # use run with ubuntu/linux
                        subprocess.Popen(
                            f'sudo pm2 start {absDirname}/deviceDriver/ModbusTCP.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
                # join the same group ModbusRTU
                if item["connect_type"] == "RS485":
                    result_rs485_group.append(item)
        # Initialize the device RS485 RTU
        if len(result_rs485_group)>0:
                result_rs485_list = [x for i, x in enumerate(result_rs485_group) if x['serialport_group'] not in {y['serialport_group'] for y in result_rs485_group[:i]}]
                data=[]
                for rs485_item in result_rs485_list:
                    item=[]
                    for device_item in result_rs485_group:
                            if rs485_item["serialport_group"]==device_item["serialport_group"]:
                                    item.append({
                                            'id_communication':device_item['id_communication'],            
                                            'id':device_item['id'],
                                            'name':device_item['name'],
                                           
                                            'connect_type':device_item['connect_type'],                            
                                            'serialport_group':rs485_item['serialport_group'],
                                            'serialport_name':rs485_item['serialport_name'],
                                            'serialport_baud':int(rs485_item['serialport_baud']),
                                            'serialport_stopbits':int(rs485_item['serialport_stopbits']),
                                            # Get the first character of the first string
                                            'serialport_parity':rs485_item['serialport_parity'][0],
                                            # ----- End -----
                                            'serialport_timeout':int(rs485_item['serialport_timeout']),
                                            'serialport_debug_level':rs485_item['serialport_debug_level']
                                        })
                    data.append(item)
                for item in data:                                                 
                    # name of pid pm2=Dev|id_communication|connect_type|serialport_name
                    id=item[0]["id_communication"]
                    id_communication=item[0]["id_communication"]
                    serialport_group=item[0]["serialport_group"]
                    serialport_name=item[0]["serialport_name"]
                    connect_type=item[0]["connect_type"]
                    pid = f'Dev|{id_communication}|{connect_type}|{serialport_group}'
                    
                    print(f'pid: {pid}') 
                    if id_communication !=-1:
                    
                        if sys.platform == 'win32':
                            # use run with window
                            subprocess.Popen(
                                f'pm2 start {absDirname}/deviceDriver/ModbusRTU.py -f  --name "{pid}" -- "{id}"  --restart-delay=10000', shell=True).communicate()
                        else:
                            # use run with ubuntu/linux
                            subprocess.Popen(
                                f'sudo pm2 start {absDirname}/deviceDriver/ModbusRTU.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
                        
    except Exception as e:
        print('Error init driver: ',e)
        LOGGER.error(f'{e}')
# Describe functions before writing code
# /**
# 	 * @description init create log file
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_log_file():
    try:
        absDirname=path
        query_all=upload_channel_query.select_all_upload_channel.format(status=1)
        results = MySQL_Select(query_all, ())
        for item in results:
            id = item["id"]
            name = item["name"]
            type_protocol= item["type_protocol"]
            pid = f'LogFile|{id}|{name}|{type_protocol}'
            if item["enable"]==1:
                if sys.platform == 'win32':
                    subprocess.Popen(
                            f'pm2 start {absDirname}/dataLog/file/file_controler.py -f  --name "{pid}" -- {id}  --restart-delay 10000', shell=True).communicate()
                else:
                    subprocess.Popen(
                            f'sudo pm2 start {absDirname}/dataLog/file/file_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
    except Exception as e:
        print('Error init_log_file: ',e)
        LOGGER.error(f'{e}')
# Describe functions before writing code
# /**
# 	 * @description init sync file
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_sync_file():
    try:
        absDirname=path
        query_all=upload_channel_query.select_all_upload_channel.format(status=1)
        results = MySQL_Select(query_all, ())
        for item in results:
            id = item["id"]
            name = item["name"]
            type_protocol= item["type_protocol"]
            pid = f'SyncData|{id}|{name}|{type_protocol}'
            if item["enable"]==1:
                if sys.platform == 'win32':
                    subprocess.Popen(
                            f'pm2 start {absDirname}/dataSync/sync_controler.py -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
                else:
                    subprocess.Popen(
                            f'sudo pm2 start {absDirname}/dataSync/sync_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
    except Exception as e:
        print('Error init_sync_file: ',e)
        LOGGER.error(f'{e}')
# Describe functions before writing code
# /**
# 	 * @description init log data
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_log_data():
    try:
        absDirname=path
        pid = f'LogDevice'
        if sys.platform == 'win32':
            subprocess.Popen(
                            f'pm2 start {absDirname}/dataLog/device/device_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
        else:
            subprocess.Popen(
                        f'sudo pm2 start {absDirname}/dataLog/device/device_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    except Exception as e:
        print('Error init_log_data: ',e)
        LOGGER.error(f'{e}')
# Describe functions before writing code
# /**
# 	 * @description enable permission folder config network ubuntu ipc
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def enable_permission_ipc():
    from subprocess import PIPE, run

    # cmd = "echo 123654789 | sudo nano /etc/network/interfaces"
    cmd = "echo 123654789 | sudo chmod -R 777 /etc/netplan"
    out = run(cmd, shell=True, stdout=PIPE)
# Describe functions before writing code
# /**
# 	 * @description delete all app in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def delete_all_app_pm2():
    if sys.platform == 'win32':
        subprocess.Popen(f'pm2 delete all', shell=True).communicate()
    else:
        subprocess.Popen(f'sudo pm2 delete all', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run API of web
# 	 * @author vnguyen
# 	 * @since 24-01-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_api_web():
    absDirname=path
    pid=f'API'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/api/main.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/api/main.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run api gateway
# 	 * @author vnguyen
# 	 * @since 26-03-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_api_gateway():
    absDirname=path
    pid=f'APIGateway'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/apiGateway/main.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/apiGateway/main.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_setup_site():
    absDirname=path
    pid=f'SetupSite'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/setupSite/setup_site_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/setupSite/setup_site_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_process_system():
    absDirname=path
    pid=f'ProcessSystem'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/processSystem/process_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/processSystem/process_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_mode_system():
    absDirname=path
    pid=f'ModeSystem'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/modeSystem/mode_system_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/modeSystem/mode_system_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_mode_control():
    absDirname=path
    pid=f'ModeControl'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/modeControl/mode_control_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/modeControl/mode_control_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_energy_monitor():
    absDirname=path
    pid=f'EnergyMonitor'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/energyMonitor/energy_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/energyMonitor/energy_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run mqtt control
# 	 * @author vnguyen
# 	 * @since 05-04-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_caculator_control():
    absDirname=path
    pid=f'CalculatorControl'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/deviceControl/caculatorControl/caculator_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/deviceControl/caculatorControl/caculator_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run API_NEW of web
# 	 * @author vnguyen
# 	 * @since 13-05-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_api_web_v2():
    absDirname=path
    pid=f'API'
    if sys.platform == 'win32':
        # use run with window          
        print("init_api_web_v2 run only linux")
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo /usr/bin/python3 /sources/python/api_python_v2/setup.py', shell=True).communicate()
        
# Describe functions before writing code
# /**
# 	 * @description run INIT_DEVICE_SERVICE
# 	 * @author nhan.tran
# 	 * @since 14-05-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_device_service():
    if sys.platform == 'win32':
        # use run with window          
        print("init_api_web_v2 run only linux")
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo /usr/bin/python3 /sources/python/services/setup.py', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description run create virtual device
# 	 * @author vnguyen
# 	 * @since 13-06-2024
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_virtual_device():
    try:
        absDirname=path
        pid="VirtualDevice"
        if sys.platform == 'win32':
            # use run with window          
            print("init_virtual_device run only linux")
        else:
            # use run with ubuntu/linux
            subprocess.Popen(
                f'sudo pm2 start {absDirname}/deviceDriver/virtualDevice/virtual_device.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    except Exception as e:
        print('Error init driver: ',e)
        LOGGER.error(f'{e}')
def init_get_cpuinfor():
    absDirname=path
    pid=f'CPUInformation'
    if sys.platform == 'win32':
        # use run with window          
        subprocess.Popen(
            f'pm2 start {absDirname}/cpu/cpu_controler.py -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/cpu/cpu_controler.py --interpreter /usr/bin/python3 -f  --name "{pid}"  --restart-delay=10000', shell=True).communicate()
time.sleep(10)        
delete_all_app_pm2()
# init_api_web()
init_api_gateway()
init_setup_site()
init_driver()
init_log_file()
init_sync_file()
init_log_data()
init_api_web_v2()
init_device_service()
init_virtual_device()
init_get_cpuinfor()
init_process_system()
init_mode_system()
init_mode_control()
init_energy_monitor()
init_caculator_control()
