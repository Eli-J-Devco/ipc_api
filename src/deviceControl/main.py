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
# Describe handle_mqtt_message 
# 	 * @description handle_mqtt_message
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_service,serial_number ,topic, message}
# 	 * @return 
# 	 */ 
async def handle_mqtt_message(mqtt_service,serial_number ,topic, message):
    topicSudMQTT = MQTTTopicSUD()
    topicPushMQTT = MQTTTopicPUSH()
    try:
        if topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE:
            await ModeSystemClass.handleModeSystemChange(mqtt_service,message, topicPushMQTT.MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL)
        elif topic in [serial_number + topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN,serial_number + topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP,serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODIFY_DEVICE]:   # topic8, topic9, topic10
            await ModeSystemClass.triggerDeviceModeChange(mqtt_service ,topicPushMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL:
            await ModeDetailClass.handleModeDetailChange(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO: 
            await ModeDetailClass.handleParametterDetailChange(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO )
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODEGET_INFORMATION: 
            await ProjectSetupClass.pudFeedBackProjectSetup(mqtt_service,topicPushMQTT.MQTT_TOPIC_PUD_PROJECT_SETUP)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE:
            await ProjectSetupClass.insertInformationProjectSetup(mqtt_service,message,topicPushMQTT.MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_DEVICES_ALL:
            messageMQTTAllDevice = message
            resultDB = await ProjectSetupClass.initializeValueControlAuto()
            if messageMQTTAllDevice:
                await GetListAllDeviceClass.GetListAllDeviceMain(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS,resultDB)
                await ValueEnergySystemClass.ValueEnergySystemMain(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_MONIT_METER)
                await caculatorPowerClass.automatedParameterManagement(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_CONTROL_AUTO,resultDB)
    except Exception as err:
        print(f"Error MQTT subscribe processMessage: '{err}'") 
# Describe consume_mqtt_messages 
# 	 * @description consume_mqtt_messages
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_service, client, serial_number}
# 	 * @return all topic , all message
# 	 */ 
async def consume_mqtt_messages(mqtt_service, client, serial_number):
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = MQTTService.gzip_decompress(mqtt_service, message.message)
            await handle_mqtt_message(mqtt_service, serial_number, topic, payload)
    except Exception as err:
        print(f"Error handle_mqtt_messages: '{err}'")
# Describe subscribe_to_mqtt_topics 
# 	 * @description subscribe_to_mqtt_topics
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_service, serial_number}
# 	 * @return all topic , all message
# 	 */ 
async def subscribe_to_mqtt_topics(mqtt_service, serial_number):
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
        await consume_mqtt_messages(mqtt_service, client, serial_number)
    except Exception as err:
        print(f"Error subscribe_to_mqtt_topics: '{err}'")
    finally:
        await client.stop()
# Describe start_mqtt_service 
# 	 * @description start_mqtt_service
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return 
# 	 */ 
async def start_mqtt_service():
    project_setup_config = await ProjectSetupClass.initializeValueControlAuto()
    if project_setup_config["serial_number"] is not None:
        mqtt_settings = MQTTSettings()
        mqtt_topics = MQTTTopicSUD()
        mqtt_service = MQTTService(
            host=mqtt_settings.MQTT_BROKER,
            port=mqtt_settings.MQTT_PORT,
            username=mqtt_settings.MQTT_USERNAME,
            password=mqtt_settings.MQTT_PASSWORD,
            serial_number=project_setup_config["serial_number"]
        )
        mqtt_service.set_topics(
            mqtt_topics.MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
            mqtt_topics.MQTT_TOPIC_SUD_MODEGET_INFORMATION,
            mqtt_topics.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL,
            mqtt_topics.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
            mqtt_topics.MQTT_TOPIC_SUD_DEVICES_ALL,
            mqtt_topics.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN,
            mqtt_topics.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP,
            mqtt_topics.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE,
            mqtt_topics.MQTT_TOPIC_SUD_SETTING_ARLAM,
            mqtt_topics.MQTT_TOPIC_SUD_MODIFY_DEVICE
        )
        tasks = []
        tasks.append(asyncio.create_task(subscribe_to_mqtt_topics(mqtt_service, project_setup_config["serial_number"])))
        await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(start_mqtt_service())