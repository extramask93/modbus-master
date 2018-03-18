from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import *
from ConfigReader import ConfigReader
from Client import Client, DummyClient
import time
import sys
import getopt
import argparse

#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------# 
# specify slave to query
#---------------------------------------------------------------------------# 
def ReadRegisters(client,unit_,address,nrOfReg, enables):
    try:
        rr = client.read_input_registers(address, nrOfReg, unit = unit_)
        if(isinstance(rr,ModbusException)):
            print(str(rr))
            return
    except:
        return
    if(rr is None):
        print("Read timed out for slave nr {0}".format(unit_))
        return
    if(rr.function_code >= 0x80):   # test that we are not an error
        print('Invalid response from:'+str(address)+'. Error code: '+hex(rr.function_code))
        return
    print(rr.registers)
    try:
        data = {'stationID': unit_, 'temperature': (rr.registers[0]/10), 'humidity': (rr.registers[1]/10), 'lux':rr.registers[2], 'soil':rr.registers[3],
                'battery': rr.registers[4], 'co2': rr.registers[5]}
    except Exception as e:
        print("Response was broken")
        return
    try:
        log.debug(data)
        clienthtp.SendReadings(data)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    login = ''
    password = ''
    configReader = ConfigReader("config.ini")
    parser = argparse.ArgumentParser(description="Runs as a master Modbus device for sensor slaves")
    parser.add_argument("-l", "--login", help="Email address used during the registration.", required = True)
    parser.add_argument("-p","--password", help = "Password used during the registration", required = True)
    args = parser.parse_args()
    if args.login:
        login = args.login
    else:
        sys.exit(1)
    if args.password:
        password = args.password
    else:
        sys.exit(1)
    server = configReader.GetSectionMap('SERVER')
    clienthtp = Client(server['ip'], server['port'])
    try:
        clienthtp.LogIn(login, password)
    except Exception as e:
        print(str(e))
        sys.exit(1)
    # ---------------------------------------------------------------------------#
    # Init modbus
    # ---------------------------------------------------------------------------#
    serial = configReader.GetSectionMap("SERIAL");
    client = ModbusClient(method='rtu', port=serial["port"], timeout=int(serial["timeout"]),
                          baudrate=int(serial["baud"]), bytesize=int(serial["databits"]),
                          stopbits=int(serial["stopbits"]), parity=serial["parity"],
                          rtscts=int(serial["rtscts"]))
    print("Connecting to {0}...".format(serial['port']))
    if (client.connect()):
        print("connected")
    else:
        print("Unable to establish connection via {0}".format(serial["port"]))
        sys.exit(1)
    # ---------------------------------------------------------------------------#
    # Init slaves according information from the server
    # ---------------------------------------------------------------------------#
    try:
        slaves = clienthtp.GetStations()
    except Exception as e:
        print(str(e))
        sys.exit(1)
    for slave in slaves:
        slave.SetCallback(ReadRegisters, client)
    # ---------------------------------------------------------------------------#
    # Run tick forever
    # ---------------------------------------------------------------------------#
    try:
        while True:
            timeBegin = time.time()
            for slave in slaves:
                slave.Tick()
            timeElapsed = time.time() - timeBegin
            if (timeElapsed <= 1):
                time.sleep(1 - timeElapsed)
    except KeyboardInterrupt:
        print("Closing modbus connection...")
        client.close()