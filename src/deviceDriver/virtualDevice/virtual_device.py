import logging

from pymodbus.datastore import (ModbusSequentialDataBlock, ModbusServerContext,
                                ModbusSlaveContext)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.sync import (ModbusSerialServer, StartSerialServer,
                                  StartTcpServer)
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.version import version

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
identity = ModbusDeviceIdentification()
identity.VendorName = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName = 'pymodbus Server'
identity.MajorMinorRevision = version.short()

def run_server_tcp():
    addresses=[]
    for item in range(1,100):
        addresses.append(item)
    slaves = {}
    for address in addresses:
        store = ModbusSlaveContext(
 	 di=ModbusSequentialDataBlock(0, [17]*100),
         co=ModbusSequentialDataBlock(0, [17]*100),
         hr=ModbusSequentialDataBlock(0, [0]*65000),
         ir=ModbusSequentialDataBlock(0, [152, 276]),
        zero_mode=True
    )
        slaves.update({address: store})
    context = ModbusServerContext(slaves=slaves, single=False)
    
    StartTcpServer(context, address=("0.0.0.0", 502))
if __name__ == "__main__":
    run_server_tcp()