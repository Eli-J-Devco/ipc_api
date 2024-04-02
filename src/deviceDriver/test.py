from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

def write_modbus_tcp(client, unit, datatype, register, value):
    try:
        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        match datatype:
            case 3:  # Short Signed 16-bit
                builder.add_16bit_int(int(value))
            case 4:  # Word Unsigned 16-bit
                builder.add_16bit_uint(int(value))
            case 5:  # Long Signed 32-bit
                builder.add_32bit_int(int(value))
            case 6:  # DWord Unsigned 32-bit
                builder.add_32bit_uint(int(value))
            case 7:  # LLong Signed 64-bit
                builder.add_64bit_int(int(value))
            case 8:  # QWord Unsigned 64-bit
                builder.add_64bit_uint(int(value))
            case 9:  # Float 32-bit real value IEEE-754
                builder.add_32bit_float(float(value))
            case 10:  # Double 64-bit real value
                builder.add_64bit_float(float(value))
            case _:
                pass
        
        payload = builder.build()
        address = register
        result = client.write_registers(address, payload, skip_encode=True, unit=unit)
        print(f'result: {result.function_code}')
        
        if result.function_code == 16:
            msg = {
                "msg": f"Write success to INV-{register}",
                "code": result.function_code,
                "value": 0
            }
        else:
            msg = {
                "msg": f"Write error to INV-{register}",
                "code": result.function_code,
                "value": 1
            }
        
        return msg
    except Exception as err:
        print(f'Error write_modbus_tcp : {err}')
        return {
            "msg": err,
            "code": "",
            "value": 2
        }

def main():
    client = ModbusTcpClient("127.0.0.2")
    unit = 1
    datatype = 3
    registers = [0, 2, 4, 6, 8]
    values = [100, 101, 102, 103, 104]  # Giá trị cần ghi cho từng thanh ghi

    for register, value in zip(registers, values):
        result = write_modbus_tcp(client, unit, datatype, register, value)
        print(result)

if __name__ == "__main__":
    main()
