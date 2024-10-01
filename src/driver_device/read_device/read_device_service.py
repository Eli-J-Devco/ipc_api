
import datetime
import time

from pymodbus.client import AsyncModbusTcpClient  # ModbusTcpClient,
from pymodbus.constants import Endian
from pymodbus.exceptions import (ConnectionException, ModbusException,
                                 ModbusIOException)
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.driver_device.read_device.read_device_model import (
    MergeRegisterDevice, PointDataBase, PointDataOut, ReadRegisterDevice,
    RegisterData, RegisterValueDevice, StatusRB)
from src.utils.device_point.device_point_model import (DevicePointBase,
                                                       DevicePointsOutput)
from src.utils.utils import getUTC

from ...utils.register_block.register_block_model import RegisterBlockOutput


class ReadDeviceService:
    def __init__(self,job_id,job_events={}, **kwargs):
        self.job_id=job_id
        self.job_events=job_events
        # self.client=client
    
    def scaling_modbus(self,slopeenabled: int,
                    slope,
                    offsetenabled: int,
                    offset,
                    value): #multiply by constant
        result= None
        if slopeenabled==1:
            result=value*slope
        else:
            result=value
        
        if offsetenabled==1:
            result=result+offset
        else:
            result=result
            
        return result 
    
    def check_float_modbus(self,value): #Check if a number is int or float
        result= None
        if type(value) == float:
            result=round(value,2)
        else:
            result=value
        return result
    
    def exception_code_modbus(self,exception_code: any):
        try:
            code_desc=""
            match exception_code :
                case 1:
                    code_desc=  "IllegalFunction"
                case 2:
                    code_desc= "IllegalAddress"
                case 3:
                    code_desc= "IllegalValue"
                case 4:
                    code_desc= "SlaveFailure"
                case 5:
                    code_desc= "Acknowledge"
                case 6:
                    code_desc= "SlaveBusy"
                case 8:
                    code_desc= "MemoryParityError"
                case 10:
                    code_desc= "GatewayPathUnavailable"
                case 11:
                    code_desc= "GatewayNoResponse"
        except Exception as err:
            print(f"Error exception_code_modbus: '{err}'")   
        finally:
            return code_desc
    
    async def read_register_device( self,client: AsyncModbusTcpClient, 
                                func: int, 
                                address: int, 
                                count: int, 
                                slave_id: int):
        result_rb=None
        addr =address
        
        try:
            match func:
                case 0:# not used           
                    result_rb = None
                case 1:# Read Coils
                    # 0x
                    # addr = address                        
                    result_rb = await client.read_coils(
                                    address=addr, count=count, slave=slave_id)
                    # return result_rb
                case 2:# Read Discrete Inputs
                    #  1x 
                    # addr = address #-10000
                    result_rb =await client.read_discrete_inputs(
                                        address=addr, count=count, slave=slave_id)
                    # return result_rb
                
                case 3:# Read Holding Registers
                    # 4x
                    # addr = address #-40000
                    result_rb =await client.read_holding_registers(
                                        address=addr, count=count, slave=slave_id)
                    # return result_rb

                case 4:# Read Input Registers
                    # 3x
                    # addr = address #-30000
                    result_rb =await client.read_input_registers(
                                        address=addr, count=count, slave=slave_id)
                    # return result_rb
                case _:
                    result_rb = None
            #
            if isinstance(result_rb, ModbusIOException):
                return ReadRegisterDevice(code=404,data=[],exception_code=result_rb,address=addr)
            elif hasattr(result_rb, "function_code"): 
                if hasattr(result_rb, "exception_code"):
                    desc=self.exception_code_modbus(result_rb.exception_code)
                    return ReadRegisterDevice(code=result_rb.function_code,data=[],exception_code=desc,address=addr)
                elif hasattr(result_rb, "registers"):
                    return ReadRegisterDevice(code=100,data=result_rb.registers,exception_code="",address=addr)
        except Exception as err:
            return ReadRegisterDevice(code=404,data=[],exception_code=str(err),address=addr)
        finally:
            pass
        
    def merge_register_device(self,func: int, addr: int, register_block:ReadRegisterDevice):
        try:
            inc = addr
            data=[]
            status_rb=[]
            status_device=""
            match register_block.code:
                case None:
                    status_device="offline"
                case 404:
                    status_device="offline"
                    status_rb.append(StatusRB(address=addr,error_code=404,timestamp=getUTC()))
                case 131:
                    exception_code=register_block.exception_code
                    if exception_code=="GatewayNoResponse":
                        status_device="offline"                                     
                        status_rb.append(StatusRB(address=addr,error_code=139,timestamp=getUTC()))
                    else:
                        status_device="online"
                        status_rb.append(StatusRB(address=addr,error_code=exception_code,timestamp=getUTC()))
                case 100:
                        status_device="online"
                        if register_block.data:
                            for itemR in register_block.data:
                                data.append(RegisterData(mra=inc,value=itemR,func=func))
                                inc +=1
        except Exception as err:
            print(f"Error register_data_modbus: '{err}'")   
        finally:
            return MergeRegisterDevice(status_device = status_device, status_rb = status_rb, data = data)
    
    async def read_data_device(self,
                            connected: bool,
                            client: AsyncModbusTcpClient,
                            slave_id : int,
                            register_blocks:RegisterBlockOutput):
        lazy_error_count = 2
        data_rb=[]
        status_rb=[]
        data_merge=[]
        read_status_rb=[]
        status_device=""
        message=""
        if connected==False:
            status_device="offline"
            message="Connection to client failed: timed out"
            return RegisterValueDevice(data=data_merge,status_rb=status_rb, read_status_rb=read_status_rb,status_device=status_device,timestamp=getUTC(),message=message)
        if not register_blocks:
            status_device="offline"
            message="Register block not created yet"
            return RegisterValueDevice(data=data_merge,status_rb=status_rb, read_status_rb=read_status_rb,status_device=status_device,timestamp=getUTC(),message=message)
        # while lazy_error_count > 0:
        try:
            data_rb=[]
            status_rb=[]
            data_merge=[]
            read_status_rb=[]
            status_device=""

            for item in register_blocks.registerblock:
                if not self.job_events.get(self.job_id, True):
                    return
                func_modbus=item.Functions
                result_rb = await self.read_register_device( client=client,
                                                    func=func_modbus,
                                                    address=item.addr,
                                                    count=item.count, 
                                                    slave_id=slave_id)
                result_rb_device= self.merge_register_device(
                                                    func=func_modbus,
                                                    addr=item.addr,
                                                    register_block=result_rb)
                if result_rb_device.data:
                    for item_data in result_rb_device.data:
                        data_rb.append(item_data)
                if result_rb_device.status_rb:
                    for item_data in result_rb_device.status_rb:
                        status_rb.append(item_data)
                if result_rb_device.status_device:
                    read_status_rb.append(result_rb_device.status_device)
            if data_rb:
                data_merge = [x for i, x in enumerate(data_rb) if x.mra not in {y.mra for y in data_rb[:i]}]            
        except Exception as exc:
            print(f"Error: exception lazy({lazy_error_count}) {exc}")
            lazy_error_count -= 1
                # continue
            # break
        # if not lazy_error_count:
        #     raise RuntimeError("HARD ERROR, more than 2 retries!")
        if "online" in read_status_rb:
            status_device="online"
        else:
            status_device="offline"
        return RegisterValueDevice(data=data_merge,
                                status_rb=status_rb, 
                                read_status_rb=read_status_rb,
                                status_device=status_device,
                                message=message,
                                timestamp=getUTC())
    
    def point_data(self,point: PointDataBase):
        timestamp=(lambda x:  getUTC() if x ==None else x) (point.timestamp)
        return PointDataBase(**point.dict(exclude={"timestamp"}),timestamp=timestamp )
    
    def convert_from_registers(self,point:DevicePointBase,register_data_device:RegisterValueDevice):
        try:
            # ----------------------------------------------------
            data_have=0
            point_value :int = None
            message=""
            quality=1
            value=None
            
            # ----------------------------------------------------
            if register_data_device:
                match point.value_datatype:
                    case 3: # Short Signed 16-bit
                        result = []
                        for itemD in register_data_device.data:
                            if point.register_value == itemD.mra and point.func == itemD.func:
                                result.append(int(itemD.value))
                        # print(f'result: --- {result}')        
                        if len(result) > 0:
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_16bit_int()
                            data_have=1
                        else:
                            data_have=0
                    case 4: # Word Unsigned 16-bit
                        result = []
                        point_value :int = None
                        for itemD in register_data_device.data:
                            if point.register_value == itemD.mra and point.func == itemD.func:
                                result.append(int(itemD.value))
                        # print(f'result: --- {result}')        
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_16bit_uint()
                            data_have=1
                        else:
                            data_have=0
                    case 5: # Long Signed 32-bit
                        
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point.register_value)
                        
                        if R1:
                            R2=R1+1
                            Rn.append({
                                "register":R1,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R2,
                                "func":point.func
                            })
                        for item in Rn:
                            for itemD in register_data_device.data:
                                if item["register"] == itemD.mra and item['func'] == itemD.func:
                                    result.append(int(itemD.value))      

                        if len(result) > 0:
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            
                            point_value = decoder.decode_32bit_int()
                            
                            data_have=1
                        else:
                            data_have=0
                        
                    case 6: # DWord Unsigned 32-bit
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point.register_value)
                        if R1:
                            R2=R1+1
                            Rn.append({
                                "register":R1,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R2,
                                "func":point.func
                            })
                        for item in Rn:
                            for itemD in register_data_device.data:
                                if item["register"] == itemD.mra and item['func'] == itemD.func:
                                    result.append(int(itemD.value)) 
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_32bit_uint()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 7: # LLong Signed 64-bit
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point.register_value)
                        if R1:
                            R2=R1+1
                            R3=R1+2
                            R4=R1+3
                            
                            # Rn.append(R1)
                            # Rn.append(R2)
                            # Rn.append(R3)
                            # Rn.append(R4)
                            Rn.append({
                                "register":R1,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R2,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R3,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R4,
                                "func":point.func
                            })
                        for item in Rn:
                            for itemD in register_data_device.data:
                                if item["register"] == itemD.mra and item['func'] == itemD.func:
                                    result.append(int(itemD.value))    
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_64bit_int()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 8: # QWord Unsigned 64-bit 
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point.register_value)
                        if R1:
                            R2=R1+1
                            R3=R1+2
                            R4=R1+3
                            
                            # Rn.append(R1)
                            # Rn.append(R2)
                            # Rn.append(R3)
                            # Rn.append(R4)
                            Rn.append({
                                "register":R1,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R2,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R3,
                                "func":point.func
                            })
                            Rn.append({
                                "register":R4,
                                "func":point.func
                            })
                        for item in Rn:
                            for itemD in register_data_device.data:
                                if item["register"] == itemD.mra and item['func'] == itemD.func:
                                    result.append(int(itemD.value))    
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_64bit_uint()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 9: # Float 32-bit real value IEEE-754       
                        
                        result = []
                        point_value : float = None
                        for itemD in register_data_device.data:
                            if point.register_value == itemD.mra and point.func == itemD.func:
                                result.append(int(itemD.value))
                        for itemD in register_data_device.data:
                            if point.register_value+1 == itemD.mra and point.func == itemD.func:
                                result.append(int(itemD.value))
                        if len(result) > 0:
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.BIG, wordorder=Endian.BIG)
                            point_value = decoder.decode_32bit_float()
                            data_have=1
                        else:
                            data_have=0
                    case 10: # Double 64-bit real value
                        data_have=0
                    case _:
                        data_have=0
            # ----------------------------------------------------
            if  data_have==0:
                message="Not found register"
                quality=1
                value=point_value
            else:
                if point_value != None:
                    point_value=self.scaling_modbus(point.slopeenabled,point.slope,
                                                    point.offsetenabled,point.offset,
                                                    point_value)
                    if point.value_datatype==9:# Float 32-bit real value IEEE-754    
                        value=round(point_value,2)
                    else:
                        value=self.check_float_modbus(point_value)
                    quality=0
                else:
                    quality=0
            
            # ----------------------------------------------------
        except Exception as err:
            print(f"Error convert_from_registers: '{err}'")   
            
        finally:
            # ----------------------------------------------------
            
            return self.point_data(point=PointDataBase(
            config=point.config_information,
            id_point_list_type=point.id_point_list_type,
            name_point_list_type=point.name_point_list_type,
            id_point=point.id_point,
            parent=point.parent,
            id=point.id,
            point_key=point.pointkey,
            name=point.point_name,
            unit=point.name_units,
            value=value,
            quality=quality,
            message=message,
            active=point.active,
            id_control_group=point.id_control_group,
            control_type_input=point.control_type_input,
            control_menu_order=point.control_menu_order,
            control_min=point.control_min,
            control_max=point.control_max,
            control_enabled=1,
            panel_height=point.panel_height,
            panel_width=point.panel_width,
            output_values=point.output_values,
            slope=point.slope
            ))
    
    def convert_from_internal(self,point:DevicePointBase,register_data_device:RegisterValueDevice):
        try:
            value=None
            quality=0
            message=""
        except Exception as err:
            print(f"Error convert_from_internal: '{err}'")   
            
        finally:
            return self.point_data(point=PointDataBase(
            config=point.config_information,
            id_point_list_type=point.id_point_list_type,
            name_point_list_type=point.name_point_list_type,
            id_point=point.id_point,
            parent=point.parent,
            id=point.id,
            point_key=point.pointkey,
            name=point.point_name,
            unit=point.name_units,
            value=value,
            quality=quality,
            message=message,
            active=point.active,
            id_control_group=point.id_control_group,
            control_type_input=point.control_type_input,
            control_menu_order=point.control_menu_order,
            control_min=point.control_min,
            control_max=point.control_max,
            control_enabled=1,
            panel_height=point.panel_height,
            panel_width=point.panel_width,
            output_values=point.output_values,
            slope=point.slope
            ))
    
    def convert_from_equation(self,point:DevicePointBase,register_data_device:RegisterValueDevice):
        try:
            value=point.constants
            quality=0
            message=""
        except Exception as err:
            print(f"Error convert_from_equation: '{err}'")   
            
        finally:
            return self.point_data(point=PointDataBase(
            config=point.config_information,
            id_point_list_type=point.id_point_list_type,
            name_point_list_type=point.name_point_list_type,
            id_point=point.id_point,
            parent=point.parent,
            id=point.id,
            point_key=point.pointkey,
            name=point.point_name,
            unit=point.name_units,
            value=value,
            quality=quality,
            message=message,
            active=point.active,
            id_control_group=point.id_control_group,
            control_type_input=point.control_type_input,
            control_menu_order=point.control_menu_order,
            control_min=point.control_min,
            control_max=point.control_max,
            control_enabled=1,
            panel_height=point.panel_height,
            panel_width=point.panel_width,
            output_values=point.output_values,
            slope=point.slope
            ))
            
    def point_get_register_block(self,device_points:DevicePointsOutput,register_data_device:RegisterValueDevice):
        points=[]
        try:
            
            for device_point in device_points.points:
                match device_point.pointtype:
                    case "Modbus register":
                        result=self.convert_from_registers(device_point,register_data_device)
                        if result:
                            points.append(result)
                    case "Internal":
                        result=self.convert_from_internal(device_point,register_data_device)
                        if result:
                            points.append(result)
                    case "Equation":
                        result=self.convert_from_equation(device_point,register_data_device)
                        if result:
                            points.append(result) 
        except Exception as err:
            print(f"Error point_get_register_block: '{err}'")   
        finally:
            return PointDataOut(points)
