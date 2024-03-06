# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import pathlib
import subprocess
import sys
import time
from pathlib import Path
from shlex import split
from subprocess import Popen, run

import mybatis_mapper2sql
import pandas as pd
from pydantic_settings import VERSION, BaseSettings, SettingsConfigDict

# absDirname=os.path.dirname(os.path.abspath(__file__))
# path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")+"/"
# sys.path.append(path)
path=os.path.dirname(__file__)+"/src/"
from src.utils.libMySQL import *

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
        # load file sql from mybatis
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
            xml= absDirname + 'mybatis/device_list.xml')

        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True)
        # 
        if type(statement) == list and len(statement)>2 and 'select_all_device' not in statement:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        query_all = statement[0]["select_all_device"]
        # 
        results = MySQL_Select(query_all, ())
        if type(results) == list and len(results)>=1:
            pass
        else:           
            print("Error not found data device")
            return -1
        result_rs485_group=[]
        for item in results:
        
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
# Describe functions before writing code
# /**
# 	 * @description init create log file
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
def init_log_file():
        absDirname=path
        # load file sql from mybatis
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
            xml= absDirname + '/mybatis/settup.xml')

        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True)
        
        if type(statement) == list and len(statement)>1 and 'select_upload_channel' not in statement:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        query_all = statement[1]["select_upload_channel"]
        results = MySQL_Select(query_all, ())
        # print(f'results: {results}')
        for item in results:
            
            id = item["id"]
            name = item["name"]
            type_protocol= item["type_protocol"]
            pid = f'LogFile|{id}|{name}|{type_protocol}'
            # if sys.platform == 'win32':
            #     subprocess.Popen(
            #             f'pm2 start {absDirname}/create_logfile/log_file.py -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
            if sys.platform == 'win32':
                subprocess.Popen(
                        f'pm2 start {absDirname}/dataLog/file.py -f  --name "{pid}" -- {id}  --restart-delay 10000', shell=True).communicate()
            else:
                subprocess.Popen(
                        f'sudo pm2 start {absDirname}/dataLog/file.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()

def init_sync_file():
        absDirname=path
        # load file sql from mybatis
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
            xml= absDirname + '/mybatis/settup.xml')

        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True)
        
        if type(statement) == list and len(statement)>1 and 'select_upload_channel' not in statement:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        query_all = statement[1]["select_upload_channel"]
        print(f'query_all: {query_all}')
        results = MySQL_Select(query_all, ())
        # print(f'results: {results}')
        for item in results:
            id = item["id"]
            name = item["name"]
            type_protocol= item["type_protocol"]
            pid = f'UpData|{id}|{name}|{type_protocol}'
            if sys.platform == 'win32':
                subprocess.Popen(
                            f'pm2 start {absDirname}/dataSync/url.py -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
            else:
                subprocess.Popen(
                        f'sudo pm2 start {absDirname}/dataSync/url.py --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()

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
        os.system(f'pm2 delete all')
    else:
        os.system(f'sudo pm2 delete all')
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
delete_all_app_pm2()
init_driver()
# init_log_file()
# init_sync_file()
init_api_web()


