import base64
import datetime
import gzip
import json
from pymodbus.client import ModbusTcpClient,AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
import mqttools
from .read_device.read_device_service import ReadModbusService
import paho.mqtt.publish as publish
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.devices.devices_model import DeviceInitOutput,DeviceInit,DeviceFull
from src.utils.register_block.register_block_model import RegisterBlockOutput
from src.utils.device_point.device_point_model import DevicePointsOutput,ControlPoints
from src.driver_device.read_device.read_device_model import ReadRegisterDevice,MergeRegisterDevice,StatusRB,RegisterData,RegisterValueDevice,PointDataOut
from src.mqtt_client.mqtt_client_service import MQTTClientService 
from src.mqtt_client.mqtt_client_model import MQTTConfigBase ,MQTTMsg, MQTTMsgs
from src.driver_device.monitoring_device.monitoring_device_service import MonitoringDeviceService
from src.utils.project_setup.project_setup_model import ProjectSetup
from src.utils.point_list_control_group.point_list_control_group_model import  PointListControlGroupsOut 


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
                    device_point_parameter_write_web
                    ):
        self.session=session
        self.multi_device_parameter=multi_device_parameter
        # -------------------------------------
        self.device_parameter=DeviceFull(**dict(multi_device_parameter[job_id]))
        # 
        
        self.init_read_modbus_service=ReadModbusService(job_id=job_id,job_events=job_events)
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
            client = AsyncModbusTcpClient(self.device_host, port=self.device_port)
            await client.connect()
            result_register_blocks=await self.init_read_modbus_service.read_data_device(
                                                                        connected=client.connected,
                                                                        client=client,
                                                                        slave_id=self.slave_id,
                                                                        register_blocks=self.register_blocks)
            client.close()
            if self.device_point_parameter_write_web:
                data:dict=self.device_point_parameter_write_web
                
                keys_to_delete = [key for key, value in data.items() if value.id_device == self.job_id]
                new_data=None
                for key in keys_to_delete:
                    print(key)
                    new_data=data[key]
                print(f'new_data: {new_data}')
                
        except (ConnectionException,ModbusException) as exc:
            print(f"device_manager job_id: {self.job_id}|AE ConnectionException", exc)
        finally:
            pass
        try:
            # print(f'result_register_blocks: {result_register_blocks.status_rb}')
            # print(f'result_register_blocks: {result_register_blocks.read_status_rb}')
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
        
        