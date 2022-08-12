from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

server_ip_address = '0.0.0.0'
server_port = 10502

store = ModbusSlaveContext(
   di=ModbusSequentialDataBlock.create(),
   co=ModbusSequentialDataBlock.create(),
   hr=ModbusSequentialDataBlock.create(),
   ir=ModbusSequentialDataBlock.create())

context = ModbusServerContext(slaves=store, single=True)

print("[+]Info : Server started on Ip : {IP} and PORT : {P} " . format(IP=server_ip_address, P=server_port))
StartTcpServer(context, address=(server_ip_address, server_port))

