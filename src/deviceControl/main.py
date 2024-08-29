# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import MQTTSettings, MQTTTopicSUD,MQTTTopicPUSH
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from cpu.cpu_service import *
from deviceControl.serviceDeviceControl.control_service import *
from deviceControl.serviceDeviceControl.enegy_service import *
from deviceControl.serviceDeviceControl.modedetail_service import *
from deviceControl.serviceDeviceControl.modesystem_service import *
from deviceControl.serviceDeviceControl.processdevice_service import *
from deviceControl.serviceDeviceControl.siteinfor_service import *

############################################################################ Sud MQTT ############################################################################
# Describe processMessage 
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def processMessage(mqtt_service,serial_number ,topic, message):
    topicSudMQTT = MQTTTopicSUD()
    topicPushMQTT = MQTTTopicPUSH()
    try:
        # Process About ModeSystem
        if topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE:  # ok 
            await ModeSystemClass.handleModeSystemChange(mqtt_service,message, topicPushMQTT.MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL)
        elif topic in [serial_number + topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN,serial_number + topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP,serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODIFY_DEVICE]:   # topic8, topic9, topic10
            await ModeSystemClass.triggerDeviceModeChange(mqtt_service ,topicPushMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE)
        # Process Mode Control
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL:   # ok
            await ModeDetailClass.handleModeDetailChange(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO:   # ok
            await ModeDetailClass.handleParametterDetailChange(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO )
        # Process Table Project setup
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODEGET_INFORMATION:   # ok
            await ProjectSetupClass.pudFeedBackProjectSetup(mqtt_service,topicPushMQTT.MQTT_TOPIC_PUD_PROJECT_SETUP)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE:   # ok
            await ProjectSetupClass.insertInformationProjectSetup(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE)
        # Process List INV + Value Power
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_DEVICES_ALL:   # ok
            messageMQTTAllDevice = message
            resultDB = await ProjectSetupClass.initializeValueControlAuto()
            if messageMQTTAllDevice:
                # process all inv 
                await GetListAllDeviceClass.GetListAllDeviceMain(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS,resultDB)
                # value energy
                await ValueEnergySystemClass.ValueEnergySystemMain(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_MONIT_METER)
                # parametter power auto 
                await caculatorPowerClass.automatedParameterManagement(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_CONTROL_AUTO,resultDB)
    except Exception as err:
        print(f"Error MQTT subscribe processMessage: '{err}'") 
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processHandleMessagesDriver(mqtt_service,client, SerialNumer):
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = MQTTService.gzip_decompress(mqtt_service,message.message)
            await processMessage(mqtt_service,SerialNumer, topic, payload)
    except Exception as err:
        print(f"Error processHandleMessagesDriver: '{err}'")
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processSudAllMessageFromMQTT(mqtt_service,SerialNumer):
    # global mqtt_service
    try:
        client = mqttools.Client(
            host=mqtt_service.host,
            port=mqtt_service.port,
            username=mqtt_service.username,
            password=bytes(mqtt_service.password, 'utf-8'),
            subscriptions=mqtt_service.topics,
            connect_delays=[1, 2, 4, 8]
        )
        await client.start()
        await processHandleMessagesDriver(mqtt_service,client, SerialNumer)
    except Exception as err:
        print(f"Error in processSudAllMessageFromMQTT: '{err}'")
    finally:
        await client.stop()
async def main():
    # Initialize values ​​for global variables
    initialized_values = await ProjectSetupClass.initializeValueControlAuto()
    # Run Task
    if initialized_values["serial_number"] != None :
        parameterMQTT = MQTTSettings()
        topicSudMQTT = MQTTTopicSUD()
        # Khởi tạo dịch vụ MQTT
        mqtt_service = MQTTService(
            host=parameterMQTT.MQTT_BROKER,
            port=parameterMQTT.MQTT_PORT,
            username=parameterMQTT.MQTT_USERNAME,
            password=parameterMQTT.MQTT_PASSWORD,
            serial_number=initialized_values["serial_number"]  # Thay thế bằng serial number thực tế
        )
        # Đặt các topic SUD
        mqtt_service.set_topics(
            topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
            topicSudMQTT.MQTT_TOPIC_SUD_MODEGET_INFORMATION,
            topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL,
            topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
            topicSudMQTT.MQTT_TOPIC_SUD_DEVICES_ALL,
            topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN,
            topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP,
            topicSudMQTT.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE,
            topicSudMQTT.MQTT_TOPIC_SUD_SETTING_ARLAM,
            topicSudMQTT.MQTT_TOPIC_SUD_MODIFY_DEVICE
        )
        tasks = []
        tasks.append(asyncio.create_task(processSudAllMessageFromMQTT(
                                        mqtt_service,
                                        initialized_values["serial_number"]
                                        )))
        await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())