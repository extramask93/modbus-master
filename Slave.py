class Slave:
    __init__(self,address, timeOut, timeOutHandler):
        self.timeOutHandler = timeOutHandler
        self.address_ = address
        self.time_ = timeOut
    def SetTime(self,time):
        self.time_=time
    def Tick(self):
        self.timeLeft_=self.timeLeft-1
        if self.timeLeft_ <= 0:
            self.timeOutHandler(id)
            self.timeLeft_=self.time_
    
            
        
