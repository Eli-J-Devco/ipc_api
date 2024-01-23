# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import logging
import os
import sys

import mysql.connector
import paho.mqtt.publish as publish

from logger_manager import setup_logger

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