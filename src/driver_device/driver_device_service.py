import base64
import datetime
import gzip
import json

import mqttools
import paho.mqtt.publish as publish
from pymodbus.client import AsyncModbusTcpClient, ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
from sqlalchemy.ext.asyncio import AsyncSession

from src.driver_device.monitoring_device.monitoring_device_service import \
    MonitoringDeviceService
from src.driver_device.read_device.read_device_model import (
    MergeRegisterDevice, PointDataOut, ReadRegisterDevice, RegisterData,
    RegisterValueDevice, StatusRB)
from src.driver_device.read_device.read_device_service import ReadDeviceService
from src.driver_device.write_device.write_device_model import \
    WriteParameter as WriteParameterModel

from src.driver_device.write_device.write_device_service import \
    WriteDeviceService
from src.mqtt_client.mqtt_client_model import MQTTConfigBase, MQTTMsg, MQTTMsgs
from src.mqtt_client.mqtt_client_service import MQTTClientService
from src.utils.device_point.device_point_model import (ControlPoints,
                                                       DevicePointsOutput)
from src.utils.devices.devices_model import (DeviceFull, DeviceInit,
                                             DeviceInitOutput)
from src.utils.point_list_control_group.point_list_control_group_model import \
    PointListControlGroupsOut
from src.utils.project_setup.project_setup_model import ProjectSetup
from src.utils.register_block.register_block_model import RegisterBlockOutput

from src.driver_device.write_device.write_device_model import \
    WriteStatus as WriteStatusModel , Action as WriteDeviceAction

from src.driver_device.driver_device_model import \
    ParameterWeb as ParameterWebModel
from src.driver_device.driver_device_model import \
    ParameterAuto as ParameterAutoModel
from src.driver_device.driver_device_model import \
    ParameterMode as ParameterModeModel
    
from src.utils.devices.devices_entity import Devices as DevicesEntity

from sqlalchemy import update


class DriverDevicesService:
    def __init__(   self,
                    session: AsyncSession,
                    project_setup:ProjectSetup, 
                    mqtt_config:MQTTConfigBase,
                    job_id,
                    job_events,
                    multi_device_parameter,
                    register_blocks: RegisterBlockOutput,
                    device_points:DevicePointsOutput,
                    device_point_data,
                    point_control_groups:PointListControlGroupsOut,
                    point_list_type,
                    device_point_control,
                    device_point_parameter_write_web,
                    device_point_parameter_write_auto,
                    device_point_parameter_write_mode
                    ):
        self.session=session
        self.multi_device_parameter=multi_device_parameter
        # -------------------------------------
        self.device_parameter=DeviceFull(**dict(multi_device_parameter[job_id]))
        # 
        
        self.init_read_modbus_service=ReadDeviceService(job_id=job_id,job_events=job_events)
        self.job_events=job_events
        self.job_id=job_id
        self.mqtt_config=mqtt_config
        # -------------------------------------
        self.device_host = self.device_parameter.tcp_gateway_ip
        self.device_port = self.device_parameter.tcp_gateway_port
        self.slave_id =self.device_parameter.rtu_bus_address
        self.register_blocks=register_blocks
        self.device_points=device_points
        self.device_point_data=device_point_data
        
        # -------------------------------------
        self.project_setup=project_setup
        self.point_list_type=point_list_type
        
        self.device_point_control=device_point_control
        self.point_control_groups=point_control_groups
        
        self.device_point_parameter_write_web=device_point_parameter_write_web
        self.device_point_parameter_write_auto=device_point_parameter_write_auto
        self.device_point_parameter_write_mode=device_point_parameter_write_mode
        self.write_device_service=WriteDeviceService(mqtt_config=self.mqtt_config,id_device=job_id)
    async def update_parameter_from_web(self,parameter_web:ParameterWebModel):
        try:
            if parameter_web:
                device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
                mode=parameter_web.mode
                rated_power=parameter_web.rated_power
                rated_power_custom=parameter_web.rated_power_custom
                
                query = (update(DevicesEntity)
                    .where(DevicesEntity.id == self.job_id)
                    .values(mode=mode,rated_power=rated_power,rated_power_custom=rated_power_custom))
                await self.session.execute(query)    
                await self.session.commit()
                
                self.multi_device_parameter[self.job_id]=DeviceFull(**device_parameter.dict(exclude={"mode","rated_power","rated_power_custom"}),
                                                                        mode=mode,
                                                                        rated_power=rated_power,
                                                                        rated_power_custom=rated_power_custom
                                                                        
                                                                        )
        except Exception as e:
            print('Error update_parameter_from_web: {self.job_id} |', e)
        finally:
            await self.session.close()
    def check_parameter_from_web(self):
        
        try:
            data:dict=self.device_point_parameter_write_web
            device_token=None
            keys_id_device = [key for key, value in data.items() if value.id_device == self.job_id]
            new_data: ParameterWebModel=None
            for token in keys_id_device:
                device_token=token
                new_data=data[token]
                break
            
        except Exception as e:
            print('Error update_parameter_from_web: {self.job_id} |', e)
        finally:
            return ParameterWebModel(**new_data.dict(exclude={"device_token"}),device_token=device_token)
    def check_parameter_from_auto(self):
        
        try:
            data:dict=self.device_point_parameter_write_auto
            device_token=None
            keys_id_device = [key for key, value in data.items() if value.id_device == self.job_id]
            new_data: ParameterAutoModel=None
            for token in keys_id_device:
                device_token=token
                new_data=data[token]
                break
            
        except Exception as e:
            print('Error update_parameter_from_web: {self.job_id} |', e)
        finally:
            
            return ParameterAutoModel(**new_data.dict(exclude={"device_token"}),device_token=device_token)
    async def check_parameter_from_mode(self):
        
        try:
            data:dict=self.device_point_parameter_write_mode
            device_token=None
            keys_id_device = [key for key, value in data.items() if value.id_device == self.job_id]
            new_data: ParameterModeModel=None
            for token in keys_id_device:
                device_token=token
                new_data=data[token]
                break
            if new_data:
                device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
                mode=new_data.confirm_mode
                query = (update(DevicesEntity)
                        .where(DevicesEntity.id == self.job_id)
                        .values(mode=mode))
                await self.session.execute(query)    
                await self.session.commit()
                self.multi_device_parameter[self.job_id]=DeviceFull(**device_parameter.dict(exclude={"mode"}),
                                                                        mode=mode,
                                                                        )
        except Exception as e:
            print('Error check_parameter_from_mode: {self.job_id} |', e)
        finally:
            await self.session.close()
            return ParameterModeModel(**new_data.dict(exclude={"device_token"}),device_token=device_token)
    async def device_manager(self,control_data):
        try:
            print(f'device_host: {self.device_host} {'--'*50}')
            print(f'device_port: {self.device_port}')
            print(f'slave_id: {self.slave_id}')
            mqtt_client=MQTTClientService(mqtt_config=self.mqtt_config)
            monitoring_device=MonitoringDeviceService(
                                                    session=self.session,
                                                    job_id=self.job_id,
                                                    job_events=self.job_events,
                                                    project_setup=self.project_setup,
                                                    multi_device_parameter=self.multi_device_parameter,
                                                    point_list_type=self.point_list_type,
                                                    point_control_groups=self.point_control_groups
                                                    )
            
            result_register_blocks: RegisterValueDevice
            # client = ModbusTcpClient(self.device_host, port=self.device_port)
            if self.device_point_parameter_write_mode:
                result_parameter_mode=await self.check_parameter_from_mode()
                if result_parameter_mode:
                    print(f'result_parameter_mode: {result_parameter_mode}')
                    del self.device_point_parameter_write_mode[result_parameter_mode.device_token]
                
            client = AsyncModbusTcpClient(self.device_host, port=self.device_port)
            await client.connect()
            result_register_blocks=await self.init_read_modbus_service.read_data_device(
                                                                        connected=client.connected,
                                                                        client=client,
                                                                        slave_id=self.slave_id,
                                                                        register_blocks=self.register_blocks)
            
            if self.device_point_parameter_write_web:
                result_parameter_web=self.check_parameter_from_web()
                if result_parameter_web:
                    result_write: WriteStatusModel=await self.write_device_service.write_modbus_tcp(
                                                                                                    connected=client.connected,
                                                                                                    client=client,
                                                                                                    slave=self.slave_id,
                                                                                                    parameter=WriteParameterModel(**result_parameter_web.__dict__))
                    
                    if result_write.status in [WriteDeviceAction.WriteStatusSuccess.value,WriteDeviceAction.WriteStatusError.value]:
                        del self.device_point_parameter_write_web[result_parameter_web.device_token]
                        result_update_db=await self.update_parameter_from_web(parameter_web=result_parameter_web)
            if self.device_point_parameter_write_auto:
                result_parameter_auto=self.check_parameter_from_auto()
                if result_parameter_auto:
                    result_write: WriteStatusModel=await self.write_device_service.write_modbus_tcp(
                                                                                                    connected=client.connected,
                                                                                                    client=client,
                                                                                                    slave=self.slave_id,
                                                                                                    parameter=WriteParameterModel(**result_parameter_auto.__dict__))
                    if result_write.status in [WriteDeviceAction.WriteStatusSuccess.value,WriteDeviceAction.WriteStatusError.value]:
                        del self.device_point_parameter_write_auto[result_parameter_auto.device_token]
            
            client.close()    
        except (ConnectionException,ModbusException) as exc:
            print(f"device_manager job_id: {self.job_id}|AE ConnectionException", exc)
        finally:
            pass
        try:
            result_point_list_data=self.init_read_modbus_service.point_get_register_block(self.device_points,result_register_blocks)
            device_point_control=ControlPoints(self.device_point_control[self.job_id])
            result_data=monitoring_device.data_summary(register_value_device=result_register_blocks,
                                                    point_list_data=result_point_list_data,
                                                    device_point_control=device_point_control
                                                    )                
            msgs=[MQTTMsg(topic=f'{self.mqtt_config.serial_number}/Devices/{self.job_id}',payload= result_data)]
            mqtt_client.public_multi_paho_zip(messages=MQTTMsgs(msgs=msgs),encode=False)
        except Exception as e:
            print('Error monitoring data job_id: {self.job_id} |', e)
        finally:
            pass
        
        