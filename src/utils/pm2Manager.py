# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import mybatis_mapper2sql
from passlib.context import CryptContext
# from database import get_db
# from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
#                      Response, status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from api.domain.template import models as template_models
from api.domain.uploadChannel import models as uploadChannel_models


# Describe functions before writing code
# /**
# 	 * @description restart app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data ()
# 	 */
async def restart_program_pm2(app_name):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        app_detect=0
        for item in result:
            name = item['name']                   
            if name.find(app_name)==0:
                if sys.platform == 'win32':
                    os.system(f'pm2 restart "{name}"')
                else:
                    os.system(f'sudo pm2 restart "{name}"')
                app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error restart pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description restart many app running in pm2
# 	 * @author vnguyen
# 	 * @since 08-01-2023
# 	 * @param {list app_name of pm2}
# 	 * @return data ()
# 	 */
async def restart_program_pm2_many( app_name=[]):
    try:
        print(f'List app pm2: {app_name}')
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        app_detect=0
        pid_list=[]
        for item in result:
            name = item['name']
            for item_app in app_name:
                if name.find(item_app)==0:
                    pid= item['pm_id']
                    pid_list.append(pid)
        print(f'List Id app pm2: {pid_list}')
        cmd_pm2=""
        if sys.platform == 'win32':
            cmd_pm2=f'pm2 restart '
        else:
            cmd_pm2=f'sudo pm2 restart '
        join_pid=""
        if pid_list:
            for item in pid_list:
                join_pid=join_pid+ " " +str(item)
            cmd_pm2= cmd_pm2 +join_pid
            print(f'cmd_pm2: {cmd_pm2}')
            os.system(f'{cmd_pm2}')
            app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error restart pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description stop many app running in pm2
# 	 * @author vnguyen
# 	 * @since 07-03-2024
# 	 * @param {list app_name of pm2}
# 	 * @return data ()
# 	 */
async def stop_program_pm2_many(app_name):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        app_detect=0
        pid_list=[]
        for item in result:
            name = item['name']
            for item_app in app_name:
                if name.find(item_app)==0:
                    pid= item['pm_id']
                    pid_list.append(pid)
        print(f'list {pid_list}')
        cmd_pm2=""
        if sys.platform == 'win32':
            cmd_pm2=f'pm2 stop '
        else:
            cmd_pm2=f'sudo pm2 stop '
        join_pid=""
        if pid_list:
            for item in pid_list:
                join_pid=join_pid+ " " +str(item)
            cmd_pm2= cmd_pm2 +join_pid
            print(f'cmd_pm2: {cmd_pm2}')
            os.system(f'{cmd_pm2}')
            app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error stop pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description delete app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
async def delete_program_pm2(app_name):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        # print("----- pm2 list ----- ")
        app_detect=0
        for item in result:
            name = item['name']
            # namespace = item['pm2_env']['namespace']
            # mode = item['pm2_env']['exec_mode']
            # pid = item['pid']
            # uptime = item['pm2_env']['pm_uptime']
            # status = item['pm2_env']['status']
            # cpu = item['monit']['cpu']
            # mem = item['monit']['memory'] / 1000000
            # print(f'namespace: {namespace}')
            # print(f'mode: {mode}')
            # print(f'pid: {pid}')
            # print(f'uptime: {uptime}')
            # print(f'status: {status}')
            # print(f'cpu: {cpu}')
            # print(f'mem: {mem}')
            # print(f'name: {name}')
            # app_name=f'Dev|{str(id)}|'
                    
            if name.find(app_name)==0:
                # print(f'Find channel RS485: {name}')
                # os.system(f'sudo pm2 delete "{name}"')
                if sys.platform == 'win32':
                    os.system(f'pm2 delete "{name}"')
                else:
                    os.system(f'sudo pm2 delete "{name}"')
                
                app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error delete pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description stop app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
async def stop_program_pm2(app_name):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        # print("----- pm2 list ----- ")
        app_detect=0
        for item in result:
            name = item['name']
            namespace = item['pm2_env']['namespace']
            mode = item['pm2_env']['exec_mode']
            pid = item['pid']
            uptime = item['pm2_env']['pm_uptime']
            status = item['pm2_env']['status']
            cpu = item['monit']['cpu']
            mem = item['monit']['memory'] / 1000000
            # print(f'namespace: {namespace}')
            # print(f'mode: {mode}')
            # print(f'pid: {pid}')
            # print(f'uptime: {uptime}')
            # print(f'status: {status}')
            # print(f'cpu: {cpu}')
            # print(f'mem: {mem}')
            # print(f'name: {name}')
            # app_name=f'Dev|{str(id)}|'
                    
            if name.find(app_name)==0:
                # print(f'Find channel RS485: {name}')
                # os.system(f'sudo pm2 stop "{name}"')
                if sys.platform == 'win32':
                    os.system(f'pm2 stop "{name}"')
                else:
                    os.system(f'sudo pm2 stop "{name}"')
                app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error stop pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description stop app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
async def create_program_pm2(filename,pid,id):
    try:
        if sys.platform == 'win32':
            # use run with window      
            subprocess.Popen(
            f'pm2 start {filename} -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
            return 100
        else:               
            subprocess.Popen(
            f'sudo pm2 start {filename} --interpreter /usr/bin/python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
            return 100
    except Exception as e:
        print('Error init driver: ',e)
        return 300
# Describe functions before writing code
# /**
# 	 * @description init app in pm2
# 	 * @author vnguyen
# 	 * @since 03-12-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
async def create_device_group_rs485_run_pm2(absDirname,result_rs485_group):
    try:
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
# 	 * @description find app running in pm2
# 	 * @author vnguyen
# 	 * @since 06-12-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
async def find_program_pm2(app_name):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        # print("----- pm2 list ----- ")
        app_detect=0
        for item in result:
            name = item['name']
            # namespace = item['pm2_env']['namespace']
            # mode = item['pm2_env']['exec_mode']
            # pid = item['pid']
            # uptime = item['pm2_env']['pm_uptime']
            # status = item['pm2_env']['status']
            # cpu = item['monit']['cpu']
            # mem = item['monit']['memory'] / 1000000   
            if name.find(app_name)==0:
                app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error find pm2 : ',err)
        return 300
# Describe functions before writing code
# /**
# 	 * @description restart_pm2_change_template
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {id_template,db}
# 	 * @return data ()
# 	 */
async def restart_pm2_change_template(id_template:int,db:Session):
    try:
        
        # --------------------------------------
        # Restart PM2 read device
        template_query = db.query(template_models.Template_library).filter(template_models.Template_library.id == id_template).\
                                                filter(template_models.Template_library.status == 1)                                       
        result_template=template_query.first()
        device_list=[]
        if result_template:
            if result_template.device_group:
                if hasattr(result_template.device_group[0], 'device_list'):
                    result_device_list=[item for item in result_template.device_group[0].device_list if item.status == True]
                    device_list_rs485=[]
                    device_list_tcp=[]
                    device_list=result_device_list
                    for item in result_device_list:
                        print(f'{item.id_communication}|{item.id}|{item.name} {item.communication.driver_list.name}')
                        id_communication=item.id_communication
                        connect_type=item.communication.driver_list.name
                        channel_type=item.communication.namekey
                        id_device=item.id
                        
                        match connect_type:
                            case "Modbus/TCP":
                                pid=f'Dev|{id_communication}|{connect_type}|{id_device}'
                                device_list_tcp.append(pid)
                            case "RS485":
                                pid=f'Dev|{id_communication}|{connect_type}|{channel_type}'
                                device_list_rs485.append(pid)
                            case _:
                                continue
                    #
                    if device_list_rs485:
                        device_list_rs485=list(set(device_list_rs485))
                        print(f'device_list_rs485: {device_list_rs485}')
                        for item in device_list_rs485:
                            result_pm2=restart_program_pm2(pid)
                            print(f'pm2: {result_pm2}')
                    if device_list_tcp:
                        print(f'device_list_tcp: {device_list_tcp}')
                        result_pm2=restart_program_pm2_many(device_list_tcp)
                        
        # Restart PM2 log file
        if device_list:
            upload_channel_query = db.query(uploadChannel_models.Upload_channel).\
                                                    filter(uploadChannel_models.Upload_channel.status == 1)                         
            result_upload_channel=upload_channel_query.all()
            if result_upload_channel:
                pid_upload_channel_list=(lambda channel : [f'Log|{item.id}' for item in channel]) (result_upload_channel)
                print(f'pid_upload_channel_list: {pid_upload_channel_list}')
                result_pm2=restart_program_pm2_many(pid_upload_channel_list)
                # --------------------------------------
    except Exception as err:
        print(f'Error: {err}')
# Describe functions before writing code
# /**
# 	 * @description restart_pm2_delete_template
# 	 * @author vnguyen
# 	 * @since 15-01-2024
# 	 * @param {id_template,db}
# 	 * @return data ()
# 	 */
async def restart_pm2_update_template(device_lists,db:Session):
    try:
                
        # --------------------------------------
        # Restart PM2 read device
        result_device_list=device_lists
        device_list=[]
        device_list_rs485=[]
        device_list_tcp=[]
        device_list=result_device_list
        for item in result_device_list:
            print(f'{item.id_communication}|{item.id}|{item.name} {item.communication.driver_list.name}')
            id_communication=item.id_communication
            connect_type=item.communication.driver_list.name
            channel_type=item.communication.namekey
            id_device=item.id
            
            match connect_type:
                case "Modbus/TCP":
                    pid=f'Dev|{id_communication}|{connect_type}|{id_device}'
                    device_list_tcp.append(pid)
                case "RS485":
                    pid=f'Dev|{id_communication}|{connect_type}|{channel_type}'
                    device_list_rs485.append(pid)
                case _:
                    continue
        #
        if device_list_rs485:
            device_list_rs485=list(set(device_list_rs485))
            print(f'device_list_rs485: {device_list_rs485}')
            for item in device_list_rs485:
                result_pm2=restart_program_pm2(pid)
                print(f'pm2: {result_pm2}')
        if device_list_tcp:
            print(f'device_list_tcp: {device_list_tcp}')
            result_pm2=restart_program_pm2_many(device_list_tcp)
                        
        # Restart PM2 log file
        if device_list:
            upload_channel_query = db.query(uploadChannel_models.Upload_channel).\
                                                    filter(uploadChannel_models.Upload_channel.status == 1)                         
            result_upload_channel=upload_channel_query.all()
            if result_upload_channel:
                pid_upload_channel_list=(lambda channel : [f'Log|{item.id}' for item in channel]) (result_upload_channel)
                print(f'pid_upload_channel_list: {pid_upload_channel_list}')
                result_pm2=restart_program_pm2_many(pid_upload_channel_list)
                # --------------------------------------
    except Exception as err:
        print(f'Error: {err}')
# Describe functions before writing code
# /**
# 	 * @description delete many app running in pm2
# 	 * @author vnguyen
# 	 * @since 29-03-2024
# 	 * @param {list app_name of pm2}
# 	 * @return data ()
# 	 */
async def delete_program_pm2_many(app_name=[]):
    try:
        cmd_list=""
        if sys.platform == 'win32':
            cmd_list="pm2 jlist"
        else:
            cmd_list="sudo pm2 jlist"
        shellscript = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        app_detect=0
        pid_list=[]
        for item in result:
            name = item['name']
            for item_app in app_name:
                if name.find(item_app)==0:
                    pid= item['pm_id']
                    pid_list.append(pid)
        print(f'list {pid_list}')
        cmd_pm2=""
        if sys.platform == 'win32':
            cmd_pm2=f'pm2 delete '
        else:
            cmd_pm2=f'sudo pm2 delete '
        join_pid=""
        if pid_list:
            for item in pid_list:
                join_pid=join_pid+ " " +str(item)
            cmd_pm2= cmd_pm2 +join_pid
            print(f'cmd_pm2: {cmd_pm2}')
            os.system(f'{cmd_pm2}')
            app_detect=1
        if app_detect==1:
            return 100
        else:
            return 200
    except Exception as err:
        print('Error stop pm2 : ',err)
        return 300