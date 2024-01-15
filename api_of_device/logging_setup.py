import logging
import logging.handlers
import logging.handlers as handlers
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from utils import path_directory_relative

path=path_directory_relative("ipc_api")
sys.path.append(path)
class LevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level
class LoggerSetup:

    def __init__(self) -> None:
        self.logger = logging.getLogger('')
        self.setup_logging()
        # self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.DEBUG)

    def setup_logging(self):
        # add log format
        LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

        #configure formmater for logger
        formatter = logging.Formatter(LOG_FORMAT)

        # configure console handler
        # console= logging.StreamHandler()
        # console.setFormatter(formatter)
        # console.setLevel("DEBUG")
        # self.logger.addHandler(console)
        # configure TimeRotatingFileHandler
        path_file_info = f"{path}/api_of_device/logs/file_info.log"
        path_file_error = f"{path}/api_of_device/logs/file_error.log"
        # logHandler  = handlers.TimedRotatingFileHandler(filename=log_file_normal, when="midnight", backupCount=5)

        #  5MB
        logHandlerInfo = logging.handlers.RotatingFileHandler(filename=path_file_info, maxBytes=50*1024*1024, 
                                backupCount=0, encoding=None, delay=0)
        logHandlerInfo.setLevel(logging.INFO)
        logHandlerInfo.setFormatter(formatter)
        logHandlerInfo.addFilter(LevelFilter(logging.INFO))
        # 5MB
        logHandlerError = logging.handlers.RotatingFileHandler(filename=path_file_error, maxBytes=50*1024*1024, 
                                backupCount=0)
        logHandlerError.setLevel(logging.ERROR)
        logHandlerError.setFormatter(formatter)
        logHandlerError.addFilter(LevelFilter(logging.ERROR))
        
        self.logger.addHandler(logHandlerInfo)
        self.logger.addHandler(logHandlerError)

        # add handlers
        # logger.debug('debug message')
        # logger.info('info message')
        # logger.warn('warn message')
        # logger.error('error message')
        # logger.critical('critical message')
        