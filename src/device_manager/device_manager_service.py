import asyncio
import datetime
import json
import os
import sys
from asyncio import run
from uuid import uuid1

import mqttools
from apscheduler.events import (EVENT_ALL, EVENT_JOB_ERROR,
                                EVENT_JOB_MAX_INSTANCES, JobExecutionEvent,
                                JobSubmissionEvent)
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text

from src.async_db.wrapper import async_db_request_handler
# import time
# path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
# sys.path.append(path)
# sys.stdout.reconfigure(encoding='utf-8')
from src.configs.config import Config
from src.configs.config import orm_provider as db_config
from src.device_manager.control_device.control_device_model import \
    ControlDevice as ControlDeviceModel
from src.device_manager.control_device.control_device_model import \
    ControlDevices as ControlDevicesModel
from src.device_manager.control_device.control_device_service import \
    ControlDeviceService
from src.device_manager.device_manager_model import \
    Action as DriverManagerAction
from src.device_manager.device_manager_model import (MqttDataSub, MqttMsgSub,
                                                     StatusJob, StatusJobs)
from src.device_manager.devices.devices_service import \
    DevicesService as DevicesManagerService
from src.driver_device.driver_device_service import DriverDevicesService
from src.mqtt_client.mqtt_client_model import MQTTConfigBase
from src.utils.device_point.device_point_service import DevicePointService
from src.utils.devices.devices_model import Action as DeviceAction
from src.utils.devices.devices_model import (DeviceFull, DeviceInit,
                                             DeviceInitOutput)
from src.utils.devices.devices_service import DeviceService
from src.utils.point_list_control_group.point_list_control_group_service import \
    PointListControlGroupService
from src.utils.point_list_type.point_list_type_model import PointListTypes
from src.utils.point_list_type.point_list_type_service import \
    PointListTypeService
from src.utils.project_setup.project_setup_model import ProjectSetup
from src.utils.project_setup.project_setup_service import ProjectSetupService
from src.utils.register_block.register_block_service import \
    RegisterBlockService
from src.utils.utils import getUTC

"""
G83VZT33/Manager/Device
{
    "code":"add_job",
    "payload":12
}
"""

import logging

logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
from pydantic import BaseModel, EmailStr


# from typing import List, Optional
# class JobBase(BaseModel):
#     id : Optional[int] = None
#     name : Optional[str] = None
# class JobOut(BaseModel):
#     Job: list[JobBase] = None
# class JobPausedException(Exception):
#     pass
class DeviceManagerService:
    
    def __init__(self,
                session: AsyncSession,
                project_setup:ProjectSetup,
                mqtt_config: MQTTConfigBase,
                # point_list_type: PointListTypes,
                
                **kwargs):
        
        self.session=session
        self.project_setup=project_setup
        self.DeviceService=DeviceService(self.session)
        self.RegisterBlockService=RegisterBlockService(self.session)
        self.DevicePointService=DevicePointService(self.session)
        self.PointListControlGroupService=PointListControlGroupService(self.session)
        
        self.mqtt_config =mqtt_config
        self.MQTT_BROKER = mqtt_config.host
        self.MQTT_PORT = mqtt_config.port
        self.MQTT_USERNAME = mqtt_config.username
        self.MQTT_PASSWORD = mqtt_config.password
        self.MQTT_TOPIC = mqtt_config.serial_number
        
        self.job_events = {}
        self.device_point_data={}
        self.control_group_list=None
        self.control_data = None
        self.device_point_control={}
        self.multi_device_parameter={}
        self.multi_device_point={}
        # 
        self.point_list_type=None
        # 
        self.sender = mqttools.Client(host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            password=self.MQTT_PASSWORD,
                            client_id='mqttools-{}'.format(uuid1().node),
                            connect_delays=[1, 2, 4, 8]
                            )
        self.devices_manager_service =DevicesManagerService(self.session,
                                                            mqtt_config=self.mqtt_config,
                                                            multi_device_parameter=self.multi_device_parameter)    
        self.control_device_service=ControlDeviceService(self.session,
                                                            multi_device_parameter=self.multi_device_parameter,
                                                            multi_device_point=self.multi_device_point
                                                        )
        self.device_point_parameter_write_web={}
        self.device_point_parameter_write_local={}
        try:
            
            self.scheduler = AsyncIOScheduler()
            # self.scheduler.add_listener(self.job_listener,  EVENT_JOB_ERROR | EVENT_JOB_MAX_INSTANCES)
            # executors = {
            #     'default': ThreadPoolExecutor(5)
            # }
            # self.scheduler = BackgroundScheduler(executors=executors)
            
            self.scheduler.start()
            
            
        except Exception as e:
            print('An exception occurred')
        finally:
            print("Scheduler inited")
    async def init(self):
        
        self.point_list_type = await self.async_task(self.session)
        await asyncio.sleep(1)
        await self.init_devices()

        
    # def job_listener(event, *args):
    #     try:
    #         if isinstance(event, JobExecutionEvent):
    #             if event.exception:
    #                 # print(f"Job failed with exception: {event.exception}")
    #                 print(f"Job failed with exception.")
    #             else:
    #                 print("Job executed successfully.")
    #         elif event.code == EVENT_JOB_MAX_INSTANCES:
    #             print(f"Job skipped due to max instances reached.")
    #         else:
    #             # print(f"Unhandled event: {event}")
    #             print(f"Unhandled event")
    #     except Exception as e:
    #         # print(f"Error in job listener: {e}")
    #         pass
    
    async def run_device(self,
                        id_device,
                        register_blocks,
                        device_points,
                        point_control_groups
                        ):
        now = datetime.datetime.now()
        job_id=id_device
        print(f'run_device job_id: {job_id}|{now} {'-'*20}')
        try:
            
            driver_device_services=DriverDevicesService(
                                                session=self.session,
                                                project_setup=self.project_setup,
                                                mqtt_config=self.mqtt_config,
                                                job_id=job_id,
                                                job_events=self.job_events,
                                                multi_device_parameter=self.multi_device_parameter,
                                                register_blocks=register_blocks,
                                                device_points=device_points,
                                                device_point_data=self.device_point_data,
                                                point_control_groups=point_control_groups,
                                                point_list_type=self.point_list_type,
                                                device_point_control=self.device_point_control,
                                                device_point_parameter_write_web=self.device_point_parameter_write_web
                                                )
            await driver_device_services.device_manager(
                                                control_data=self.control_data
                                                )
        except Exception as exc:
            print(f"run_device job_id: {id_device}|error", exc)
        finally:
            print(f'run_device job_id: {id_device}|add_device finish |')
            pass
    
    async def add_job(self,id_device: int):
        print(f'add_job ----------------- ')
        job_status=None
        job_message=""
        mode=None
        job_id=id_device
        
        device_name=""
        device_parameter=await self.DeviceService.get_device(id_device=id_device)
        if not device_parameter:
            return
        mode=device_parameter.mode
        device_name=device_parameter.name
        id_template=device_parameter.id_template
        register_blocks=[]
        if id_template:
            register_blocks=await self.RegisterBlockService.get_register_blocks(id_template=id_template)
        device_points=[]
        device_point_control=[]
        if id_device:
            device_points=await self.DevicePointService.get_device_points(id_device=id_device)
            device_point_control=await self.DevicePointService.get_device_point_control(points=device_points)
        point_control_groups=[]
        if id_template:    
            point_control_groups= await self.PointListControlGroupService.get_point_list_control_groups(id_template=id_template)
        
        try:
            
            if device_point_control:
                self.device_point_control[job_id]=device_point_control
            
            if device_parameter:
                self.multi_device_parameter[job_id]=device_parameter
            
            if device_points:
                self.multi_device_point[job_id]=device_points
    
            
            self.job_events[job_id] = True
            
            self.scheduler.add_job(
            self.run_device,
            args=[job_id,
                register_blocks,
                device_points,
                point_control_groups
                ],
            trigger='interval',
            id=f"{job_id}",
            seconds = 1,
            replace_existing=True,
            max_instances=1, 
            coalesce=True
            )
            job_status=1
        except Exception as exc:
            print(f"add_job job_id: |error", exc.args)
            job_message=exc
            pass
        finally:
            pass
            print(f'add_job job_id: {job_id}|created finish |')
            return StatusJob(id=job_id,status=job_status,message=job_message, mode=mode, name=device_name)
    
    async def remove_job(self,id_device: int):
        print(f'remove_job ----------------- ')
        job_status=None
        job_message=""
        # mode=None
        job_id=id_device
        # device_name=""
        
        try:
            self.job_events[job_id] = False 
            self.scheduler.remove_job(job_id=f"{job_id}")
            job_status=1
        except Exception as exc:
            print(f"add_job job_id: {job_id}|error", exc)
            job_message=exc
        finally:
            print(f'add_job job_id: {job_id}|created finish |')
            return StatusJob(id=job_id,status=job_status,message=job_message)
    
    async def add_devices(self,device_list:DeviceInitOutput):
        try:
            if device_list.devices:
                device_tcp=[]
                device_rs485=[]
                device_other=[]
                "Device tcp"
                device_tcp=[device for device in device_list.devices if device.connect_type in [DeviceAction.TCP.value]]
                "Device rs485"
                device_rs485=[device for device in device_list.devices if device.connect_type in [DeviceAction.RS485.value]]
                "Device other"
                if device_tcp:
                    
                    for device in device_tcp:
                        await self.add_job(id_device=device.id)
                if device_rs485:
                    # await self.add_job(id_device=1)
                    pass
                
        except Exception as exc:
            print(f"Error add_devices", exc)
        finally:
            print(f'Add_devices finish')
    
    async def init_devices(self):
        try:
            
            devices=await self.DeviceService.classify_devices()
            if not devices:
                return
            await self.add_devices(devices)
            pass
        except Exception as exc:
            print(f"Error init_devices", exc)
        finally:
            print(f'init_devices finish')
    @staticmethod
    async def async_task(session: AsyncSession):
        point_list_type: PointListTypes=[]
        try:
            await asyncio.sleep(1)
            point_list_type =await PointListTypeService.get_point_list_type(session)
            
        except Exception as exc:
            print(f"Error async_task", exc)
        finally:
            return point_list_type
    async def handle_messages_device(self,client:mqttools.Client):
        try :
            # 
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                mqtt_data_sub=MqttDataSub(topic=message.topic,message=message.message)
                
                print(f'Topic:   {mqtt_data_sub.topic}')
                if mqtt_data_sub.topic==f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicCreateUpdateDev.value}':
                    if not mqtt_data_sub.message:
                        return 
                    msg=json.loads(mqtt_data_sub.message.decode())
                    # msg=gzip_decompress(mqtt_data_sub.message)
                    msg_sub=MqttMsgSub(**msg)
                    match msg_sub.CODE:
                        case DriverManagerAction.CreateTCPDev.value:
                            if  msg_sub.PAYLOAD.device:
                                await self.devices_manager_service.create_dev_tcp(code=DriverManagerAction.CreateTCPDev.value,
                                                                                func=self.add_job,
                                                                                payload=msg_sub.PAYLOAD)
                        case DriverManagerAction.CreateRS485Dev.value:
                            pass
                        case DriverManagerAction.DeleteDev.value:
                            if  msg_sub.PAYLOAD.device:
                                await self.devices_manager_service.delete_dev(code=DriverManagerAction.DeleteDev.value,
                                                                                func=self.remove_job,
                                                                                payload=msg_sub.PAYLOAD)
                        case DriverManagerAction.UpdateDev.value:
                            if  msg_sub.PAYLOAD.device:
                                await self.devices_manager_service.update_dev(code=DriverManagerAction.UpdateDev.value,
                                                                                payload=msg_sub.PAYLOAD)
                        case DriverManagerAction.UpdateTemplate.value:
                            pass
                        case DriverManagerAction.DeleteTemplate.value:
                            pass
                        case DriverManagerAction.UpdatePortRS485.value:
                            pass
                        case DriverManagerAction.UpdateUploadChannels.value:
                            pass
                        case DriverManagerAction.CreateNoLogDev.value:
                            pass
                if mqtt_data_sub.topic==f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicWeb.value}':
                    
                    if not mqtt_data_sub.message:
                        return 
                    msg=json.loads(mqtt_data_sub.message.decode())
                    # msg=gzip_decompress(mqtt_data_sub.message)
                    # print(ControlDevicesModel(msg))
                    
                    device_points:ControlDevicesModel=await self.control_device_service.get_register_control_device(device_data=msg)
                    for item in device_points:
                        token=f'token={item.token}|id={item.id_device}'
                        self.device_point_parameter_write_web[token]=ControlDeviceModel(**item.dict())
                        
                    # print(f'self.device_point_parameter_write_web: {self.device_point_parameter_write_web}')
                    data={
                        "token=4444|id=296": {
                            "token":4444,
                            "id_device": 296,
                            "id_device_group": 1,
                            "mode": 0,
                            "rated_power": 3.33,
                            "rated_power_custom": None,
                            "parameter":[
                                {
                                    "id_pointkey": "WMaxPercentEnable",
                                    "datatype":1,
                                    "modbus_func":1,
                                    "register_value":22,
                                    "value": 0,
                                }
                            ]
                        },
                        "token=5555|id=300": {
                            "token":5555,
                            "id_device": 300,
                            "id_device_group": 1,
                            "mode": 0,
                            "rated_power": 3.33,
                            "rated_power_custom": None,
                            "parameter":[]
                        },
                        "token=6666|id=300": {
                            "token":6666,
                            "id_device": 300,
                            "id_device_group": 1,
                            "mode": 0,
                            "rated_power": 3.33,
                            "rated_power_custom": None,
                            "parameter":[]
                        },
                    }
                    
                    
                    
                # if 'code' in result.keys() and 'payload' in result.keys():
                #     if result["code"]=="add_job":
                #             job_id=result["payload"]
                #             self.job_events[job_id] = True
                #             print(f'job_id: {job_id}')
                #             self.scheduler.add_job(
                #             self.add_device,
                #             args=[job_id],
                #             # lambda: run(self.add_device(job_id)),
                #             trigger='interval',
                #             id=f"{job_id}",
                #             seconds = 1,
                #             replace_existing=True,
                #             max_instances=1, 
                #             coalesce=True
                #             )
                #     if result["code"]=="add_multi_job":
                #         pass    
                #     if result["code"]=="remove_job":  
                #         job_id=result["payload"]
                #         self.job_events[job_id] = False 
                        
                #         self.scheduler.remove_job(job_id=f"{job_id}")
                        
                #     if result["code"]=="pause_job":
                #         job_id=result["payload"]
                #         self.job_events[job_id] = False
                        
                #         self.scheduler.pause_job(job_id=f"{job_id}")
                        
                #     if result["code"]=="resume_job":
                #         job_id=result["payload"]
                #         self.job_events[job_id] = True
                        
                #         self.scheduler.resume_job(job_id=f"{job_id}")
                        
                #     if result["code"]=="pause":  
                #         self.scheduler.pause()
                                                
                #     if result["code"]=="resume":  
                #         self.scheduler.resume()
                        
                #     if result["code"]=="get_jobs":     
                #         result=self.scheduler.get_jobs()
                #         jobs=[]
                #         for item in result:
                #             jobs.append(JobBase(id=item.id,name=item.name))
                #         print(jobs)
                #         print(jobs[0].id)
                        
                #     if result["code"]=="control":
                #         self.control_data=result["payload"]
                #     if result["code"]=="get":
                #         job_id=result["payload"]
                #         if job_id==1:
                #             return []

                #         print('hello')
                #         # job_id=result["payload"]
                #         # name=result["name"]
                #         # print(f'name: {name} ||||||||||||||||||||||')
                #         # device_parameter=DeviceFull(**dict(self.multi_device_parameter[job_id]))
                #         # print(f'device_parameter: {device_parameter.name}')
                #         # self.multi_device_parameter[job_id]=DeviceFull(**device_parameter.dict(exclude={"name"}),name=name)
                        
                #         # PointDataBase(**point.dict(exclude={"timestamp"}),timestamp=timestamp )
                        
        except Exception as err:
            print(f"Error handle_messages_device: '{err}'") 
            pass

    async def device_manager(self):
        try:
                
            Topic=[]
            Topic.append(f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicCreateUpdateDev.value}')
            Topic.append(f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicWeb.value}')
            Topic.append(f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicAutoControl.value}')
            Topic.append(f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicModeSys.value}')
            Topic.append(f'{self.MQTT_TOPIC}/{DriverManagerAction.PathTopicMeter.value}')         
            client = mqttools.Client(host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            subscriptions=Topic,
                            password=bytes(self.MQTT_PASSWORD, 'utf-8'),
                            connect_delays=[1, 2, 4, 8]
                            )
            
            while True:
                await client.start()
                await self.handle_messages_device(client)
                await client.stop()
        except Exception as err:
            print(f"Error managerDrivers: '{err}'")   
