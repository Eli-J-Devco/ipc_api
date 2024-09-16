import asyncio
import time
import datetime
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
from utils.MQTTService import *
from cpu.cpu_service import CPUInfo
from deviceControl.setupSite.setup_site_service import *

# create global variables
net_io_counters_prev = {
    "TotalSent": 0,
    "TotalReceived": 0,
    "Timestamp": datetime.datetime.now()
}

disk_io_counters_prev = {
    "ReadBytes": 0,
    "WriteBytes": 0,
    "Timestamp": datetime.datetime.now()
}

def get_utc():
    now = None
    try:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return now
    except Exception as err:
        print(f"Error in get_utc: {err}")
        return None

async def getIPCHardwareInformation(mqtt_service, Topic_CPU_Information):
    global net_io_counters_prev, disk_io_counters_prev 
    timeStampPudCpuInformation = get_utc()
    system_info = {
        "Timestamp": timeStampPudCpuInformation,
        "Time": int(time.time() * 1000),
        "SystemInformation": {},
        "BootTime": {},
        "CPUInfo": {},
        "MemoryInformation": {},
        "DiskInformation": {},
        "NetworkInformation": {},
        "NetworkSpeed": {},
        "DiskIO": {}
    }
    try:
        # get system information
        system_info["SystemInformation"] = CPUInfo.getSystemInformation()
        system_info["BootTime"] = CPUInfo.getBootTime() or {}
        system_info["CPUInfo"] = CPUInfo.getCpuInformation() or {}
        system_info["MemoryInformation"] = CPUInfo.getMemoryInformation() or {}
        system_info["DiskInformation"] = CPUInfo.getDiskInformation() or {}
        system_info["NetworkInformation"] = CPUInfo.getNetworkInformation() or {}
        system_info["NetworkSpeed"] = CPUInfo.getNetworkSpeedInformation(net_io_counters_prev) or {}
        system_info["DiskIO"] = CPUInfo.getDiskIoInformation(disk_io_counters_prev) or {}
        # sent data to mqtt
        MQTTService.push_data(mqtt_service, Topic_CPU_Information + "Binh", system_info)
        MQTTService.push_data_zip(mqtt_service, Topic_CPU_Information, system_info)
    except Exception as err:
        print(f"Error in getIPCHardwareInformation: '{err}'")

async def main():
    setup_site_instance = SetupSite()
    initialized_values = await setup_site_instance.get_project_setup_values()
    parameterMQTT = MQTTSettings()
    topicPushMQTT = MQTTTopicPUSH()
    # Create Service MQTT
    mqtt_service = MQTTService(
        host=parameterMQTT.MQTT_BROKER,
        port=parameterMQTT.MQTT_PORT,
        username=parameterMQTT.MQTT_USERNAME,
        password=parameterMQTT.MQTT_PASSWORD,
        serial_number=initialized_values["serial_number"] 
    )
    # create scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(getIPCHardwareInformation, 'cron', second='*/3', args=[mqtt_service, topicPushMQTT.CPU_Information])
    scheduler.start()
    while True:
        await asyncio.sleep(1)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
