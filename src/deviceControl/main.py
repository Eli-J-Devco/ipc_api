# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import collections
import datetime
import os
import sys
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
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

arr = sys.argv # Variables Array System
def pathDirectory(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
path=pathDirectory("ipc_api") # name of project
sys.path.append(path)
from utils.logger_manager import LoggerSetup
arr = sys.argv
# Describe process_zero_export_power_limit 
# 	 * @description process_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return chosse process zero_export ,power_limit ,zero_export + power_limit , Auto - Full P
# 	 */ 
async def automatedParameterManagement(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
    # Select the auto run process
    if resultDB["control_mode"] == 1 :
        print("==============================zero_export==============================")
        await processCaculatorPowerForInvInZeroExportMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
    else:
        print("==============================power_limit==============================")
        await processCaculatorPowerForInvInPowerLimitMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
############################################################################ Power Limit Control  ############################################################################
# Describe processCaculatorPowerForInvInPowerLimitMode 
# 	 * @description processCaculatorPowerForInvInPowerLimitMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return gIntValuePowerForEachInvInModePowerLimit
# 	 */ 
async def processCaculatorPowerForInvInPowerLimitMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
    # Local variables
    Arraydevices = []
    ArrayDeviceList = []
    gIntValuePowerForEachInvInModePowerLimit = 0 
    Powerlimit = resultDB["value_power_limit"]
    PowerLimitOffset = resultDB["value_offset_power_limit"]
    ModeSystem = resultDB["mode"]
    ModeDetail = resultDB["control_mode"]
    # Calculate Power Limit
    PowerlimitCaculator = Powerlimit - (Powerlimit * PowerLimitOffset / 100) if PowerLimitOffset is not None else Powerlimit
    # Get List Device Can Control 
    if messageMQTTAllDevice:
        # Calculate Total Power 
        totalProduction, totalConsumption = await ValueEnergySystemClass.calculate_production_and_consumption(messageMQTTAllDevice)
        # Calculate Power Of INV AutoMode
        Arraydevices = await GetListAutoDeviceClass.getListDeviceAutoModeInALLInv(messageMQTTAllDevice)
        TotalPowerINVAuto = GetListAutoDeviceClass.calculate_total_power_inv_auto(Arraydevices)
        # Extract device info
        ArrayDeviceList = [GetListAllDeviceClass.extract_device_all_info(item) for item in messageMQTTAllDevice if GetListAllDeviceClass.extract_device_all_info(item)]
        # Calculate the sum of wmax values of all inv in the system
        TotalPowerINVAll, TotalPowerINVMan = GetListAllDeviceClass.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
    # Get Infor Device Control 
    if Arraydevices:
        listInvControlPowerLimitMode = []
        for device in Arraydevices:
            id_device, mode, intPowerMaxOfInv = caculatorPowerClass.process_device_powerlimit_info(device)
            gIntValuePowerForEachInvInModePowerLimit = caculatorPowerClass.calculate_power_value(intPowerMaxOfInv,ModeSystem,TotalPowerINVMan,\
                TotalPowerINVAuto,PowerlimitCaculator)
            # Create Infor Device Publish MQTT
            if totalProduction < PowerlimitCaculator:
                item = caculatorPowerClass.create_control_item(ModeDetail,device, gIntValuePowerForEachInvInModePowerLimit,PowerlimitCaculator,\
                    TotalPowerINVMan,totalProduction)
            else:
                item = {
                    "id_device": id_device,
                    "mode": mode,
                    "status": "power limit",
                    "setpoint": PowerlimitCaculator - TotalPowerINVMan,
                    "feedback": totalProduction,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": max(0, gIntValuePowerForEachInvInModePowerLimit - (totalProduction - PowerlimitCaculator))}
                    ]
                }
            # Create List Device 
            listInvControlPowerLimitMode.append(item)
        # Push MQTT
        if len(Arraydevices) == len(listInvControlPowerLimitMode):
            MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlPowerLimitMode)
            MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto + "Binh",listInvControlPowerLimitMode)
############################################################################ Zero Export Control ############################################################################
# Describe processCaculatorPowerForInvInZeroExportMode 
# 	 * @description processCaculatorPowerForInvInZeroExportMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return PowerForEachInvInModeZeroExport
# 	 */ 
async def processCaculatorPowerForInvInZeroExportMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
    # Local variables
    Arraydevices = []
    ArrayDeviceList = []
    PowerForEachInvInModeZeroExport = 0
    PracticalConsumptionValue = 0.0
    Setpoint = 0 
    ModeSystem = resultDB["mode"]
    ModeDetail = resultDB["control_mode"]
    ThresholdZeroExport = resultDB.get("threshold_zero_export") or 0.0
    OffsetZeroExport = resultDB.get("value_offset_zero_export") or 0.0
    # Get List Device Can Control 
    if messageMQTTAllDevice:
        # Calculate Total Power 
        totalProduction, totalConsumption = await ValueEnergySystemClass.calculate_production_and_consumption(messageMQTTAllDevice)
        # Calculate Power Of INV AutoMode
        Arraydevices = await GetListAutoDeviceClass.getListDeviceAutoModeInALLInv(messageMQTTAllDevice)
        TotalPowerINVAuto = GetListAutoDeviceClass.calculate_total_power_inv_auto(Arraydevices)
        # Extract device info
        ArrayDeviceList = [GetListAllDeviceClass.extract_device_all_info(item) for item in messageMQTTAllDevice if GetListAllDeviceClass.extract_device_all_info(item)]
        # Calculate the sum of wmax values of all inv in the system
        TotalPowerINVAll, TotalPowerINVMan = GetListAllDeviceClass.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
    # Get Setpoint ,Value Consumption System 
    if totalConsumption:
        Setpoint, PracticalConsumptionValue = await caculatorPowerClass.calculate_setpoint(ModeSystem,totalConsumption,TotalPowerINVMan,OffsetZeroExport)
    if Arraydevices:
        listInvControlZeroExportMode = []
        for device in Arraydevices:
            id_device, mode, intPowerMaxOfInv = caculatorPowerClass.process_device_powerlimit_info(device)
            PowerForEachInvInModeZeroExport = caculatorPowerClass.calculate_power_value(intPowerMaxOfInv, ModeSystem, 
                TotalPowerINVMan, TotalPowerINVAuto, Setpoint)
            # Create Infor Device Publish MQTT
            if totalProduction < PracticalConsumptionValue and \
                totalConsumption >= ThresholdZeroExport and totalConsumption >= 0:
                item = caculatorPowerClass.create_control_item(ModeDetail,device, PowerForEachInvInModeZeroExport,Setpoint,\
                TotalPowerINVMan,totalProduction)
            else:
                item = {
                    "id_device": id_device,
                    "mode": mode,
                    "status": "zero export",
                    "setpoint": Setpoint,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": 0}
                    ]
                }
            # Create List Device 
            listInvControlZeroExportMode.append(item)
        # Push MQTT
        if len(Arraydevices) == len(listInvControlZeroExportMode):
            MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlZeroExportMode)
            MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto + "Binh",listInvControlZeroExportMode)
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
                await automatedParameterManagement(mqtt_service,messageMQTTAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_CONTROL_AUTO,resultDB)
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