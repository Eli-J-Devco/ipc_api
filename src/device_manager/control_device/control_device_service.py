from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler

from src.device_manager.control_device.control_device_model import  (
                                                        ControlParameter,
                                                        ControlDevice,
                                                        ControlDevices
                                                        )
from src.utils.device_point.device_point_model import  (DevicePointsOutput
                                                        )
from src.configs.query_sql.point_list import query_all as point_query
from src.driver_device.monitoring_device.monitoring_device_model import Action as MonitorAction, DeviceTypeAction
from src.device_manager.control_device.control_device_model import \
     ControlModeDevice as ControlModeDeviceModel
class ControlDeviceService:
    def __init__(self,session: AsyncSession, 
                    multi_device_parameter,
                    multi_device_point,
                    **kwargs
                    ):
        self.session=session
        self.multi_device_parameter=multi_device_parameter
        self.multi_device_point=multi_device_point
    @async_db_request_handler
    async def get_register_control_device(self,device_data):
        control_devices: ControlDevices
        control_device_list=[]
        try:
            
            if not isinstance(device_data, list):
                return []
            control_devices=list(map(lambda item: ControlDevice(**item), device_data))
            if not control_devices:
                return []
            if not self.multi_device_point:
                return []
            for control_device in control_devices:
                device_point=DevicePointsOutput(**dict(self.multi_device_point[control_device.id_device]))
                parameter=[]
                for item_parameter in control_device.parameter:
                    result_point=[item for item in device_point.points if item_parameter.id_pointkey== item.pointkey ]
                    
                    if result_point:
                        parameter.append(ControlParameter(**item_parameter.dict(
                                                            exclude={"datatype","modbus_func","register_value","value"}),
                                                            datatype=result_point[0].value_datatype,
                                                            register_value=result_point[0].register_value,
                                                            modbus_func=result_point[0].func,
                                                            value=item_parameter.value
                                                            ))
                    else:
                        parameter.append(ControlParameter(**control_device.dict(),
                                                            ))
                control_device_list.append(ControlDevice(**control_device.dict(exclude={"parameter"}),parameter=parameter))
        except Exception as e:
            print("Error get_register_point_control: ", e)
        finally:
            return ControlDevices(control_device_list)
    @async_db_request_handler
    async def get_device_control(self,data):
        try:
            system_mode=ControlModeDeviceModel(**data)
            if not self.multi_device_parameter:
                return []
            control_device_list=[]
            keys_id_device = [id for id, value in self.multi_device_parameter.items() if value.device_type in [DeviceTypeAction.PVSystemInverter.value]]
            for item in keys_id_device:
                control_device_list.append(ControlDevice(id_device=item,
                                                        mode=system_mode.confirm_mode,
                                                        token=system_mode.token,
                                                        time=system_mode.time_stamp
                                                        ))
            
        except Exception as e:
            print("Error get_device_control: ", e)
        finally:
            return ControlDevices(control_device_list)