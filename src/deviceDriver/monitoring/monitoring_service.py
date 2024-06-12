# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

class MonitorService:
    def __init__(self,
                id_template,rated_DC_input_voltage,maximum_DC_input_current,device_parent,
                device_id,device_name,status_device,msg_device,status_register_block,point_list_device,
                power_limit_percent,power_limit_percent_enable,reactive_limit_percent,reactive_limit_percent_enable,
                name_device_type,
                id_device_type,
                device_mode : None,
                rated_power,rated_power_custom,min_watt_in_percent,rated_reactive_custom,
                meter_type,inverter_type=None):
            
            # 
            self.id_template=id_template
            self.rated_DC_input_voltage=rated_DC_input_voltage
            self.maximum_DC_input_current=maximum_DC_input_current
            self.device_parent=device_parent
            self.device_id=device_id
            self.device_name=device_name
            self.status_device=status_device
            self.msg_device=msg_device
            self.status_register_block=status_register_block
            self.point_list_device=point_list_device
            self.power_limit_percent=power_limit_percent
            self.power_limit_percent_enable=power_limit_percent_enable
            self.reactive_limit_percent=reactive_limit_percent
            self.reactive_limit_percent_enable=reactive_limit_percent_enable
            self.name_device_type=name_device_type
            self.id_device_type=id_device_type
            self.device_mode=device_mode
            self.rated_power=rated_power
            self.rated_power_custom=rated_power_custom
            self.min_watt_in_percent=min_watt_in_percent
            self.rated_reactive_custom=rated_reactive_custom
            self.meter_type=meter_type
            self.inverter_type=inverter_type
            # 
    def device_type(self):
        match self.name_device_type:
            case "PV System Inverter":
                return self.device_mode
            case _:
                return None
    