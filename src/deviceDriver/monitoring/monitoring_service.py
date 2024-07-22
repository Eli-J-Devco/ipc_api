# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import datetime
import math


def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now

class MonitorService:
    def __init__(self,
                id_template,rated_DC_input_voltage,maximum_DC_input_current,device_parent,
                device_id,device_name,status_device,msg_device,status_register_block,point_list_device,
                power_limit_percent,power_limit_percent_enable,reactive_limit_percent,reactive_limit_percent_enable,
                name_device_type,
                id_device_type,
                device_mode : None,
                rated_power,rated_power_custom,min_watt_in_percent,
                # rated_reactive_custom,
                meter_type,inverter_type=None,
                emergency_stop=None
                ):
            
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
            # self.rated_reactive_custom=rated_reactive_custom
            self.meter_type=meter_type
            self.inverter_type=inverter_type
            self.emergency_stop=emergency_stop
            self.rated_reactive_custom=None
            # 
    def device_type(self):
        # match self.name_device_type:
        #     case "PV System Inverter":
        #         return self.device_mode
        #     case _:
        #         return None
        if self.name_device_type in ["PV System Inverter"]:
            return self.device_mode
        else:
            return None
    def point_list_change_para_control(self):
        new_point_list_device=[]
        for item in self.point_list_device:
            
            match item["point_key"]:
                case "WMaxPercent":
                    new_point_list_device.append({
                        **item,
                        "value":self.power_limit_percent,
                        })
                case "WMaxPercentEnable":
                    new_point_list_device.append({
                        **item,
                        "value":self.power_limit_percent_enable,
                        })
                case "VarMaxPercent":
                    new_point_list_device.append({
                        **item,
                        "value":self.reactive_limit_percent,
                        })
                case "VarMaxPercentEnable":
                    new_point_list_device.append({
                        **item,
                        "value":self.reactive_limit_percent_enable,
                        })
                case "ACPowerFactor":
                    cosPhi=item["value"]
                    
                    if cosPhi not in [None, "null",0] and self.rated_power_custom not in [None, "null"] :
                        sinPhi=math.sqrt(1-cosPhi**2)
                        tanPhi=sinPhi/cosPhi
                        self.rated_reactive_custom=round(self.rated_power_custom*tanPhi,2)
                        if self.rated_reactive_custom==-0.0:
                            self.rated_reactive_custom=0.0
                    else:
                        if  self.rated_power_custom  in [None, "null"] and cosPhi not in [None, "null",0]:
                            sinPhi=math.sqrt(1-cosPhi**2)
                            tanPhi=sinPhi/cosPhi
                            self.rated_reactive_custom=round(self.rated_power*tanPhi,2)
                            if self.rated_reactive_custom==-0.0:
                                self.rated_reactive_custom=0.0
                        elif  self.rated_power_custom not in [None, "null"] and cosPhi in [None, "null",0]:
                            self.rated_reactive_custom=0
                        else:
                            self.rated_reactive_custom=0            
                    new_point_list_device.append({
                        **item,
                        "timestamp":getUTC()
                        })
                case "WMax":
                    control_max=None
                    if self.rated_power_custom not in [None, "null"]:
                        control_max=self.rated_power_custom
                    else:
                        control_max=self.rated_power
                    new_point_list_device.append({
                        **item,
                        "control_max": control_max,
                        "timestamp":getUTC()
                        })
                case "VarMax":
                    cosPhi=0.95
                    control_max=None
                    sinPhi=math.sqrt(1-cosPhi**2)
                    tanPhi=sinPhi/cosPhi
                    if self.rated_power_custom not in [None, "null"]:
                        control_max=round(self.rated_power_custom*tanPhi,2)
                    else:
                        control_max=round(self.rated_power*tanPhi,2)
                    new_point_list_device.append({
                        **item,
                        "control_max": control_max,
                        "timestamp":getUTC()
                        })
                case _:
                    new_point_list_device.append({
                        **item,
                        "timestamp":getUTC()
                        })
        return new_point_list_device
    def combiner_box(self, point_list):
        # combiner=[
        #             {
        #                 "config": "StringAmps",
        #                 "id_point": 28,
        #                 "name":"STRING1",
        #                 "value":{
        #                     "string_amps": 0.1,
        #                     "number_panel": 4,
        #                 }
        #             },
        #         ]
        match self.name_device_type:
            case "String Combiner":
                combiner_string=[]
                combiner_string=[item for item in point_list if item["config"]=="StringAmps" ]
                combiner_box=[]
                for item_string in combiner_string:
                    combiner_string_panel=[item for item in point_list if item['parent'] == item_string["id_point"]and item['config'] =="Panel"]
                    combiner_box.append(
                        {
                            # **item_string,
                            "config": item_string["config"],
                            "id_point": item_string["id_point"],
                            "name":item_string["name"],
                            "value":{
                                "string_amps": item_string["value"],
                                "number_panel":len(combiner_string_panel)
                            }
                        }
                    )
                    
                return combiner_box
            case _:
                return []
            
    # def point_list_field(self):