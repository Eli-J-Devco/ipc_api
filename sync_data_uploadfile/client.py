import asyncio
import os
import sys

import mybatis_mapper2sql

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from libMySQL import *

arr = sys.argv
id_upload_chanel = arr
DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_USERNAME = Config.DATABASE_USERNAME
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME
URL_SERVER_SYNC = Config.URL_SERVER_SYNC

QUERY_ALL_DEVICES = ""
QUERY_TIME_SYNC_DATA = ""
QUERY_SYNC_SERVER = ""

data_sent_server = {}
data = 0
status = 0 

def path_directory_relative(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    print("Path directory relative:", result)
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    try:
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+file_name)
        statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
        result={}
        for item,value in enumerate(statement):
            for key in value.keys():
                result[key]=value[key]   

        return result  
    except Exception as e:
        print('An exception occurred:',e)
        return -1 
async def bar2():
    global data
    while True:
        # print('bar2: ----------------------------------------------------')
        data +=1
        await asyncio.sleep(5)
# Describe Get data from Database
# /**
# 	 * @description get_Data
# 	 * @author bnguyen
# 	 * @since 8-1-2023
# 	 * @param {}
# 	 * @return data_sent_server
# 	 */
async def get_Data():
    global id_upload_chanel
    global QUERY_SYNC_SERVER
    global data_sent_server
    data_sync_server = []
    
    id_device_fr_sys = id_upload_chanel[1]
    
    data_sync_server = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,))
    if data_sync_server:
        data_sync_dict = data_sync_server[0]
        if 'id' not in data_sync_dict:
            return -1 
        if 'id_device' not in data_sync_dict:
            return -1 
        if 'modbusdevice' not in data_sync_dict:
            return -1 
        if 'data' not in data_sync_dict:
            return -1 
        
        id = data_sync_dict['id']        
        id_device = data_sync_dict['id_device']
        modbusdevice = data_sync_dict['modbusdevice']
        data = data_sync_dict['data']
                
    data_sent_server = {"id": id, "id_device": id_device, "modbusdevice": modbusdevice, "data": data}
# Describe Sent data to server
# /**
# 	 * @description send_data_to_server
# 	 * @author bnguyen
# 	 * @since 8-1-2023
# 	 * @param {}
# 	 * @return response.status_code
# 	 */
def send_data_to_server(URL_SERVER_SYNC):
    global status
    global data_sent_server
    
    try:
        if data_sent_server:
            response = requests.post(URL_SERVER_SYNC, json=data_sent_server)
            if response.status_code == 200:
                status = 1
            else:
                status = 0
    except Exception as e:
        status = 0
        print("Error connecting to the server:", str(e))
        
async def main():
    global id_upload_chanel
    id_device_fr_sys = id_upload_chanel[1]
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    global QUERY_ALL_DEVICES
    global QUERY_TIME_SYNC_DATA
    global QUERY_SYNC_SERVER
    try:
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TIME_SYNC_DATA = result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_SYNC_SERVER = result_mybatis["QUERY_SYNC_SERVER"]
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_TIME_SYNC_DATA or not QUERY_ALL_DEVICES or not QUERY_SYNC_SERVER:
        print("Error not found data in file mybatis")
        return -1
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    
    if not result_all or not time_sync_data :
        print("Error not found data in Database")
        return -1
    
    for item in time_sync_data:
        type_file = item["type_protocol"]
        time_sync = item["time_log_interval"]
        
        position = time_sync.rfind("minute")
        number = time_sync[:position]
        int_number = int(number)
    #-------------------------------------------------------
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(get_Data, 'cron', minute = f"*/{int_number}")
    scheduler.add_job(get_Data, 'cron', second = "*/10")
    # scheduler.add_job(send_data_to_server, 'cron', minute = f"*/{int_number}")
    scheduler.add_job(send_data_to_server, 'cron', second = "*/10" ,  args=[URL_SERVER_SYNC])
    scheduler.start()
    tasks = []
    # tasks.append(asyncio.create_task(bar1()))
    tasks.append(asyncio.create_task(bar2()))
    await asyncio.gather(*tasks, return_exceptions=False)
    #------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
