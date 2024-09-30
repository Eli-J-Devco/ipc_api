from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from src.device_manager.device_manager_model import PayloadSub
from src.device_manager.device_manager_model import MqttMsgSub, StatusJob,StatusJobs
from src.utils.devices.devices_entity import Devices as DevicesEntity
from src.mqtt_client.mqtt_client_model import MQTTConfigBase ,MQTTMsg, MQTTMsgs
from src.mqtt_client.mqtt_client_service import MQTTClientService
from src.device_manager.devices.device_model import Action as DevicesManagerAction

from src.device_manager.devices.device_model import Device as DeviceModel
from src.device_manager.devices.device_model import Devices as DevicesModel
from src.device_manager.devices.device_model import Action as DevicesAction
from src.pm2_manager.pm2_manager_service import Pm2ManagerService
from src.utils.utils import getUTC
from src.utils.devices.devices_model import DeviceInitOutput,DeviceInit,DeviceFull,ParameterListUpdate

from src.utils.devices.devices_service import DeviceService
class DevicesService:
    def __init__(self,
                session: AsyncSession,
                mqtt_config:MQTTConfigBase,
                multi_device_parameter,
                **kwargs):
        self.mqtt_config=mqtt_config
        self.session=session
        self.mqtt_client=MQTTClientService(mqtt_config=mqtt_config)
        self.multi_device_parameter=multi_device_parameter
        self.DeviceService=DeviceService(self.session)
    async def update_status_job_with_mqtt(self,devices:DevicesModel,status_jobs:StatusJobs):
        try:
            msgs=[]
            msgs.append(MQTTMsg(topic=f'{self.mqtt_config.serial_number}/{DevicesManagerAction.ControlModify.value}',payload= devices))
            msgs.append(MQTTMsg(topic=f'{self.mqtt_config.serial_number}/{DevicesAction.ResponseAPI.value}',payload= status_jobs))
            self.mqtt_client.public_multi_paho_zip(messages=MQTTMsgs(msgs=msgs),encode=False)
        except Exception as exc:
            print(f"Error update_status_job_with_mqtt: ", exc)
        finally:
            pass
        
    async def create_dev_tcp(self,code: str,func,payload:PayloadSub):
        status_jobs:StatusJobs
        devices:DevicesModel=[]
        try:
            jobs=[]
            for device in payload.device:
                result:StatusJob=await func(id_device=device.id)
                jobs.append(StatusJob(**result.dict()))
                devices.append(DeviceModel(id_device=result.id, mode=result.mode))
            status_jobs=StatusJobs(jobs=jobs,code=code, timestamp=getUTC())
        except Exception as exc:
            print(f"Error create_dev_tcp: ", exc)
        finally:
            print(f'status_jobs: {status_jobs}')
            pass
        
        try:
            if status_jobs:
                id_device = [item.id for item in status_jobs.jobs]
                
                query = (update(DevicesEntity)
                    .where(DevicesEntity.id.in_(id_device))
                    .where(DevicesEntity.creation_state == -1)
                    .values(creation_state=0))
                await self.session.execute(query)    
                await self.session.commit()
        except Exception as exc:
            print(f"Error update status create device: ", exc)
        finally:
            await self.session.close()
            await self.update_status_job_with_mqtt(devices=devices,status_jobs=status_jobs)
        try:
            pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
            await Pm2ManagerService.restart_program_pm2_many(app_name=pm2_app_list)
        except Exception as exc:
            print(f"Error run pm2 app: ", exc)
        finally:
            pass
    async def delete_dev(self,code: str,func,payload:PayloadSub):
        status_jobs:StatusJobs
        devices:DevicesModel=[]
        try:
            jobs=[]
            for device in payload.device:
                result:StatusJob=await func(id_device=device.id)
                jobs.append(StatusJob(**result.dict()))
                devices.append(DeviceModel(id_device=result.id))
            status_jobs=StatusJobs(jobs=jobs,code=code, timestamp=getUTC())
        except Exception as exc:
            print(f"Error delete_dev: ", exc)
        finally:
            print(f'status_jobs: {status_jobs}')
            await self.update_status_job_with_mqtt(devices=devices,status_jobs=status_jobs)
        try:
            pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
            await Pm2ManagerService.restart_program_pm2_many(app_name=pm2_app_list)
        except Exception as exc:
            print(f"Error run pm2 app: ", exc)
        finally:
            pass
    async def update_dev(self,code: str,payload:PayloadSub):
        status_jobs:StatusJobs
        devices:DevicesModel=[]
        try:
            jobs=[]
            if payload.id:
                id_device=payload.id
                device_parameter=await self.DeviceService.get_device(id_device=id_device)
                if not device_parameter:
                    return
                update_parameters=ParameterListUpdate.parameters.value
                
                if self.multi_device_parameter.get(id_device):
                    self.multi_device_parameter[id_device]=DeviceFull(**device_parameter.dict(exclude=update_parameters),
                                                                        rtu_bus_address=device_parameter.rtu_bus_address,
                                                                        tcp_gateway_ip=device_parameter.tcp_gateway_ip,
                                                                        tcp_gateway_port=device_parameter.tcp_gateway_port,
                                                                        mode=device_parameter.mode,
                                                                        rated_power=device_parameter.rated_power,
                                                                        rated_power_custom=device_parameter.rated_power_custom,
                                                                        min_watt_in_percent=device_parameter.min_watt_in_percent,
                                                                        DC_voltage=device_parameter.DC_voltage,
                                                                        DC_current=device_parameter.DC_current
                                                                        )
                    jobs.append(StatusJob(id=id_device, name=device_parameter.name))
                    status_jobs=StatusJobs(jobs=jobs,code=code, timestamp=getUTC())
                    devices.append(DeviceModel(id_device=id_device, mode=device_parameter.mode))
        except Exception as exc:
            print(f"Error update_dev: ", exc)
        finally:
            pass
            print(f'status_jobs: {status_jobs}')
            await self.update_status_job_with_mqtt(devices=devices,status_jobs=status_jobs)
        # try:
        #     pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
        #     await Pm2ManagerService.restart_program_pm2_many(app_name=pm2_app_list)
        # except Exception as exc:
        #     print(f"Error run pm2 app: ", exc)
        # finally:
        #     pass