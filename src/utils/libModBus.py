
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

# Describe funtion wwrite in device modbus TCP 
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
def write_modbus_tcp(client, unit, datatype,register, value):
    try:
        builder = BinaryPayloadBuilder(
        byteorder=Endian.Big)
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
        result = client.write_registers(
        address, payload, skip_encode=True, unit=unit)
        print(f'result: {result.function_code }')
        if result.function_code == 16:
            msg ={ "msg":"Write success to INV-"+str(register),
                "code":result.function_code,
                "value":0
                }
        else:
            msg ={ "msg":"Write error to INV-"+str(register),
                "code":result.function_code,
                "value":1
                }
        return msg
    except Exception as err:
        print(f'Error write_modbus_tcp : {err}')
        return {
                "msg":err,
                "code":"",
                "value":2
            }