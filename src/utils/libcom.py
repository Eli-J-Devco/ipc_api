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
import mysql.connector
import paho.mqtt.publish as publish


# sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
#                 ("src"))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
# from logger_manager import setup_logger

# LOGGER = setup_logger(module_name='LIBCOM')

def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
      return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# setup root logger
# logger_setup = LoggerSetup("LIBCOM")
# LOGGER = logging.getLogger(__name__)
# ----- MQTT -----
# Describe functions before writing code
# /**
# 	 * @description public data MQTT alarm
# 	 * @author vnguyen
# 	 * @since 22-01-2024
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
def func_mqtt_public_alarm(host, port,topic, username, password, data_send):
    LOGGER = setup_logger(module_name='LIBCOM')
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        # LOGGER.error(f'{err}')
        print(f"Error MQTT public: '{err}'")
        LOGGER.error(f"{err}")
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=file_name)
    statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
    result={}
    for item,value in enumerate(statement):
      for key in value.keys():
        result[key]=value[key]   

    return result 
def cov_xml_sql(id_mybatis,param):

    node_script_path="jspybridge.js"
    # Run the Node.js script using subprocess
    # print(f'id_mybatis: {id_mybatis}')
    # print(f'param: {param}')
    result = subprocess.run(['node', node_script_path, 
                            'convert_mybatis',"mybatis/EnergyMapper.xml","mybatis",id_mybatis,str(param)], 
                            capture_output=True, text=True)
    # Check the result
    if result.returncode == 0:
        # print("Node.js script executed successfully.")
        # print("Output:\n", result.stdout)
        return result.stdout
    else:
        # print("Error executing Node.js script.")
        # print("Error message:\n", result.stderr)
        return ""
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
    
def cov_xml_sql(fileName,id_mybatis,param):
    
    node_script_path=path+"/utils/jspybridge.js"
    # Run the Node.js script using subprocess
    # print(f'id_mybatis: {id_mybatis}')
    # print(f'param: {param}')
    result = subprocess.run(['node', node_script_path, 
                            'convert_mybatis',path+"/mybatis/"+fileName,"mybatis",id_mybatis,str(param)], 
                            capture_output=True, text=True)
    # Check the result
    if result.returncode == 0:
        # print("Node.js script executed successfully.")
        # print("Output:\n", result.stdout)
        return result.stdout
    else:
        # print("Error executing Node.js script.")
        # print("Error message:\n", result.stderr)
        return ""