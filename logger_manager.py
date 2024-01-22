# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
"""
MQTT_TOPIC= IPC/Logger/API
MQTT_TOPIC= IPC/Logger/RWDevice
MQTT_TOPIC= IPC/Logger/ControlDevice
MQTT_TOPIC= IPC/Logger/EventAlarm
MQTT_TOPIC= IPC/Logger/SyncData
MQTT_TOPIC= IPC/Logger/CreateFile
# 
path logs/API
path logs/RWDevice
path logs/ControlDevice
path logs/EventAlarm
path logs/SyncData
path logs/CreateFile

{
    "function":logging.getLogger(__name__),
    "error":"",
    "type":""
}
# How to use
from logger_manager import LoggerSetup
logger_setup = LoggerSetup(path,"API")
LOGGER = logging.getLogger(__name__)
"""
import logging
import logging.handlers
import logging.handlers as handlers
import os
import sys
import time
from logging.handlers import RotatingFileHandler


class LevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level
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
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
class LoggerSetup:
    def __init__(self,PATH="",FOLDER="") -> None:
        # 
        self.path=PATH
        self.folder=FOLDER
        self.logger = logging.getLogger('')
        self.setup_logging()
    def setup_logging(self):
        # add log format
        LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

        #configure formmater for logger
        formatter = logging.Formatter(LOG_FORMAT)
        pathFolder= self.path+'/'+f'logs/'+self.folder+'/'
        os.makedirs(pathFolder, exist_ok=True)
        
        path_file_info = pathFolder+f"file_info.log"
        path_file_warn = pathFolder+f"file_warn.log"
        path_file_error =  pathFolder+f"file_error.log"
        path_file_critical = pathFolder+f"file_critical.log"
        #   INFO
        logHandlerInfo = logging.handlers.RotatingFileHandler(filename=path_file_info, maxBytes=50*1024*1024, 
                                backupCount=0, encoding=None, delay=0)
        logHandlerInfo.setLevel(logging.INFO)
        logHandlerInfo.setFormatter(formatter)
        logHandlerInfo.addFilter(LevelFilter(logging.INFO))
        #   WARN
        logHandlerWarn = logging.handlers.RotatingFileHandler(filename=path_file_warn, maxBytes=50*1024*1024, 
                                backupCount=0, encoding=None, delay=0)
        logHandlerWarn.setLevel(logging.WARN)
        logHandlerWarn.setFormatter(formatter)
        logHandlerWarn.addFilter(LevelFilter(logging.WARN))
        #   ERROR
        logHandlerError = logging.handlers.RotatingFileHandler(filename=path_file_error, maxBytes=50*1024*1024, 
                                backupCount=0)
        logHandlerError.setLevel(logging.ERROR)
        logHandlerError.setFormatter(formatter)
        logHandlerError.addFilter(LevelFilter(logging.ERROR))
        
        #   CRITICAL
        logHandlerCritical = logging.handlers.RotatingFileHandler(filename=path_file_critical, maxBytes=50*1024*1024, 
                                backupCount=0)
        logHandlerCritical.setLevel(logging.CRITICAL)
        logHandlerCritical.setFormatter(formatter)
        logHandlerCritical.addFilter(LevelFilter(logging.CRITICAL))
        # add handlers
        self.logger.addHandler(logHandlerInfo)
        self.logger.addHandler(logHandlerWarn)
        self.logger.addHandler(logHandlerError)
        self.logger.addHandler(logHandlerCritical)
