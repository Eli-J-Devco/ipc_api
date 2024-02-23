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
# from database import get_db
# from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
#                      Response, status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {project_name}
# 	 * @return data (path of project)
# 	 */

def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    # print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    # print("Path directory relative:", result)
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from test.config import Config

# from logging_setup import LoggerSetup
from passlib.context import CryptContext

import models
from libcom import cov_xml_sql
# logging
from logger_manager import setup_logger

# setup root logger
LOGGER = setup_logger(module_name='API')

# -----------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Describe functions before writing code
# /**
# 	 * @description create file config network
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {ethernet_list,network_interface,pathfile}
# 	 * @return data ()
# 	 */
def create_file_config_network(ethernet_list,network_interface,pathfile):
  try:
      new_Line=[]
      new_Line.append('network:\n')
      new_Line.append('   version: 2\n')
      new_Line.append('   renderer: networkd\n')
      
      if len(ethernet_list)>0:
        new_Line.append('   ethernets:\n')
        
      for item in ethernet_list:
        if item.id==network_interface["id_ethernet"]:
            # add from api
            new_Line.append(f'      {network_interface["namekey"]}:\n')
            result=item.type_ethernet
            if network_interface["id_type_ethernet_name"]=="dhcp":
                new_Line.append(f'          dhcp4: yes\n')
            elif network_interface["id_type_ethernet_name"]=="none":
                new_Line.append(f'          dhcp4: no\n')
                new_Line.append(f'          addresses: [{network_interface["ip_address"]}/24]\n')
                
                new_Line.append(f'          gateway4: {network_interface["gateway"]}\n')
                if network_interface["allow_dns"]==True:
                    new_Line.append(f'          nameservers:\n')
                    new_Line.append(f'              addresses: [{network_interface["dns1"]}, {network_interface["dns2"]}]\n')
            else:
                new_Line.append(f'          dhcp4: yes\n')
          
        else:
            # add from database
            new_Line.append(f'      {item.namekey}:\n')
            result=item.type_ethernet
            if result.name=="dhcp":
                new_Line.append(f'          dhcp4: yes\n')
            elif result.name=="none":
                new_Line.append(f'          dhcp4: no\n')
                new_Line.append(f'          addresses: [{item.ip_address}/24]\n')
                new_Line.append(f'          gateway4: {item.gateway}\n')
                if item.allow_dns== True:
                    new_Line.append(f'          nameservers:\n')
                    new_Line.append(f'              addresses: [{item.dns1},{item.dns2}]\n')
                
            else:
                new_Line.append(f'          dhcp4: yes\n')
                
      # 
      # pathfile = 'D:\\NEXTWAVE\\project\\ipc_api\\test\\netplan\\01-netcfg.yaml'
      check_file = os.path.isfile(pathfile)
      if check_file:
          fileName = open(pathfile, 'w')
          fileName.writelines(new_Line)
          fileName.close()
      else:
          filename = Path(pathfile)
          filename.touch(exist_ok=True)
          # 
          fileName = open(pathfile, 'w')
          fileName.writelines(new_Line)
          fileName.close()
  except Exception as err:
    print('Error create file config network',err)
# Describe functions before writing code
# /**
# 	 * @description restart app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data ()
# 	 */
def restart_program_pm2(app_name):
    try:
        shellscript = subprocess.Popen(["pm2", "jlist"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                
        out, err = shellscript.communicate()
        result = json.loads(out)             
        app_detect=0
        for item in result:
            name = item['name']                   
            if name.find(app_name)==0:
                os.system(f'pm2 restart "{name}"')
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
def restart_program_pm2_many(app_name):
    try:
        shellscript = subprocess.Popen(["pm2", "jlist"],
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
        cmd_pm2=f'pm2 restart '
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
# 	 * @description delete app running in pm2
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
def delete_program_pm2(app_name):
    try:
        shellscript = subprocess.Popen(["pm2", "jlist"],
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
                os.system(f'pm2 delete "{name}"')
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
def stop_program_pm2(app_name):
    try:
        shellscript = subprocess.Popen(["pm2", "jlist"],
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
                os.system(f'pm2 stop "{name}"')
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
def create_program_pm2(filename,pid,id):
    if sys.platform == 'win32':
        # use run with window      
        subprocess.Popen(
        f'pm2 start {filename} -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
    else:               
        subprocess.Popen(
        f'pm2 start {filename} --interpreter python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
# Describe functions before writing code
# /**
# 	 * @description init app in pm2
# 	 * @author vnguyen
# 	 * @since 03-12-2023
# 	 * @param {app_name of pm2}
# 	 * @return data (status)
# 	 */
def create_device_group_rs485_run_pm2(absDirname,result_rs485_group):
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
                                f'pm2 start {absDirname}/driver_of_device/ModbusRTU.py -f  --name "{pid}" -- "{id}"  --restart-delay=10000', shell=True).communicate()
                        else:
                            # use run with ubuntu/linux
                           
                            subprocess.Popen(
                                f'pm2 start {absDirname}/driver_of_device/ModbusRTU.py --interpreter python3 -f  --name "{pid}" -- {id}  --restart-delay=10000', shell=True).communicate()
            
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
def find_program_pm2(app_name):
    try:
        shellscript = subprocess.Popen(["pm2", "jlist"],
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
# 	 * @description hash password
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {password}
# 	 * @return data (password)
# 	 */
def hash(password: str):
    return pwd_context.hash(password)
# Describe functions before writing code
# /**
# 	 * @description verify password
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {plain_password, hashed_password}
# 	 * @return data (password verify)
# 	 */
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+file_name)
    statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
    result={}
    for item,value in enumerate(statement):
      for key in value.keys():
        result[key]=value[key]   

    return result  
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 22-12-2023
# 	 * @param {auth}
# 	 * @return data (or_auth)
# 	 */
def convert_binary_auth(auth):
    try:
        result_auth=""
        for i,item in enumerate(auth):
            if i < len(auth)-1:
                result_auth=result_auth + str(item)+"|"
            else:
                result_auth=result_auth + str(item)
        if not result_auth:
            return 0
        else:
            return int(bin(eval(result_auth)),2)
    except Exception as err:
        print('Convert_binary_auth: '+err)
        return 0
# Describe functions before writing code
# /**
# 	 * @description convert :parameter to parameter
# 	 * @author vnguyen
# 	 * @since 27-12-2023
# 	 * @param {query,data}
# 	 * @return data (query)
# 	 */
def pybatis(query= str,params={}):
  
  if not type(params) is dict:
    return -1
  if not type(query) is str:
    return -1
  new_string=""
  for key, value in params.items():
    if str(f':{key}') in query:
      new_string = query.replace(str(f':{key}'), str(value))
  return new_string
# Describe functions before writing code
# /**
# 	 * @description restart_pm2_change_template
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {id_template,db}
# 	 * @return data ()
# 	 */
def restart_pm2_change_template(id_template:int,db:Session):
    try:
        
        # --------------------------------------
        # Restart PM2 read device
        template_query = db.query(models.Template_library).filter(models.Template_library.id == id_template).\
                                                filter(models.Template_library.status == 1)                                       
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
            upload_channel_query = db.query(models.Upload_channel).\
                                                    filter(models.Upload_channel.status == 1)                         
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
def restart_pm2_update_template(device_lists,db:Session):
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
            upload_channel_query = db.query(models.Upload_channel).\
                                                    filter(models.Upload_channel.status == 1)                         
            result_upload_channel=upload_channel_query.all()
            if result_upload_channel:
                pid_upload_channel_list=(lambda channel : [f'Log|{item.id}' for item in channel]) (result_upload_channel)
                print(f'pid_upload_channel_list: {pid_upload_channel_list}')
                result_pm2=restart_program_pm2_many(pid_upload_channel_list)
                # --------------------------------------
    except Exception as err:
        print(f'Error: {err}')