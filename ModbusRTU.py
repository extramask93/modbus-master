from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from ConfigReader import ConfigReader

class ModbusRTU:
    def __init__(self, config):
        self.serial = config.GetSectionMap("SERIAL");
        self.client = ModbusClient(method='rtu', port=self.serial["port"], timeout=int(self.serial["timeout"]),
                              baudrate=int(self.serial["baud"]), bytesize=int(self.serial["databits"]),
                              stopbits=int(self.serial["stopbits"]), parity=self.serial["parity"],
                              rtscts=int(self.serial["rtscts"]))
    def connect(self):
        print("Connecting to {0}...".format(self.serial['port']))
        if(self.client.connect()):
            print("Connected")
        else:
            raise Exception("Unable to establish connection via {0}".format(self.serial["port"]))
