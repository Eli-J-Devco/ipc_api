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
from deviceControl.serviceDeviceControl.enegy_service import *
from deviceControl.serviceDeviceControl.processdevice_service import *
# ==================================================== Caculator PowerLit And ZeroExport  ==================================================================
class caculatorPowerClass:
    def __init__(self):
        pass
    async def automatedParameterManagement(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
        # Select the auto run process
        if resultDB["control_mode"] == 1 :
            print("==============================zero_export==============================")
            await caculatorPowerClass.processCaculatorPowerForInvInZeroExportMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
        else:
            print("==============================power_limit==============================")
            await caculatorPowerClass.processCaculatorPowerForInvInPowerLimitMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
    ############################################################################ Power Limit Control  ############################################################################
    # Describe processCaculatorPowerForInvInPowerLimitMode 
    # 	 * @description processCaculatorPowerForInvInPowerLimitMode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
    # 	 * @return gIntValuePowerForEachInvInModePowerLimit
    # 	 */ 
    async def processCaculatorPowerForInvInPowerLimitMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
        # Local variables
        Arraydevices = []
        ArrayDeviceList = []
        gIntValuePowerForEachInvInModePowerLimit = 0 
        Powerlimit = resultDB["value_power_limit"]
        PowerLimitOffset = resultDB["value_offset_power_limit"]
        ModeSystem = resultDB["mode"]
        ModeDetail = resultDB["control_mode"]
        # Calculate Power Limit
        PowerlimitCaculator = Powerlimit - (Powerlimit * PowerLimitOffset / 100) if PowerLimitOffset is not None else Powerlimit
        # Get List Device Can Control 
        if messageMQTTAllDevice:
            # Calculate Total Power 
            totalProduction, totalConsumption = await ValueEnergySystemClass.calculate_production_and_consumption(messageMQTTAllDevice)
            # Calculate Power Of INV AutoMode
            Arraydevices = await GetListAutoDeviceClass.getListDeviceAutoModeInALLInv(messageMQTTAllDevice)
            TotalPowerINVAuto = GetListAutoDeviceClass.calculate_total_power_inv_auto(Arraydevices)
            # Extract device info
            ArrayDeviceList = [GetListAllDeviceClass.extract_device_all_info(item) for item in messageMQTTAllDevice if GetListAllDeviceClass.extract_device_all_info(item)]
            # Calculate the sum of wmax values of all inv in the system
            TotalPowerINVAll, TotalPowerINVMan = GetListAllDeviceClass.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Get Infor Device Control 
        if Arraydevices:
            listInvControlPowerLimitMode = []
            for device in Arraydevices:
                id_device, mode, intPowerMaxOfInv = caculatorPowerClass.process_device_powerlimit_info(device)
                gIntValuePowerForEachInvInModePowerLimit = caculatorPowerClass.calculate_power_value(intPowerMaxOfInv,ModeSystem,TotalPowerINVMan,\
                    TotalPowerINVAuto,PowerlimitCaculator)
                # Create Infor Device Publish MQTT
                if totalProduction < PowerlimitCaculator:
                    item = caculatorPowerClass.create_control_item(ModeDetail,device, gIntValuePowerForEachInvInModePowerLimit,PowerlimitCaculator,\
                        TotalPowerINVMan,totalProduction)
                else:
                    item = {
                        "id_device": id_device,
                        "mode": mode,
                        "status": "power limit",
                        "setpoint": PowerlimitCaculator - TotalPowerINVMan,
                        "feedback": totalProduction,
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": max(0, gIntValuePowerForEachInvInModePowerLimit - (totalProduction - PowerlimitCaculator))}
                        ]
                    }
                # Create List Device 
                listInvControlPowerLimitMode.append(item)
            # Push MQTT
            if len(Arraydevices) == len(listInvControlPowerLimitMode):
                MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlPowerLimitMode)
                MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto + "Binh",listInvControlPowerLimitMode)
    ############################################################################ Zero Export Control ############################################################################
    # Describe processCaculatorPowerForInvInZeroExportMode 
    # 	 * @description processCaculatorPowerForInvInZeroExportMode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
    # 	 * @return PowerForEachInvInModeZeroExport
    # 	 */ 
    async def processCaculatorPowerForInvInZeroExportMode(mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
        # Local variables
        Arraydevices = []
        ArrayDeviceList = []
        PowerForEachInvInModeZeroExport = 0
        PracticalConsumptionValue = 0.0
        Setpoint = 0 
        ModeSystem = resultDB["mode"]
        ModeDetail = resultDB["control_mode"]
        ThresholdZeroExport = resultDB.get("threshold_zero_export") or 0.0
        OffsetZeroExport = resultDB.get("value_offset_zero_export") or 0.0
        # Get List Device Can Control 
        if messageMQTTAllDevice:
            # Calculate Total Power 
            totalProduction, totalConsumption = await ValueEnergySystemClass.calculate_production_and_consumption(messageMQTTAllDevice)
            # Calculate Power Of INV AutoMode
            Arraydevices = await GetListAutoDeviceClass.getListDeviceAutoModeInALLInv(messageMQTTAllDevice)
            TotalPowerINVAuto = GetListAutoDeviceClass.calculate_total_power_inv_auto(Arraydevices)
            # Extract device info
            ArrayDeviceList = [GetListAllDeviceClass.extract_device_all_info(item) for item in messageMQTTAllDevice if GetListAllDeviceClass.extract_device_all_info(item)]
            # Calculate the sum of wmax values of all inv in the system
            TotalPowerINVAll, TotalPowerINVMan = GetListAllDeviceClass.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Get Setpoint ,Value Consumption System 
        if totalConsumption:
            Setpoint, PracticalConsumptionValue = await caculatorPowerClass.calculate_setpoint(ModeSystem,totalConsumption,TotalPowerINVMan,OffsetZeroExport)
        if Arraydevices:
            listInvControlZeroExportMode = []
            for device in Arraydevices:
                id_device, mode, intPowerMaxOfInv = caculatorPowerClass.process_device_powerlimit_info(device)
                PowerForEachInvInModeZeroExport = caculatorPowerClass.calculate_power_value(intPowerMaxOfInv, ModeSystem, 
                    TotalPowerINVMan, TotalPowerINVAuto, Setpoint)
                # Create Infor Device Publish MQTT
                if totalProduction < PracticalConsumptionValue and \
                    totalConsumption >= ThresholdZeroExport and totalConsumption >= 0:
                    item = caculatorPowerClass.create_control_item(ModeDetail,device, PowerForEachInvInModeZeroExport,Setpoint,\
                    TotalPowerINVMan,totalProduction)
                else:
                    item = {
                        "id_device": id_device,
                        "mode": mode,
                        "status": "zero export",
                        "setpoint": Setpoint,
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": 0}
                        ]
                    }
                # Create List Device 
                listInvControlZeroExportMode.append(item)
            # Push MQTT
            if len(Arraydevices) == len(listInvControlZeroExportMode):
                MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlZeroExportMode)
                MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto + "Binh",listInvControlZeroExportMode)
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
            Efficiency = (Setpoint / TotalPowerInInvInAutoMode)
        else:
            Efficiency = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
        # Công suất của thiết bị bằng hiệu suất nhân với công suất tối đa.
        if 0 <= Efficiency <= 1:
            return Efficiency * intPowerMaxOfInv
        elif Efficiency < 0:
            return 0
        else:
            return intPowerMaxOfInv
    @staticmethod
    def create_control_item(ModeSystemDetail ,device, PowerForEachInv, Setpoint, TotalPowerInInvInManMode, ValueProduction):
        if ModeSystemDetail == 1 :
            status = "Zero Export"
        else:
            status = "Power Limit"
        id_device = device["id_device"]
        mode = device["mode"]
        ItemlistInvControlPowerLimitMode = {
            "id_device": id_device,
            "mode": mode,
            "time": get_utc(),
            "status": status,
            "setpoint": Setpoint - TotalPowerInInvInManMode,
            "feedback": ValueProduction,
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
    async def calculate_setpoint( modeSystem, ValueConsump, ValueTotalPowerInInvInManMode, ValueOffetConsump):
        ConsumptionAfterSudOfset = 0.0
        gMaxValueChangeSetpoint = 10 
        # minus man value
        if modeSystem == 1:
            ValueConsump
        else:
            ValueConsump -= ValueTotalPowerInInvInManMode
        
        if not hasattr(caculatorPowerClass.calculate_setpoint, 'last_setpoint'):
            caculatorPowerClass.calculate_setpoint.last_setpoint = ValueConsump
        # setpoint value change limit
        new_setpoint = ValueConsump
        Setpoint = max(
            caculatorPowerClass.calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
            min(caculatorPowerClass.calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        caculatorPowerClass.calculate_setpoint.last_setpoint = Setpoint
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump) / 100)
        if Setpoint:
            Setpoint -= Setpoint * ValueOffetConsump / 100
        return Setpoint, ConsumptionAfterSudOfset

    
