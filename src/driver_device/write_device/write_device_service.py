import base64
import datetime
import gzip
import json
from typing import Any, Optional

from pymodbus.client import AsyncModbusTcpClient, ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

from src.driver_device.write_device.write_device_model import \
    WriteParameter as WriteParameterModel
from src.driver_device.write_device.write_device_model import \
    WritePointStatus as WritePointStatus
from src.driver_device.write_device.write_device_model import WriteStatus
from src.driver_device.write_device.write_device_model import Action,FeedbackWeb
from src.mqtt_client.mqtt_client_service import MQTTClientService
from src.mqtt_client.mqtt_client_model import MQTTConfigBase, MQTTMsg, MQTTMsgs
from src.utils.utils import getUTC
class WriteDeviceService():
    def __init__(self,
                 mqtt_config:MQTTConfigBase,
                 id_device,
                 **kwargs):
        self.mqtt_config=mqtt_config
        self.id_device=id_device
        self.mqtt_client=MQTTClientService(mqtt_config=self.mqtt_config)
    async def write_point(self,client:AsyncModbusTcpClient, 
                            slave: Any, 
                            datatype=None, 
                            modbus_func=None,
                            register=None, 
                            value=None
                            ):
        try:
            msg=None
            print(f'datatype: {datatype}|modbus_func: {modbus_func}|value: {value}')
            builder = BinaryPayloadBuilder(
            byteorder=Endian.BIG)
            match datatype:
                case 3: # Short Signed 16-bit
                    builder.add_16bit_int(int(value))
                case 4: # Word Unsigned 16-bit
                    builder.add_16bit_uint(int(value))
                case 5: # Long Signed 32-bit
                    builder.add_32bit_int(int(value))
                case 6: # DWord Unsigned 32-bit
                    builder.add_32bit_uint(int(value))
                case 7: # LLong Signed 64-bit
                    builder.add_64bit_int(int(value))
                case 8: # QWord Unsigned 64-bit
                    builder.add_64bit_uint(int(value))
                case 9: # Float 32-bit real value IEEE-754
                    builder.add_32bit_float(float(value))
                case 10: # Double 64-bit real value
                    builder.add_64bit_float(float(value))
                case _:
                    pass
            payload = builder.build()
            address=register
            
            match modbus_func:
                case 3:
                    result =await client.write_registers(
                    address, payload, skip_encode=True, slave=slave)
                    if hasattr(result, "function_code"):
                        print(f'result: {result.function_code }')
                        if result.function_code == 16:
                            msg=WritePointStatus(msg="Write success",
                                            code=result.function_code,
                                            status=0,
                                            address=address
                                            )
                        else:
                            msg=WritePointStatus(msg="Write error",
                                            code=result.function_code,
                                            status=1,
                                            address=address
                                            )
                        return msg
        except Exception as e:
            print('Error write_point :', e)
        finally:
            return msg
        
    async def write_modbus_tcp(self,client:AsyncModbusTcpClient, slave: int, parameter: WriteParameterModel):
        write_status:WriteStatus =None
        try:
            # control_devices=list(map(lambda item: ControlDevice(**item), device_data))
            write_point_status:list[WritePointStatus]=[]
            for point in parameter.parameter:
                # print(f'point: {point}')
                result_write_point=await self.write_point(client=client,slave=slave,
                                        datatype=point.datatype,
                                        modbus_func=point.modbus_func,
                                        register=point.register_value,
                                        value=point.value
                                        )
                write_point_status.append(WritePointStatus(**result_write_point.dict()))
                # print(f'result_write: {result_write}')
            print(f'write_point_status: {write_point_status}')
            # [item for item in mppt_volt if item.quality== 1]
            if not write_point_status:
                return                
            result: list=[item for item in write_point_status if item.status == 0]
            
            if result:
                results=WritePointStatus(**result[0].__dict__)
                write_status=WriteStatus(**results.dict(exclude={"status","address","code"}),
                                        status=200,
                                        address=None,
                                        code=None
                                        )
            else:
                write_status=WriteStatus(status=400)
        except Exception as e:
            print('Error write_modbus_tcp :', e)
        finally:
            result_data:FeedbackWeb=FeedbackWeb(time_stamp=getUTC(),status=write_status.status,token=parameter.token,id_device=parameter.id_device)
            msgs=[MQTTMsg(topic=f'{self.mqtt_config.serial_number}/{Action.PathTopicFeedBackWeb.value}',payload= result_data)]
            self.mqtt_client.public_multi_paho_zip(messages=MQTTMsgs(msgs=msgs),encode=False)
            
            return write_status
        