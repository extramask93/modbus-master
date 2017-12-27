class Slave:
    def __init__(self,address, name, read_delay_sec):
        self.name_ = name #string representation of a given station
        self.address_ = address #address of a device in modbus network
        self.time_ = read_delay_sec #imposed delay between subsequent reads
        self.timeLeft_ = self.time_
        self.client_ = None
        self.callback = None
    def SetTime(self,time):
        self.time_=time
    def SetCallback(self,callback,client):
        self.callback_ = callback
        self.client_ = client
    def Tick(self):
        self.timeLeft_=self.timeLeft_-1
        if self.timeLeft_ <= 0:
            self.timeLeft_=self.time_
            self.callback_(self.client_,self.address_,1000,6)
            
        
