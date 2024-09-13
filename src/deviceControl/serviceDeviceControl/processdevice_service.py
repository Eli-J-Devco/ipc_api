# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from utils.MQTTService import *
from utils.libTime import *
from deviceControl.serviceDeviceControl.enegy_service import *
# ==================================================== Get List All Device ==================================================================
class ProcessSystem:
    def __init__(self):
        pass
        # Describe GetListAllDeviceMain 
    # 	 * @description GetListAllDeviceMain
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageAllDevice, topicFeedback ,resultDB}
    # 	 * @return result = {
    #     "ModeSystempCurrent": ModeSystem,
    #     "devices": ArrayDeviceList,
    #     "total_max_power": TotalPowerINV,
    #     "total_max_power_man": TotalPowerINVMan,
    #     "total_max_power_auto": TotalPowerINVAuto,
    #     "system_performance": {
    #         "performance": SystemPerformance,
    #         "message": statusString,
    #         "status": statusInt
    #     }
    # 	 */ 
    async def create_message_for_process_systemp(mqtt_service, messageAllDevice, topicFeedback ,resultDB):
        ArrayDeviceList = []
        TotalPowerINV = 0.0
        TotalPowerINVMan = 0.0
        ModeSystem = resultDB["mode"] 
        # Get Information about the device
        if messageAllDevice and isinstance(messageAllDevice, list):
            # Calculate Total Power 
            totalProduction, totalConsumption = await EnergySystem.calculate_production_and_consumption(messageAllDevice)
            device_auto_info = await ProcessAuto.get_parametter_device_list_auto_mode(messageAllDevice)
            TotalPowerINVAuto = ProcessAuto.calculate_total_power_inv_auto(device_auto_info)
            for item in messageAllDevice:
                device_info = ProcessSystem.get_device_details(item)
                if device_info:
                    ArrayDeviceList.append(device_info)
        # Calculate the sum of wmax values of all inv in the system
        TotalPowerINV, TotalPowerINVMan = ProcessSystem.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Call the update_system_performance function and get the return value
        SystemPerformance, statusString, statusInt = ProcessSystem.calculate_system_performance (
            resultDB,
            totalProduction,
            TotalPowerINV,
            totalConsumption
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
                "message": statusString,
                "status": statusInt
            }
        }
        # Public MQTT
        MQTTService.push_data_zip(mqtt_service, topicFeedback, result)
        MQTTService.push_data(mqtt_service, topicFeedback + "Binh", result)
    # Describe get_device_details 
    # 	 * @description get_device_details
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {item}
    # 	 * @return return {
                #     'id_device': id_device,
                #     'device_name': device_name,
                #     'mode': mode,
                #     'status_device': status_device,
                #     'operator': operator,
                #     'capacitypower': capacity_power,
                #     'p_max': p_max_custom,
                #     'p_min': p_min,
                #     'wmax': wmax,
                #     'realpower': real_power,
                #     'timestamp': get_utc(),
                # }
    # 	 */ 
    def get_device_details(item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom_temp = item['rated_power_custom']
            if p_max_custom_temp != None :
                p_max_custom = p_max_custom_temp
            else:
                p_max_custom = p_max
            p_min_percent = item['min_watt_in_percent']
            device_name = item['device_name']
            results_device_type = item['name_device_type']
            if results_device_type == "PV System Inverter":
                operator, wmax, capacity_power, real_power = ProcessSystem.get_operator_wmax_capacitypower_realpower(item)
                if status_device == 'offline':
                    real_power = 0.0
                    operator = "off"
                p_min = ProcessSystem.calculate_p_min(p_max_custom, p_min_percent)
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
    # Describe get_operator_wmax_capacitypower_realpower
    # 	 * @description get_device_parameters
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {item}
    # 	 * @return operator, wmax, capacity_power, real_power
    # 	 */ 
    @staticmethod
    def get_operator_wmax_capacitypower_realpower(item):
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
    # Describe calculate_total_wmax 
    # 	 * @description calculate_total_wmax
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {device_list, power_auto}
    # 	 * @return total_power, total_power_manual
    # 	 */ 
    @staticmethod
    def calculate_total_wmax(device_list, power_auto):
        total_power_write_inv = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None), 2)
        total_power_manual = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None and device['mode'] == 0), 2)
        total_power = round((total_power_manual + power_auto), 2)
        return total_power, total_power_manual
    # Describe calculate_p_min 
    # 	 * @description calculate_p_min
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {p_max_custom, p_min_percent}
    # 	 * @return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0
    # 	 */ 
    @staticmethod
    def calculate_p_min(p_max_custom, p_min_percent):
        return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0
    # Describe update_system_performance 
    # 	 * @description update_system_performance
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {resultDB, production_system, total_power_in_all_inv ,ValueConsumtion}
    # 	 * @return systemPerformance, statusString, statusInt
    # 	 */ 
    @staticmethod
    def calculate_system_performance (resultDB, production_system, total_power_in_all_inv ,ValueConsumtion):
        current_mode = resultDB["mode"] 
        mode_detail = resultDB["control_mode"] 
        low_performance_threshold = resultDB["low_performance"] 
        high_performance_threshold = resultDB["high_performance"] 
        Powerlimit = resultDB["value_power_limit"]
        ValueOffetConsump = resultDB["value_offset_zero_export"]
        # Calculate Power Limit
        ConsumptionAfterSudOfset = ValueConsumtion - (ValueConsumtion * ValueOffetConsump / 100) if ValueOffetConsump is not None else ValueConsumtion 
        if current_mode == 0: # Man
            systemPerformance = (production_system / total_power_in_all_inv) * 100 if total_power_in_all_inv else 0
        else:
            if mode_detail == 1: # Zero export
                systemPerformance = (production_system / ConsumptionAfterSudOfset) * 100 if ConsumptionAfterSudOfset > 0 else (101 if production_system > 0 else 0)
            else: # Power Limit 
                systemPerformance = (production_system / Powerlimit) * 100 if Powerlimit > 0 else (101 if production_system > 0 else 0)
        # Rounded results
        systemPerformance = round(systemPerformance, 1)
        if systemPerformance < low_performance_threshold:
            statusString = "System performance is below expectations."
            statusInt = 0
        elif low_performance_threshold <= systemPerformance < high_performance_threshold:
            statusString = "System performance is meeting"
            statusInt = 1
        else:
            statusString = "System performance is exceeding established thresholds."
            statusInt = 2
        return systemPerformance, statusString, statusInt
# ==================================================== Get List Auto Device ==================================================================
class ProcessAuto:
    def __init__(self):
        pass
    # Describe get_parametter_device_list_auto_mode 
    # 	 * @description get_parametter_device_list_auto_mode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageAllDevice}
    # 	 * @return ArayyDeviceList
    # 	 */ 
    @staticmethod
    async def get_parametter_device_list_auto_mode(messageAllDevice):
        ArayyDeviceList = []
        if messageAllDevice and isinstance(messageAllDevice, list):
            for item in messageAllDevice:
                device_info = ProcessAuto.get_device_auto_details(item)
                if not device_info:
                    continue
                # Get Information Each Device 
                id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type = device_info
                # Check Device Auto 
                if ProcessAuto.is_device_controlable(results_device_type, status_device, mode, operator):
                    ArayyDeviceList.append({
                        'id_device': id_device,
                        'mode': mode,
                        'status_device': status_device,
                        'p_max': p_max_custom,
                        'p_min': p_min,
                        'controlinv': value,
                        'operator': operator,
                        'slope': slope,
                    })
        return ArayyDeviceList
    # Describe extract_device_auto_info 
    # 	 * @description extract_device_auto_info
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageMQTT}
    # 	 * @return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
    # 	 */ 
    @staticmethod
    def get_device_auto_details(messageMQTT):
        if 'id_device' in messageMQTT and 'mode' in messageMQTT and 'status_device' in messageMQTT:
            id_device = messageMQTT['id_device']
            mode = messageMQTT['mode']
            status_device = messageMQTT['status_device']
            p_max = messageMQTT['rated_power']
            p_max_custom_temp = messageMQTT['rated_power_custom']
            if p_max_custom_temp != None :
                p_max_custom = p_max_custom_temp
            else:
                p_max_custom = p_max
            p_min_percent = messageMQTT['min_watt_in_percent']
            p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
            value = ProcessAuto.get_device_value(messageMQTT, "ControlINV")
            if value is None:
                return None
            operator = ProcessAuto.get_device_value(messageMQTT, "OperatingState")
            if operator is None:
                return None
            slope = ProcessAuto.get_device_value(messageMQTT, "WMax", field_key='slope')
            if slope is None:
                return None
            results_device_type = messageMQTT.get('name_device_type')
            if results_device_type is None:
                return None
            return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
        return None
    # Describe get_device_value 
    # 	 * @description get_device_value
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {item, point_key, field_key='value'}
    # 	 * @return value of field_key
    # 	 */ 
    @staticmethod
    def get_device_value(item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None
    # Describe is_device_controlable 
    # 	 * @description is_device_controlable
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {results_device_type, status_device, mode, operator}
    # 	 * @return conditon divece is auto
    # 	 */ 
    @staticmethod
    def is_device_controlable(results_device_type, status_device, mode, operator):
        return (results_device_type == "PV System Inverter" and 
                status_device == 'online' and 
                mode == 1 and 
                operator not in [7, 8])
    # Describe calculate_total_power_inv_auto 
    # 	 * @description calculate_total_power_inv_auto
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {ArayyDeviceList}
    # 	 * @return total_power
    # 	 */ 
    @staticmethod
    def calculate_total_power_inv_auto(ArayyDeviceList):
        if ArayyDeviceList:
            total_power = round(sum(device['p_max'] for device in ArayyDeviceList if device['p_max'] is not None), 2)
            return total_power
        return 0
    