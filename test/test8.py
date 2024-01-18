# import asyncio
# import json
# import time
# # from controllers import bar, foo
# from datetime import datetime

# import mqttools
# import paho.mqtt.publish as publish
# from apscheduler.schedulers.asyncio import AsyncIOScheduler


# def func_mqtt_public(host, port,topic, username, password, data_send):
#     try:
#         print(f'public data to MQTT')
#         payload = json.dumps(data_send)
#         publish.single(topic, payload, hostname=host,
#                     retain=False, port=port,
#                     auth = {'username':f'{username}', 
#                             'password':f'{password}'})

#     except Exception as err:
#         print(f"Error MQTT public: '{err}'")
# async def foo(value):
#     print(f'foo: ---------------------------------------------------- {value}')
#     print(f'{datetime.now()} Foo')

# data=0

# async def bar():
#     # while True:
#         # print('bar2: ----------------------------------------------------')
#         global data
#         data +=1
#         # print(data)
#         # print(f'{datetime.now()} Bar2')
#         MQTT_BROKER = "127.0.0.1"
#         MQTT_PORT = 1883
#         MQTT_TOPIC = "IPC"
#         MQTT_USERNAME = "nextwave"
#         MQTT_PASSWORD = "123654789"
#         func_mqtt_public(MQTT_BROKER,MQTT_PORT,MQTT_TOPIC,MQTT_USERNAME,MQTT_PASSWORD,data)
#         # await asyncio.sleep(5)
# async def main():
#     # Init message
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(foo, 'cron', second="*/1",args=["111"])
#     scheduler.add_job(bar, 'cron', second="*/1",args=[])
#     # scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
#     # scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
#     scheduler.start()

# if __name__ == "__main__":
#     # loop = asyncio.get_event_loop()
#     # loop.create_task(main())
#     # loop.run_forever()
#     asyncio.get_event_loop().run_forever()


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
class LoggerSetup:

    def __init__(self) -> None:
        self.logger = logging.getLogger('')
        # self.logger1.setLevel(logging.INFO)
        self.setup_logging()
    def setup_logging(self):
        # add log format
        LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

        #configure formmater for logger
        formatter = logging.Formatter(LOG_FORMAT)

        # configure console handler
    #     console= logging.StreamHandler()
    #     console.setFormatter(formatter)
    #     console.setLevel("DEBUG")
    #     http_handle = logging.handlers.HTTPHandler( '127.0.0.1:3000',
    # '/log',
    # method='POST',) 
    #     self.logger.addHandler(console)
        # configure TimeRotatingFileHandler
        log_file_normal = f"info.log"
        log_file_error = f"error.log"
        
        # level_filter = LevelFilter(logging.INFO)
        # self.logger1.addFilter(level_filter)
        
        
        logHandler = logging.handlers.RotatingFileHandler(filename=log_file_normal, maxBytes=5*1024*1024, 
                                backupCount=0, encoding=None, delay=0)
        logHandler.setLevel(logging.INFO)
        logHandler.setFormatter(formatter)
        logHandler.addFilter(LevelFilter(logging.INFO))

        # backupCount --> create add 1 file
        errorLogHandler = logging.handlers.RotatingFileHandler(filename=log_file_error, maxBytes=50, 
                                backupCount=0, encoding=None, delay=0)
        errorLogHandler.setLevel(logging.ERROR)
        errorLogHandler.setFormatter(formatter)
        errorLogHandler.addFilter(LevelFilter(logging.ERROR))
        
        self.logger.addHandler(logHandler)
        self.logger.addHandler(errorLogHandler)
        # self.logger.addHandler(http_handle) 


        # add handlers
        
        
        # logger.debug('debug message')
        # logger.info('info message')
        # logger.warn('warn message')
        # logger.error('error message')
        # logger.critical('critical message')

logger_setup = LoggerSetup()
LOGGER = logging.getLogger(__name__)
LOGGER.info("--- Start up App ---")
LOGGER.error("--- Start App ---")
# while True:
#     LOGGER.error("--- Start App ---")
#     time.sleep(1)