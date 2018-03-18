class Slave:
    def __init__(self,address, name, read_delay_sec, enables):
        self.name_ = name #string representation of a given station
        self.address_ = address #address of a device in modbus network
        self.time_ = read_delay_sec #imposed delay between subsequent reads
        self.timeLeft_ = self.time_
        self.enables = [int(enables[0]),int(enables[1]),int(enables[2]),int(enables[3]),int(enables[4]),int(enables[5])]
        self.client_ = None
        self.callback = None
    def SetTime(self,time):
        self.time_=time
    def SetCallback(self,callback,client):
        self.callback_ = callback
        self.client_ = client
    def GetEnables(self):
        return self.enables
    def Tick(self):
        self.timeLeft_=self.timeLeft_-1
        if self.timeLeft_ <= 0:
            self.timeLeft_=self.time_
            self.callback_(self.client_,self.address_,1000,6, self.enables)
            
        
