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
from deviceControl.energyMonitor.energy_service import *
from deviceControl.processSystem.process_service import *
class PowerCalculator :
    def __init__(self):
        self.mqtt_topic_sud = MQTTTopicSUD()
        self.mqtt_topic_push = MQTTTopicPUSH()
        self.ennergy_instance = EnergySystem()
        self.process_system_instance = ProcessSystem()
        self.process_auto_instance = ProcessAuto(self.process_system_instance)
    # Describe automatedParameterManagement 
    # 	 * @description automatedParameterManagement
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB}
    # 	 * @return 
    # 	 */ 
    async def calculate_auto_parameters(self,mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
        # Select the auto run process
        if resultDB["control_mode"] == 1 :
            print("==============================zero_export==============================")
            await self.calculate_zero_export_mode (mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
        else:
            print("==============================power_limit==============================")
            await self.calculate_power_limit_mode (mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB)
    # Describe processCaculatorPowerForInvInPowerLimitMode 
    # 	 * @description processCaculatorPowerForInvInPowerLimitMode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB}
    # 	 * @return 
    # 	 */ 
    async def calculate_power_limit_mode (self,mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
        Arraydevices = []
        ArrayDeviceList = []
        gIntValuePowerForEachInvInModePowerLimit = 0 
        PowerlimitCaculator = resultDB["value_power_limit"]
        ModeSystem = resultDB["mode"]
        ModeDetail = resultDB["control_mode"]
        # Get List Device Can Control 
        if messageMQTTAllDevice:
            # Calculate Total Power 
            totalProduction, totalConsumption = await self.ennergy_instance.calculate_production_and_consumption(messageMQTTAllDevice)
            # Calculate Power Of INV AutoMode
            Arraydevices = await self.process_auto_instance.get_parametter_device_list_auto_mode(messageMQTTAllDevice)
            TotalPowerINVAuto = self.process_auto_instance.calculate_total_power_inv_auto(Arraydevices)
            # Extract device info
            ArrayDeviceList = [self.process_system_instance.get_device_details(item) for item in messageMQTTAllDevice if self.process_system_instance.get_device_details(item)]
            # Calculate the sum of wmax values of all inv in the system
            TotalPowerINVAll, TotalPowerINVMan = self.process_system_instance.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Get Infor Device Control 
        if Arraydevices:
            listInvControlPowerLimitMode = []
            for device in Arraydevices:
                id_device, mode, intPowerMaxOfInv = self.extract_device_info (device)
                gIntValuePowerForEachInvInModePowerLimit = self.calculate_power_value(intPowerMaxOfInv,ModeSystem,TotalPowerINVMan,\
                    TotalPowerINVAuto,PowerlimitCaculator)
                # Create Infor Device Publish MQTT
                if totalProduction < PowerlimitCaculator:
                    item = self.create_control_item(ModeDetail,device, gIntValuePowerForEachInvInModePowerLimit,PowerlimitCaculator,\
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
    # Describe processCaculatorPowerForInvInZeroExportMode 
    # 	 * @description processCaculatorPowerForInvInZeroExportMode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
    # 	 * @return PowerForEachInvInModeZeroExport
    # 	 */ 
    async def calculate_zero_export_mode (self,mqtt_service,messageMQTTAllDevice,Topic_Control_WriteAuto,resultDB):
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
            totalProduction, totalConsumption = await self.ennergy_instance.calculate_production_and_consumption(messageMQTTAllDevice)
            # Calculate Power Of INV AutoMode
            Arraydevices = await self.process_auto_instance.get_parametter_device_list_auto_mode(messageMQTTAllDevice)
            TotalPowerINVAuto = self.process_auto_instance.calculate_total_power_inv_auto(Arraydevices)
            # Extract device info
            ArrayDeviceList = [self.process_auto_instance.get_device_details(item) for item in messageMQTTAllDevice if self.process_auto_instance.get_device_details(item)]
            # Calculate the sum of wmax values of all inv in the system
            TotalPowerINVAll, TotalPowerINVMan = self.process_auto_instance.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Get Setpoint ,Value Consumption System 
        if totalConsumption:
            Setpoint, PracticalConsumptionValue = await self.calculate_setpoint(ModeSystem,totalConsumption,TotalPowerINVMan,OffsetZeroExport)
        if Arraydevices:
            listInvControlZeroExportMode = []
            for device in Arraydevices:
                id_device, mode, intPowerMaxOfInv = self.extract_device_info (device)
                PowerForEachInvInModeZeroExport = self.calculate_power_value(intPowerMaxOfInv, ModeSystem, 
                    TotalPowerINVMan, TotalPowerINVAuto, Setpoint)
                # Create Infor Device Publish MQTT
                if totalProduction < PracticalConsumptionValue and \
                    totalConsumption >= ThresholdZeroExport and totalConsumption >= 0:
                    item = self.create_control_item(ModeDetail,device, PowerForEachInvInModeZeroExport,Setpoint,\
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
    # Describe process_device_powerlimit_info 
    # 	 * @description process_device_powerlimit_info
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {device}
    # 	 * @return id_device, mode, intPowerMaxOfInv
    # 	 */ 
    @staticmethod
    def extract_device_info (device):
        id_device = device["id_device"]
        mode = device["mode"]
        intPowerMaxOfInv = float(device["p_max"])
        return id_device, mode, intPowerMaxOfInv
    # Describe calculate_device_power 
    # 	 * @description calculate_power_value
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {intPowerMaxOfInv, modeSystem, TotalPowerInInvInManMode, TotalPowerInInvInAutoMode, Setpoint}
    # 	 * @return intPowerMaxOfInv
    # 	 */ 
    @staticmethod
    def calculate_power_value(intPowerMaxOfInv, modeSystem, TotalPowerInInvInManMode, TotalPowerInInvInAutoMode, Setpoint):
        # Calculate performance for equipment
        if modeSystem == 1:
            Efficiency = (Setpoint / TotalPowerInInvInAutoMode)
        else:
            Efficiency = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
        # The power of a device is equal to its efficiency multiplied by its maximum power.
        if 0 <= Efficiency <= 1:
            return Efficiency * intPowerMaxOfInv
        elif Efficiency < 0:
            return 0
        else:
            return intPowerMaxOfInv
    # Describe create_control_message 
    # 	 * @description create_control_item
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {ModeSystemDetail ,device, PowerForEachInv, Setpoint, TotalPowerInInvInManMode, ValueProduction}
    # 	 * @return ItemlistInvControlPowerLimitMode
    # 	 */ 
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
        # create item list for device
        if device['controlinv'] == 1:
            ItemlistInvControlPowerLimitMode["parameter"].append({"id_pointkey": "WMax", "value": PowerForEachInv})
        elif device['controlinv'] == 0:
            ItemlistInvControlPowerLimitMode["parameter"].extend([
                {"id_pointkey": "ControlINV", "value": 1},
                {"id_pointkey": "WMax", "value": PowerForEachInv}
            ])
        return ItemlistInvControlPowerLimitMode
    async def calculate_setpoint(self, modeSystem, ValueConsump, ValueTotalPowerInInvInManMode, ValueOffetConsump):
        ConsumptionAfterSudOfset = 0.0
        gMaxValueChangeSetpoint = 10 
        # minus man value
        if modeSystem == 1:
            ValueConsump
        else:
            ValueConsump -= ValueTotalPowerInInvInManMode
        
        if not hasattr(self.calculate_setpoint, 'last_setpoint'):
            self.calculate_setpoint.last_setpoint = ValueConsump
        # setpoint value change limit
        new_setpoint = ValueConsump
        Setpoint = max(
            self.calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
            min(self.calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        self.calculate_setpoint.last_setpoint = Setpoint
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump) / 100)
        if Setpoint:
            Setpoint -= Setpoint * ValueOffetConsump / 100
        return Setpoint, ConsumptionAfterSudOfset
    
class MQTTHandlerPowerCalculator(PowerCalculator):
    def __init__(self, power_caculator_instance):
        self.power_caculator_instance = power_caculator_instance
        
    async def subscribe_to_mqtt_topics(self,mqtt_service,serial,setup_site_instance):
        try:
            client = mqttools.Client(
                host=mqtt_service.host,
                port=mqtt_service.port,
                username=mqtt_service.username,
                password=bytes(mqtt_service.password, 'utf-8'),
                subscriptions=mqtt_service.topics,
                connect_delays=[1, 2, 4, 8]
            )
            while True :
                await client.start()
                await self.consume_mqtt_messages(mqtt_service, client,serial,setup_site_instance)
                await client.stop()
        except Exception as err:
            print(f"Error subscribing to MQTT topics: '{err}'")
    
    async def consume_mqtt_messages(self,mqtt_service, client,serial,setup_site_instance):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                topic = message.topic
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service,payload,topic,serial,setup_site_instance)
        except Exception as err:
            print(f"Error consuming MQTT messages: '{err}'")
    
    async def handle_mqtt_message(self, mqtt_service, message,topic, serial,setup_site_instance):
        try:
            resultDB = await setup_site_instance.get_project_setup_values()
            if message and resultDB:
                await self.power_caculator_instance.calculate_auto_parameters(mqtt_service, message, self.power_caculator_instance.mqtt_topic_push.Control_WriteAuto, resultDB)
                print("write auto parameters")
        except Exception as err:
            print(f"Error handling MQTT message: '{err}'")