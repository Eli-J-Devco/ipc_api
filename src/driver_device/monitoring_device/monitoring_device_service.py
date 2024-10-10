import base64
import datetime
import gzip
import json
import math
import os
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
import mqttools
import paho.mqtt.publish as publish
from sqlalchemy.ext.asyncio import AsyncSession
import psutil
from src.utils.point_list_control_group.point_list_control_group_model import PointListControlGroup,PointListControlGroupsOut
from src.mqtt_client.mqtt_client_model import MQTTConfigBase
from src.utils.project_setup.project_setup_model import ProjectSetup
from src.driver_device.monitoring_device.monitoring_device_model import MonitoringDeviceBase
from src.utils.devices.devices_model import DeviceInitOutput,DeviceInit,DeviceFull
from src.utils.utils import getUTC
from src.driver_device.read_device.read_device_model import (ReadRegisterDevice,
                                                            MergeRegisterDevice,
                                                            StatusRB,RegisterData,
                                                            RegisterValueDevice,
                                                            PointDataBase,
                                                            PointDataOut)
from src.utils.point_list_type.point_list_type_model import PointListTypes
from src.utils.device_point.device_point_model import  DevicePointBase,DevicePointsOutput,ControlPoints
from src.driver_device.monitoring_device.monitoring_device_model import Action as MonitorAction, DeviceTypeAction
from src.driver_device.monitoring_device.monitoring_device_model import (MonitoringParameterBase,
                                                                        MonitoringParameters,
                                                                        MonitoringPointControlGroup,
                                                                        MonitoringPointControlGroups)
from src.utils.device_point.device_point_model import  StringBase,Strings,MPPTString,MPPT,MPPTs
from utils.config_information.config_information_model import PointConfigInforAction
from src.utils.point_list_control_group.point_list_control_group_model import PointListControlGroupsOut
from src.driver_device.read_device.read_device_model import StatusRB,StatusRBs

class MonitoringDeviceService:
    def __init__(   self,
                    session: AsyncSession,
                    job_id,job_events,
                    project_setup:ProjectSetup,
                    multi_device_parameter,
                    point_list_type: PointListTypes,
                    point_control_groups: PointListControlGroupsOut,
                    **kwargs
                    ):
        self.multi_device_parameter=multi_device_parameter
        self.project_setup=project_setup
        self.job_events=job_events
        self.job_id=job_id
        self.point_list_type=point_list_type
        self.point_control_groups=point_control_groups
    
    def get_cpu(self):
        try:
            memory=0
            process = psutil.Process(os.getpid())
            memory=round(process.memory_percent(),2)
        except Exception as exc:
            print(f"Error get_cpu: '{exc}'")   
        finally:
            return memory
    
    def get_status_device(self,register_value_device:RegisterValueDevice):
        try:
            status_device=register_value_device.status_device
        except Exception as exc:
            print(f"Error get_status_device: '{exc}'")   
        finally:
            return status_device
    
    def get_message_device(self,register_value_device:RegisterValueDevice):
        try:
            status_device=register_value_device.message
        except Exception as exc:
            print(f"Error get_status_device: '{exc}'")   
        finally:
            return status_device

    def update_point_list_data(self,
                                point_list_data:PointDataOut,
                                device_point_control:ControlPoints):
        try:
            point_list=[]
            device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
            if not point_list_data:
                return PointDataOut(point_list)
            for point in point_list_data:
                match point.point_key:
                    case MonitorAction.WMaxPercent.value:
                        value=[i for i in device_point_control if i.point_key==MonitorAction.WMaxPercent.value]
                        if value:
                            point_list.append(PointDataBase(**point.dict(exclude={"value"}),value=value[0].value))
                        else:
                            point_list.append(PointDataBase(**point.dict()))
                    case MonitorAction.WMaxPercentEnable.value:
                        value=[i for i in device_point_control if i.point_key==MonitorAction.WMaxPercentEnable.value]
                        if value:
                            point_list.append(PointDataBase(**point.dict(exclude={"value"}),value=value[0].value))
                        else:
                            point_list.append(PointDataBase(**point.dict()))
                    case MonitorAction.VarMaxPercent.value:
                        value=[i for i in device_point_control if i.point_key==MonitorAction.VarMaxPercent.value]
                        if value:
                            point_list.append(PointDataBase(**point.dict(exclude={"value"}),value=value[0].value))
                        else:
                            point_list.append(PointDataBase(**point.dict()))
                    case MonitorAction.VarMaxPercentEnable.value:
                        value=[i for i in device_point_control if i.point_key==MonitorAction.VarMaxPercentEnable.value]
                        if value:
                            point_list.append(PointDataBase(**point.dict(exclude={"value"}),value=value[0].value))  
                        else:
                            point_list.append(PointDataBase(**point.dict()))      
                    case MonitorAction.ACPowerFactor.value:
                        cosPhi=point.value
                        rated_power_custom=device_parameter.rated_power_custom
                        rated_power=device_parameter.rated_power
                        rated_reactive_custom=0
                        
                        if cosPhi not in [None, "null",0] and rated_power_custom not in [None, "null"] :
                            sinPhi=math.sqrt(1-cosPhi**2)
                            tanPhi=sinPhi/cosPhi
                            rated_reactive_custom=round(rated_power_custom*tanPhi,2)
                        else:
                            if  rated_power_custom  in [None, "null"] and cosPhi not in [None, "null",0]:
                                sinPhi=math.sqrt(1-cosPhi**2)
                                tanPhi=sinPhi/cosPhi
                                rated_reactive_custom=round(rated_power*tanPhi,2)
                            elif  rated_power_custom not in [None, "null"] and cosPhi in [None, "null",0]:
                                rated_reactive_custom=0
                            else:
                                rated_reactive_custom=0
                        
                        self.multi_device_parameter[self.job_id]=DeviceFull(**device_parameter.dict(exclude={"rated_reactive_custom"}),
                                                                    rated_reactive_custom=rated_reactive_custom)
                        point_list.append(PointDataBase(**point.dict()))
                    case MonitorAction.WMax.value:
                        control_max=None
                        rated_power_custom_calculator=device_parameter.rated_power_custom_calculator
                        rated_power=device_parameter.rated_power
                        if rated_power_custom_calculator not in [None, "null"]:
                            control_max=rated_power_custom_calculator
                        else:
                            control_max=rated_power
                        point_list.append(PointDataBase(**point.dict(exclude={"control_max"}),control_max=control_max))  
                    case _:
                        point_list.append(PointDataBase(**point.dict()))
        except Exception as exc:
            print(f"Error update_point_list_data: '{exc}'")   
        finally:
            return PointDataOut(point_list)
    
    def merger_point_mppt_in_point_simple():
        pass
    
    def get_parameters(self,
                        point_list_data:PointDataOut):
        try:
            parameters=[]
            for item_type in self.point_list_type:
                points=[]
                
                for item_point in point_list_data:
                    if item_point.id_point_list_type==item_type.id:
                        points.append(PointDataBase(**item_point.dict()))
                parameters.append(MonitoringParameterBase(id=item_type.id,
                                                          name=item_type.name,
                                                          fields=PointDataOut(points)
                                                          ))
            
        except Exception as exc:
            print(f"Error get_parameters: '{exc}'")   
        finally:
            return MonitoringParameters(parameters)
        
    def get_fields(self):
        try:
            pass
        except Exception as exc:
            print(f"Error get_fields: '{exc}'")   
        finally:
            return []
    
    def get_mppt(self,point_list_data:PointDataOut):
        try:
            # point_list=[]
            device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
            rated_DC_input_voltage=device_parameter.DC_voltage
            maximum_DC_input_current=device_parameter.DC_current
            mppts:MPPTs=[]
            for point in point_list_data:
                if point.config==PointConfigInforAction.MPPT.value:
                    mppt_volt:PointDataOut=[]
                    mppt_strings:PointDataOut=[]
                    mppt_amps:PointDataOut=[]
                    strings: Strings=[]

                    mppt_volt=[item for item in point_list_data if item.parent== point.id_point and item.config ==PointConfigInforAction.MPPTVolt.value ]
                    mppt_amps=[item for item in point_list_data if item.parent== point.id_point and item.config ==PointConfigInforAction.MPPTAmps.value ]
                    mppt_strings=[item for item in point_list_data if item.parent== point.id_point and item.config ==PointConfigInforAction.StringAmps.value ]
                    
                    number_mppt_panel=0
                    
                    # print(f'mppt_volt: {mppt_volt}')
                    for item_string in mppt_strings:
                        mppt_string_panel:PointDataOut=[]
                        mppt_string_panel=[item for item in point_list_data if item.parent == item_string.id_point and item.config ==PointConfigInforAction.Panel.value]
                        area=0
                        number_panel=0
                        if mppt_string_panel:
                            for item_panel in mppt_string_panel:
                                if item_panel.panel_height!=None and item_panel.panel_width !=None:
                                    area=area+(item_panel.panel_height/1000*item_panel.panel_width/1000)
                            number_panel=len(mppt_string_panel)
                            number_mppt_panel=number_mppt_panel+number_panel
                        strings.append(StringBase(point_key=item_string.point_key,
                                                name=item_string.name,
                                                value=item_string.value,
                                                area=area,
                                                number_panel=number_panel,
                                                ))
                    Quality=[]
                    if mppt_volt:
                        volt_quality=  [item for item in mppt_volt if item.quality== 1]
                        if volt_quality==[]:
                            Quality.append(0)
                        else:
                            Quality.append(1)
                    if mppt_amps:
                        amps_quality=  [item for item in mppt_amps if item.quality == 1]
                        if amps_quality==[]:
                            Quality.append(0)
                        else:
                            Quality.append(1)
                    if mppt_strings:
                        string_quality=  [item for item in mppt_strings if item.quality == 1]
                        if string_quality==[]:
                            Quality.append(0)
                        else:
                            Quality.append(1)
                    power =0
                    total_area_string=0
                    irradiance=0
                    if mppt_volt and mppt_amps:
                        mppt_v=(lambda x: x[0].value if x else None)(mppt_volt)
                        mppt_a=(lambda x: x[0].value if x else None)(mppt_amps)
                        if mppt_v!= None and mppt_a!=None:
                            power =mppt_v*mppt_a
                    
                    if strings:
                        for item in strings:
                            if item.value!=None and item.area!=0 and item.value!=0:
                                total_area_string=total_area_string+item.area
                    if power>0 and total_area_string>0:
                        irradiance=power/total_area_string
                    mppts.append(MPPT(
                                config=point.config,
                                id_point=point.id_point,
                                parent=point.parent,
                                id= point.id,
                                point_key=point.point_key,
                                name= point.name,
                                power=round(power,2)/1000,
                                area=round(total_area_string,2),
                                irradiance=round(irradiance,2),
                                number_panel=number_mppt_panel,
                                DC_voltage_max=rated_DC_input_voltage,
                                DC_current_max=maximum_DC_input_current,
                                value=MPPTString(mppt_volt=mppt_v,mppt_amps=mppt_a,mppt_string=strings),
                                timestamp=getUTC(),
                                quality=(lambda x: 1 if 1 in Quality else 0)(Quality),
                    ))    
        except Exception as exc:
            print(f"Error get_mppt: '{exc}'")   
        finally:
            return mppts
    
    def get_combiner_box(self):
        try:
            pass
        except Exception as exc:
            print(f"Error get_combiner_box: '{exc}'")   
        finally:
            return []
    
    def get_control_group(self,point_list_data:PointDataOut):
        try:
            point_control_groups: MonitoringPointControlGroups=[]
            
            for point_control_group in  self.point_control_groups:
                new_points:PointDataOut=[]
                for point_item in point_list_data:
                    if point_item.id_control_group==point_control_group.id:
                        new_points.append(PointDataBase(**point_item.dict()))
                new_points_data:PointDataOut=sorted(new_points, key=lambda addr: addr.control_menu_order)
                new_point_control_attr:PointDataOut=[]
                match point_control_group.attributes:
                    case 0:
                        for item_point_attr in new_points_data:
                            new_point_control_attr.append(PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=1))
                    case 1: 
                        if len(new_points_data)==2:
                            control_enable=(lambda x:  x[0].value if x else None) ([item for item in new_points_data if item.control_type_input == 4])
                            for item_point_attr in new_points_data:
                                    if item_point_attr.control_type_input == 4:
                                        new_point_control_attr.append(
                                            PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=1)
                                        )
                                    else:
                                        new_point_control_attr.append(
                                            PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=(lambda x: 1  if x==1 else 0)(control_enable))
                                        )
                            else:
                                for item_point_attr in new_points_data:
                                    new_point_control_attr.append(
                                            PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=1)
                                        )
                    case 2:
                        if len(new_points_data)==3:                   
                            control_enable=(lambda x:  x[0].value if x else None) ([item for item in new_points_data if item.control_type_input == 4])
                            if control_enable not in [None,"null"]:
                                    for item_point_attr in new_points_data:
                                        if item_point_attr.control_type_input == 4:
                                            new_point_control_attr.append(
                                                PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=1)
                                            )
                                        elif item_point_attr.control_type_input == 1:
                                            new_point_control_attr.append(
                                                PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=(lambda x: 1  if x==0 else 0)(control_enable))
                                            )
                                        elif item_point_attr.control_type_input == 3:
                                            new_point_control_attr.append(
                                                PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=(lambda x: 1  if x==1 else 0)(control_enable))
                                            )
                            else:
                                for item_point_attr in new_points_data:
                                    PointDataBase(**item_point_attr.dict(exclude={"control_enabled"}),control_enabled=1)      
                point_control_groups.append(MonitoringPointControlGroup(**point_control_group.dict(exclude={"fields"}),fields=new_point_control_attr))
            
        except Exception as exc:
            print(f"Error get_control_group: '{exc}'")   
        finally:
            return MonitoringPointControlGroups(point_control_groups)
    
    def get_device_mode(self):
        try:
            mode=None
            device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
            if device_parameter.device_type in [DeviceTypeAction.PVSystemInverter.value]:
                mode =device_parameter.mode
            else:
                mode= None
        except Exception as exc:
            print(f"Error get_device_mode: '{exc}'")   
        finally:
            return mode  
    def get_status_register_block(self,register_value_device:RegisterValueDevice):
        try:
            status_rb:StatusRBs=[]
            for item in register_value_device.status_rb:
                status_rb.append(StatusRB(**item.dict()))
        except Exception as exc:
            print(f"Error get_device_mode: '{exc}'")   
        finally:
            return status_rb
    def data_summary(self,
                    register_value_device:RegisterValueDevice,
                    point_list_data:PointDataOut,
                    device_point_control:ControlPoints
                    ):
        new_point_list_data=self.update_point_list_data(point_list_data=point_list_data,
                                        device_point_control=device_point_control)
        device_parameter=DeviceFull(**dict(self.multi_device_parameter[self.job_id]))
        mppt= self.get_mppt(point_list_data=new_point_list_data)
        
        
        
        memory=self.get_cpu()
        id_device=device_parameter.id
        id_device_group=device_parameter.id_device_group
        parent= device_parameter.parent
        
        mode= self.get_device_mode() # update
        device_name= device_parameter.name
        id_device_type= device_parameter.id_device_type
        name_device_type= device_parameter.device_type
        type_device_type= device_parameter.type_device_type
        
        meter_type= device_parameter.meter_type
        inverter_type= device_parameter.inverter_type
        
        status_device= self.get_status_device(register_value_device)
        message= self.get_message_device(register_value_device)
        timestamp= getUTC()
        status_register= self.get_status_register_block(register_value_device)
        point_count=len(new_point_list_data)
        parameters= self.get_parameters(point_list_data=new_point_list_data)
        fields= new_point_list_data
        
        combiner_box= []
        control_group=  self.get_control_group(point_list_data=new_point_list_data)
        rated_power= device_parameter.rated_power # update
        rated_power_custom= device_parameter.rated_power_custom # update
        min_watt_in_percent= device_parameter.min_watt_in_percent # update
        emergency_stop= device_parameter.emergency_stop # update
        rtu_bus_address= device_parameter.rtu_bus_address 
        
        rated_power_custom_calculator=device_parameter.rated_power_custom_calculator
        rated_reactive_custom=device_parameter.rated_reactive_custom
        
        return MonitoringDeviceBase(
            memory=memory,
            id_device=id_device,
            id_device_group=id_device_group,
            parent=parent,
            mode=mode,
            status_register=status_register,
            device_name=device_name,
            id_device_type=id_device_type,
            name_device_type=name_device_type,
            type_device_type=type_device_type,
            meter_type=meter_type,
            inverter_type=inverter_type,
            status_device=status_device,
            timestamp=timestamp,
            message=message,
            parameters=parameters,
            fields=fields,
            rated_power=rated_power,
            rated_power_custom=rated_power_custom,
            min_watt_in_percent=min_watt_in_percent,
            rated_power_custom_calculator=rated_power_custom_calculator,
            rated_reactive_custom=rated_reactive_custom,
            mppt=mppt,
            rtu_bus_address=rtu_bus_address,
            emergency_stop=emergency_stop,
            point_count=point_count,
            control_group=control_group
        )