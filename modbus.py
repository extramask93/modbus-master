'''
Pymodbus Synchronous Client Examples
--------------------------------------------------------------------------
The following is an example of how to use the synchronous modbus client
implementation from pymodbus.
It should be noted that the client can also be used with
the guard construct that is available in python 2.5 and up::
    with ModbusClient('127.0.0.1') as client:
        result = client.read_coils(1,10)
        print result
'''
#---------------------------------------------------------------------------# 
# import the various server implementations
#---------------------------------------------------------------------------# 
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from ConfigReader import ConfigReader
import MySQLdb
import time
import sys
#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
#---------------------------------------------------------------------------#
# read config
#---------------------------------------------------------------------------#
configReader = ConfigReader("config.ini")
#---------------------------------------------------------------------------# 
# choose the client you want
#---------------------------------------------------------------------------# 

serial = configReader.GetSectionMap("SERIAL");
client = ModbusClient(method='rtu', port=serial["port"], timeout=int(serial["timeout"]),
                      baudrate = int(serial["baud"]), bytesize = int(serial["databits"]),
                      stopbits = int(serial["stopbits"]), parity = serial["parity"],
                      rtscts = int(serial["rtscts"]))
print("connecting to %s..."%serial['port'])
if(client.connect()):
    print("connected")
else:
    sys.exit(1)
#---------------------------------------------------------------------------# 
# specify slave to query
#---------------------------------------------------------------------------# 
def ReadRegisters(client,unit_,address,nrOfReg):
    log.debug("Read input registers")
    rr = client.read_input_registers(address, nrOfReg, unit=unit_)
    assert(rr.function_code < 0x80)     # test that we are not an error
    print(rr.registers) 
#---------------------------------------------------------------------------#
# Initialize slaves according to slaves.txt
#---------------------------------------------------------------------------#
from SlaveLoader import SlaveLoader
sloader = SlaveLoader()
slaves = sloader.LoadFromFile("slaves.txt")
for slave in slaves:
    slave.SetCallback(ReadRegisters,client)
#---------------------------------------------------------------------------#
# Run tick forever
#---------------------------------------------------------------------------#
import time
while True:
    timeBegin = time.time()
    for slave in slaves:
        slave.Tick()
    timeElapsed = time.time() - timeBegin
    if(timeElapsed<=1):
        time.sleep(1-timeElapsed)
#---------------------------------------------------------------------------# 
# close the client
#---------------------------------------------------------------------------# 
client.close()
