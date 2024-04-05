import logging
import os
import sys
import mqttools
import asyncio
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *

arr = sys.argv
ModeSysTemp = ""

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC|device_id|device_name
# Subscribe -> IPC|device_id|device_name|control
MQTT_TOPIC = Config.MQTT_TOPIC +"/Dev/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
MQTT_TOPIC_SUD_MODECONTROL = "/Control/Setup/Mode/Write"
MQTT_TOPIC_PUB_FEEDBACK_MODECONTROL = "/Control/Setup/Mode/Feedback"


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
from utils.logger_manager import LoggerSetup
arr = sys.argv
# setup root logger
# logger_setup = LoggerSetup(path,"ControlDevice")
# LOGGER = logging.getLogger(__name__)
"""
project_setup ->    mode_control 0=Man 1=Zero Export 2= Limit P,Q
Mode = Man -> value direct to function read device
Mode = Zero Export ->   
Mode = Limit -> 
"""

async def confirm_mode_control(serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    global ModeSysTemp
    topic = serial_number_project + topicPublic
    
    if ModeSysTemp == "Manual" or ModeSysTemp == "Auto" :
        try:
            if ModeSysTemp:
                current_time = get_utc()
                data_send = {
                        "confirm_mode":ModeSysTemp,
                        "time_stamp" :current_time,
                        }
                push_data_to_mqtt(mqtt_host,
                        mqtt_port,
                        topic ,
                        mqtt_username,
                        mqtt_password,
                        data_send)
                pass
        except Exception as err:
            print(f"Error MQTT subscribe: '{err}'")
    else :
        pass
    
async def mqtt_subscribe_controlsV2(serial_number_project,host, port, topic, username, password):
    
    global ModeSysTemp
    
    mqtt_result = ""
    topic = serial_number_project + topic
    
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topic)
        
        while True:
            try:
                message = await asyncio.wait_for(client.messages.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            mqtt_result = json.loads(message.message.decode())
            print("mqtt_result",mqtt_result)

            if mqtt_result and 'mode' in mqtt_result:
                ModeSysTemp = mqtt_result['mode']
            print("ModeSysTemp",ModeSysTemp)

    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
        
async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    serial_number_project=results_project[0]["serial_number"]
    # 
    tasks.append(asyncio.create_task(mqtt_subscribe_controlsV2(serial_number_project,
                                                    MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC_SUD_MODECONTROL,
                                                    MQTT_USERNAME,
                                                    MQTT_PASSWORD
                                                    )))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(confirm_mode_control, 'cron',  second = f'*/1' , args=[serial_number_project,
                                                                        MQTT_BROKER,
                                                                        MQTT_PORT,
                                                                        MQTT_TOPIC_PUB_FEEDBACK_MODECONTROL,
                                                                        MQTT_USERNAME,
                                                                        MQTT_PASSWORD])
    scheduler.start()
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())