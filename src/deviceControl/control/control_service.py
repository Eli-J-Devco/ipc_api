# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import os
import sys
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)


# ============================================================== Mode Systemp ================================
class ModeSystem:
    def __init__(self):
        pass
    @staticmethod
    async def pudSystempModeTrigerEachDeviceChange(Topic_Control_Setup_Mode_Write):
        # Chuyển sang chế độ người dùng bao gồm cả chế độ thủ công và tự động
            try:
                result_checkmode_control = await MySQL_Select_v1(
                    "SELECT device_list.mode, device_list.id FROM device_list "
                    "JOIN device_type ON device_list.id_device_type = device_type.id "
                    "WHERE device_type.name = 'PV System Inverter' AND device_list.status = 1;"
                )
                modes = set([item['mode'] for item in result_checkmode_control])
                
                if len(modes) == 1:
                    if 0 in modes:
                        data_send = {"id_device": "Systemp", "mode": 0}
                    elif 1 in modes:
                        data_send = {"id_device": "Systemp", "mode": 1}
                else:
                    data_send = {"id_device": "Systemp", "mode": 2}
                
                MQTTService.push_data_zip(Topic_Control_Setup_Mode_Write, data_send)
            except asyncio.TimeoutError:
                print("Timeout waiting for data from MySQL")
    @staticmethod
    async def processModeSystemChange(mqtt_service, gArrayMessageChangeModeSystemp, topicFeedbackModeSystemp):
        if gArrayMessageChangeModeSystemp.get('id_device') == 'Systemp':
            gStringModeSysTemp = gArrayMessageChangeModeSystemp.get('mode')
            if gStringModeSysTemp in [0, 1, 2]:
                querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
                MySQL_Insert_v5(querysystemp, (gStringModeSysTemp,))
            else:
                print("Failed to insert data")
            if gStringModeSysTemp in [0, 1]:
                querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';"
                MySQL_Insert_v5(querydevice, (gStringModeSysTemp,))
            current_time = get_utc()
            objectSend = {
                "status": 200,
                "confirm_mode": gStringModeSysTemp,
                "time_stamp": current_time,
            } if gStringModeSysTemp in [0, 1, 2] else {
                "status": 400,
                "time_stamp": current_time,
            }
            MQTTService.push_data_zip(mqtt_service, topicFeedbackModeSystemp, objectSend)
            return gStringModeSysTemp

# ============================================================== Parametter Mode Detail Systemp ================================
class ModeDetailHandler:
    def __init__(self):
        pass
    async def processUpdateModeControlDetail(self, mqtt_service, messageModeControlAuto, Topic_Control_Setup_Mode_Write_Detail_Feedback):
        # Biến cục bộ
        stringAutoMode = ""
        intComment = 0
        arrayResultUpdateModeDetailInTableProjectSetUp = []
        
        # Nhận dữ liệu từ MQTT
        try:
            if messageModeControlAuto and 'control_mode' in messageModeControlAuto:
                stringAutoMode = messageModeControlAuto['control_mode'] 
                stringAutoMode = int(stringAutoMode)
                # So sánh và cập nhật thông tin vào cơ sở dữ liệu 
                if stringAutoMode == 1:
                    gIntControlModeDetail = 1
                elif stringAutoMode == 2:
                    gIntControlModeDetail = 2 
                # Cập nhật chế độ trong cơ sở dữ liệu
                arrayResultUpdateModeDetailInTableProjectSetUp = await MySQL_Update_V1("UPDATE project_setup SET control_mode = %s", (gIntControlModeDetail,))
                # Gửi phản hồi đến MQTT
                if arrayResultUpdateModeDetailInTableProjectSetUp is None:
                    intComment = 400 
                else:
                    intComment = 200 
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment, 
                }
                MQTTService.push_data_zip(mqtt_service, Topic_Control_Setup_Mode_Write_Detail_Feedback, objectSend)
                # Trả về biến toàn cục
                return gIntControlModeDetail
        except Exception as err:
            print(f"Error MQTT subscribe processUpdateModeControlDetail: '{err}'")
            return None  # Trả về None nếu có lỗi
    @staticmethod
    async def processUpdateParameterModeDetail( mqtt_service, messageParameterControlAuto, Topic_Control_Setup_Auto_Feedback ,totalPowerINV):
        stringAutoMode = ""
        intComment = 0
        arrayResultUpdateParameterZeroExportInTableProjectSetUp = []
        arrayResultUpdateParameterPowerLimitInTableProjectSetUp = []
        query = "SELECT * FROM `project_setup`"
        result = await MySQL_Select_v1(query)
        print("messageParameter", messageParameterControlAuto)
        try:
            if messageParameterControlAuto and 'mode' in messageParameterControlAuto and 'offset' in messageParameterControlAuto :
                stringAutoMode = int(messageParameterControlAuto['mode'])
                if stringAutoMode == 1:
                    gIntValueOffsetZeroExport, gIntValueThresholdZeroExport, arrayResultUpdateParameterZeroExportInTableProjectSetUp = await handle_zero_export_mode(messageParameterControlAuto)
                    gIntValueOffsetPowerLimit = result[0]["value_offset_power_limit"]
                    gIntValuePowerLimit = result[0]["value_power_limit"]
                elif stringAutoMode == 2:
                    gIntValueOffsetPowerLimit, gIntValuePowerLimit, arrayResultUpdateParameterPowerLimitInTableProjectSetUp = await handle_power_limit_mode(messageParameterControlAuto, totalPowerINV)
                    gIntValueOffsetZeroExport = result[0]["value_offset_zero_export"]
                    gIntValueThresholdZeroExport = result[0]["threshold_zero_export"]
                # Feedback to MQTT
                if (arrayResultUpdateParameterZeroExportInTableProjectSetUp is None or 
                    arrayResultUpdateParameterPowerLimitInTableProjectSetUp is None or 
                    (gIntValuePowerLimit is not None and gIntValuePowerLimit > totalPowerINV and stringAutoMode == 2)):
                    intComment = 400 
                else:
                    intComment = 200 
                
                # Object Sent MQTT
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment,
                }
                
                # Push MQTT
                MQTTService.push_data_zip(mqtt_service, Topic_Control_Setup_Auto_Feedback, objectSend)
                return {
                    "value_offset_zero_export": gIntValueOffsetZeroExport,
                    "value_power_limit": gIntValuePowerLimit,
                    "value_offset_power_limit": gIntValueOffsetPowerLimit,
                    "threshold_zero_export": gIntValueThresholdZeroExport,
                }
        except Exception as err:
            print(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'")
            return None
        
async def handle_zero_export_mode( message):
    ValueOffsetTemp = message.get("offset", 0)
    ValueThresholdTemp = message.get("threshold", 0)
    
    # Result Query 
    ResultQuery = MySQL_Update_V1(
        "UPDATE project_setup SET value_offset_zero_export = %s, threshold_zero_export = %s",
        (ValueOffsetTemp, ValueThresholdTemp)
    )
    return ValueOffsetTemp, ValueThresholdTemp, ResultQuery

async def handle_power_limit_mode( message, TotalPower):
    ValueOffsetTemp = message.get("offset", 0)
    ValuePowerLimitTemp = message.get("value", 0)
    
    if ValuePowerLimitTemp is not None and ValuePowerLimitTemp <= TotalPower:
        ValuePowerLimit = ValuePowerLimitTemp - (ValuePowerLimitTemp * ValueOffsetTemp) / 100
        # Result Query 
        ResultQuery = MySQL_Update_V1(
            "UPDATE project_setup SET value_power_limit = %s, value_offset_power_limit = %s",
            (ValuePowerLimitTemp, ValueOffsetTemp)
        )
        return ValueOffsetTemp, ValuePowerLimit, ResultQuery
    
    return ValueOffsetTemp, None, None

# ==================================================== Get List Auto Device  ==================================================================
class GetListAutoDevice:
    def __init__(self):
        pass
    def extract_device_auto_info(self, item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom = item.get('rated_power_custom', p_max)
            p_min_percent = item['min_watt_in_percent']
            p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
            value = self.get_device_value(item, "ControlINV")
            if value is None:
                return None
            operator = self.get_device_value(item, "OperatingState")
            if operator is None:
                return None
            slope = self.get_device_value(item, "WMax", field_key='slope')
            if slope is None:
                return None
            results_device_type = item.get('name_device_type')
            if results_device_type is None:
                return None
            return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
        return None
    def get_device_value(self, item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None

    def is_device_controlable(self, results_device_type, status_device, mode, operator):
        return (results_device_type == "PV System Inverter" and 
                status_device == 'online' and 
                mode == 1 and 
                operator not in [7, 8])
    def get_device_value(self, item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None
    
# ==================================================== Get List All Device ==================================================================
class GetListAllDevice:
    def __init__(self):
        pass
    def extract_device_all_info(self, item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom = item.get('rated_power_custom', p_max)
            p_min_percent = item['min_watt_in_percent']
            device_name = item['device_name']
            results_device_type = item['name_device_type']
            
            if results_device_type == "PV System Inverter":
                operator, wmax, capacity_power, real_power = self.get_device_parameters(item)
                
                if status_device == 'offline':
                    real_power = 0.0
                    operator = "off"
                    
                p_min = self.calculate_p_min(p_max_custom, p_min_percent)
                
                return {
                    'id_device': id_device,
                    'device_name': device_name,
                    'mode': mode,
                    'status_device': status_device,
                    'operator': operator,
                    'capacitypower': capacity_power,
                    'p_max': p_max_custom,
                    'p_min': p_min,
                    'wmax': wmax,
                    'realpower': real_power,
                    'timestamp': get_utc(),
                }
        return None
    @staticmethod
    def get_device_parameters(item):
        stringOperatorText = {
            0: "shutting down",
            1: "shutting down",
            4: "running",
            5: "running",
            6: "shutting down",
            7: "fault",
        }
        
        ArrayOperator = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                        for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
        intOperator = ArrayOperator[0] if ArrayOperator else 0
        operator = stringOperatorText.get(intOperator, "off")
        
        wmax = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                        for field in param.get("fields", []) if field["point_key"] == "WMax"), 0)
        capacity_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                                for field in param.get("fields", []) if field["point_key"] == "PowerOutputCapability"), 0)
        real_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                            for field in param.get("fields", []) if field["point_key"] == "ACActivePower"), 0)

        return operator, wmax, capacity_power, real_power
    @staticmethod
    def calculate_total_wmax(device_list, power_auto):
        total_power_write_inv = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None), 2)
        total_power_manual = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None and device['mode'] == 0), 2)
        total_power = round((total_power_manual + power_auto), 2)
        return total_power, total_power_manual
    @staticmethod
    def calculate_p_min(p_max_custom, p_min_percent):
        return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0
    @staticmethod
    def update_system_performance(current_mode, systemPerformance, total_power_in_all_inv, production_system, low_performance_threshold, high_performance_threshold):
        if current_mode == 0:
            systemPerformance = (production_system / total_power_in_all_inv) * 100 if total_power_in_all_inv else 0
        
        systemPerformance = round(systemPerformance, 1)
        
        if systemPerformance < low_performance_threshold:
            StringMessageStatusSystemPerformance = "System performance is below expectations."
            intStatusSystemPerformance = 0
        elif low_performance_threshold <= systemPerformance < high_performance_threshold:
            StringMessageStatusSystemPerformance = "System performance is meeting"
            intStatusSystemPerformance = 1
        else:
            StringMessageStatusSystemPerformance = "System performance is exceeding established thresholds."
            intStatusSystemPerformance = 2

        return systemPerformance, StringMessageStatusSystemPerformance, intStatusSystemPerformance
    async def getListALLInvInProject(self,mqtt_service, messageAllDevice, Topic_Control_Process , ArlamLow , ArlamHigh,TotalPoductionINV , ModeSystem , TotalPowerINVAuto,SystemPerformance):
        
        ArrayDeviceList = []
        TotalPowerINV = 0.0
        TotalPowerINVMan = 0.0
        # Get Information about the device
        if messageAllDevice and isinstance(messageAllDevice, list):
            for item in messageAllDevice:
                device_info = self.extract_device_all_info(item)
                if device_info:
                    ArrayDeviceList.append(device_info)
        
        # Calculate the sum of wmax values of all inv in the system
        TotalPowerINV, TotalPowerINVMan = self.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        
        # Call the update_system_performance function and get the return value
        SystemPerformance, Message, intStatusSystemPerformance = self.update_system_performance(
            ModeSystem,
            SystemPerformance,
            TotalPowerINV,
            TotalPoductionINV,
            ArlamLow,
            ArlamHigh
        )
        
        # Message Public MQTT
        result = {
            "ModeSystempCurrent": ModeSystem,
            "devices": ArrayDeviceList,
            "total_max_power": TotalPowerINV,
            "total_max_power_man": TotalPowerINVMan,
            "total_max_power_auto": TotalPowerINVAuto,
            "system_performance": {
                "performance": SystemPerformance,
                "message": Message,
                "status": intStatusSystemPerformance
            }
        }
        
        # Public MQTT
        MQTTService.push_data_zip(mqtt_service, Topic_Control_Process, result)
        return TotalPowerINV,TotalPowerINVMan,SystemPerformance
    
    
# ==================================================== Get Value Metter  ==================================================================
class ValueEnergySystem:
    def __init__(self):
        pass

    def get_device_type(id_device):
        return MySQL_Select(
            "SELECT `device_type`.`name` FROM `device_type` "
            "INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id "
            "WHERE `device_list`.id = %s",
            (id_device,)
        )

    def calculate_production( item, result_type_meter, IntTotalValueProduction):
        if result_type_meter[0]["name"] == "PV System Inverter":
            ArrayValueProduction = [
                field["value"] for param in item.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            for param in item.get("parameters", []):
                if param["name"] == "Basic":
                    for field in param.get("fields", []):
                        if field["point_key"] == "ACActivePower":
                            print("Found ACActivePower value:", field["value"])
            if ArrayValueProduction and ArrayValueProduction[0] is not None:
                IntTotalValueProduction += ArrayValueProduction[0]
                print('IntTotalValueProduction',IntTotalValueProduction)
            return IntTotalValueProduction

    def calculate_consumption(item, result_type_meter, IntTotalValueConsumption):
        if result_type_meter[0]["name"] == "Consumption meter":
            ArrayValueConsumption = [
                field["value"] for param in item.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            if ArrayValueConsumption and ArrayValueConsumption[0] is not None:
                IntTotalValueConsumption += ArrayValueConsumption[0]
            return IntTotalValueConsumption

    def message_value_metter(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp):
        timeStampGetValueProductionAndConsumption = get_utc()
        gFloatValueMaxPredictProductionInstant_temp = 0
        ValueProductionAndConsumption = {
            "Timestamp": timeStampGetValueProductionAndConsumption,
            "instant": {},
        }
        if gArrayMessageAllDevice:
            for device in gArrayMessageAllDevice:
                if "mppt" in device:
                    for mppt in device["mppt"]:
                        if "power" in mppt:
                            gFloatValueMaxPredictProductionInstant_temp += mppt["power"]
        # instant power
        ValueProductionAndConsumption["instant"]["production"] = round(gIntValueProductionSystemp, 4)
        ValueProductionAndConsumption["instant"]["consumption"] = round(gIntValueConsumptionSystemp, 4)
        ValueProductionAndConsumption["instant"]["grid_feed"] = round((gIntValueProductionSystemp - gIntValueConsumptionSystemp), 4)
        ValueProductionAndConsumption["instant"]["max_production"] = round(gFloatValueMaxPredictProductionInstant_temp, 4)
        return ValueProductionAndConsumption
    @staticmethod
    async def getValueProductionAndConsumption(mqtt_service, gArrayMessageAllDevice, Topic_Meter_Monitor):
        # Get Value Production And Consumption From message All
        IntTotalValueProduction = 0.0 
        IntTotalValueConsumtion = 0.0
        if gArrayMessageAllDevice:
            for item in gArrayMessageAllDevice:
                if 'id_device' in item:
                    id_device = item['id_device']
                    result_type_meter = ValueEnergySystem.get_device_type(id_device)
                    print("id_device",id_device)
                    print("result_type_meter",result_type_meter)
                    if result_type_meter:
                        IntTotalValueProduction= ValueEnergySystem.calculate_production(
                            item, result_type_meter, IntTotalValueProduction
                        )
                        IntTotalValueConsumtion = ValueEnergySystem.calculate_consumption(
                            item, result_type_meter, IntTotalValueConsumtion,
                        )
            # Update the global values of total production and total consumption
            gIntValueProductionSystemp = IntTotalValueProduction
            gIntValueConsumptionSystemp = IntTotalValueConsumtion
            print("gIntValueProductionSystemp",gIntValueProductionSystemp)
            print("gIntValueConsumptionSystemp",gIntValueConsumptionSystemp)
        try:
            ValueProductionAndConsumtion = ValueEnergySystem.message_value_metter(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp)
            # Push system_info to MQTT
            MQTTService.push_data_zip(mqtt_service, Topic_Meter_Monitor, ValueProductionAndConsumtion)
        except Exception as err:
            print(f"Error MQTT subscribe pudValueProductionAndConsumtionInMQTT: '{err}'")
        
        # Return the relevant global variables
        return gIntValueProductionSystemp, gIntValueConsumptionSystemp

# ==================================================== Caculator PowerLit And ZeroExport  ==================================================================
class FuntionCaculatorPower:
    def __init__(self):
        pass
    @staticmethod
    async def calculate_system_performance(ModeSystemp, ValueSystemPerformance, ValueProductionSystemp, Setpoint):
        if ModeSystemp != 0:
            if Setpoint > 0 and ValueProductionSystemp > 0:
                ValueSystemPerformance = (ValueProductionSystemp / Setpoint) * 100
            elif Setpoint <= 0 and ValueProductionSystemp > 0:
                ValueSystemPerformance = 101
            else:
                ValueSystemPerformance = 0
        return ValueSystemPerformance
    @staticmethod
    def process_device_powerlimit_info(device):
        id_device = device["id_device"]
        mode = device["mode"]
        intPowerMaxOfInv = float(device["p_max"])
        return id_device, mode, intPowerMaxOfInv
    @staticmethod
    def calculate_power_value(intPowerMaxOfInv, modeSystem, TotalPowerInInvInManMode, TotalPowerInInvInAutoMode, Setpoint):
        # Tính toán hiệu suất cho thiết bị
        if modeSystem == 1:
            floatEfficiencySystemp = (Setpoint / TotalPowerInInvInAutoMode)
        else:
            floatEfficiencySystemp = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
        
        # Công suất của thiết bị bằng hiệu suất nhân với công suất tối đa.
        if 0 <= floatEfficiencySystemp <= 1:
            return floatEfficiencySystemp * intPowerMaxOfInv
        elif floatEfficiencySystemp < 0:
            return 0
        else:
            return intPowerMaxOfInv
    @staticmethod
    def create_control_item(ModeSystemDetail ,device, PowerForEachInv, Setpoint, TotalPowerInInvInManMode, ValueProductionSystemp):
        if ModeSystemDetail == 1 :
            status = "Zero Export"
        else:
            status = " Power Limit "
        id_device = device["id_device"]
        mode = device["mode"]
        ItemlistInvControlPowerLimitMode = {
            "id_device": id_device,
            "mode": mode,
            "time": get_utc(),
            "status": status,
            "setpoint": Setpoint - TotalPowerInInvInManMode,
            "feedback": ValueProductionSystemp,
            "parameter": []
        }
        # Tạo mục cho thiết bị
        if device['controlinv'] == 1:
            ItemlistInvControlPowerLimitMode["parameter"].append({"id_pointkey": "WMax", "value": PowerForEachInv})
        elif device['controlinv'] == 0:
            ItemlistInvControlPowerLimitMode["parameter"].extend([
                {"id_pointkey": "ControlINV", "value": 1},
                {"id_pointkey": "WMax", "value": PowerForEachInv}
            ])
        return ItemlistInvControlPowerLimitMode
    async def calculate_setpoint(self, modeSystem, ValueConsump, ValueTotalPowerInInvInManMode,
                                    gListMovingAverageConsumption, gMaxValueChangeSetpoint, ValueOffetConsump):
        ConsumptionAfterSudOfset = 0.0
        if modeSystem == 1:
            gListMovingAverageConsumption.append(ValueConsump)
        else:
            gListMovingAverageConsumption.append(ValueConsump - ValueTotalPowerInInvInManMode)

        if ValueConsump > ValueTotalPowerInInvInManMode:
            intAvgValueComsumtion = sum(gListMovingAverageConsumption) / len(gListMovingAverageConsumption)
        else:
            intAvgValueComsumtion = 0

        if not hasattr(self.calculate_setpoint, 'last_setpoint'):
            self.calculate_setpoint.last_setpoint = intAvgValueComsumtion
        
        new_setpoint = intAvgValueComsumtion
        setpointCalculatorPowerForEachInv = max(
            self.calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
            min(self.calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        self.calculate_setpoint.last_setpoint = setpointCalculatorPowerForEachInv
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump) / 100)
        if setpointCalculatorPowerForEachInv:
            setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv * ValueOffetConsump / 100
        return setpointCalculatorPowerForEachInv, ConsumptionAfterSudOfset
class ProjectSetupService:
    def __init__(self):
        pass
    @staticmethod
    async def initializeValueControlAuto():
        # Biến cục bộ
        gIntValueOffsetZeroExport = 0
        gIntValuePowerLimit = 0
        gIntValueOffsetPowerLimit = 0
        gIntValueThresholdZeroExport = 0
        gIntValueSettingArlamLowPerformance = 0
        gIntValueSettingArlamHighPerformance = 0
        gStringModeSystempCurrent = ""
        serialNumber = ""
        # Biến tạm
        gIntValuePowerLimit_temp = 0
        # Lấy thông tin từ cơ sở dữ liệu lần đầu
        try:
            arrayResultInitializeParameterZeroExportInTableProjectSetUp = await MySQL_Select_v1("SELECT * FROM project_setup")
            if arrayResultInitializeParameterZeroExportInTableProjectSetUp:
                serialNumber = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["serial_number"]
                gStringModeSystempCurrent = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["mode"]
                gIntControlModeDetail = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["control_mode"]
                gIntValueOffsetZeroExport = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_zero_export"]
                gIntValuePowerLimit_temp = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_power_limit"]
                gIntValueOffsetPowerLimit = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_power_limit"]
                gIntValuePowerLimit = (gIntValuePowerLimit_temp - (gIntValuePowerLimit_temp * gIntValueOffsetPowerLimit) / 100)
                gIntValueThresholdZeroExport = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["threshold_zero_export"]
                gIntValueSettingArlamLowPerformance = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["low_performance"]
                gIntValueSettingArlamHighPerformance = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["high_performance"]
                
                # Trả về các giá trị đã khởi tạo
                return {
                    "serial_number": serialNumber,
                    "mode": gStringModeSystempCurrent,
                    "control_mode": gIntControlModeDetail,
                    "value_offset_zero_export": gIntValueOffsetZeroExport,
                    "value_power_limit": gIntValuePowerLimit,
                    "value_offset_power_limit": gIntValueOffsetPowerLimit,
                    "threshold_zero_export": gIntValueThresholdZeroExport,
                    "low_performance": gIntValueSettingArlamLowPerformance,
                    "high_performance": gIntValueSettingArlamHighPerformance,
                }
        except Exception as err:
            print(f"Error MQTT subscribe initializeValueControlAuto: '{err}'")
            return None  # Trả về None nếu có lỗi
    @staticmethod
    async def pudFeedBackProjectSetup(mqtt_service,topic_project_information):
        query_all_table_project_setup = "SELECT * FROM `project_setup`"
        try :
            # Lấy thông tin từ cơ sở dữ liệu
            result_all_information_table_project_setup = await MySQL_Select_v1(query_all_table_project_setup)
            
            if result_all_information_table_project_setup:
                try:
                    # Gửi thông tin đến MQTT
                    data_send_topic_project_information = result_all_information_table_project_setup[0]
                    data_send_topic_project_information['mqtt'] = [
                        {"time_stamp": get_utc()},
                        {"status": 200}
                    ]
                    MQTTService.push_data_zip(mqtt_service,topic_project_information, data_send_topic_project_information)
                except Exception as err:
                    print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
        except Exception as err:
            data_send = {
                "mqtt": [
                        {"time_stamp" : get_utc()},
                        {"status":400}]
                        }
            MQTTService.push_data_zip(mqtt_service,topic_project_information,data_send)
    @staticmethod
    async def insertInformationProjectSetup(mqtt_service, messageInsertInformationProjectSetup, Topic_Project_Set_Feedback):
        try:
            # Tách thông tin mqtt từ thông tin được gửi
            resultSet = messageInsertInformationProjectSetup.get('parameter', {})
            resultSet.pop('mqtt', None)
            # Lọc các kết quả nhận được để tạo truy vấn cập nhật thông tin cơ sở dữ liệu
            if resultSet:
                update_fields = ", ".join([f"{field} = %s" for field in resultSet.keys()])
                update_values = list(resultSet.values())
                query = f"UPDATE project_setup SET {update_fields}"
                print("query",query)
                print("update_values",update_values)
                if query and update_values:
                    result = await MySQL_Update_v2(query, tuple(update_values))
                    current_time = get_utc()
                    if result is not None:
                        data_send = {
                            "status": 400,
                            "time_stamp": current_time
                        }
                    else:
                        data_send = {
                            "status": 200,
                            "time_stamp": current_time
                        }
                    MQTTService.push_data_zip(mqtt_service, Topic_Project_Set_Feedback, data_send)
        except Exception as err:
            print(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")