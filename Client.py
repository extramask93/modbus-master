import json
import requests
from requests.exceptions import RequestException
from Slave import Slave
class DummyClient():
    def __init__(self, ip, port):
        pass
    def LogIn(self,email,password):
        return True
    def LogOut(self):
        pass
    def SendReadings(self, readings):
        return True
    def RegisterUser(self):
        pass
class Client(DummyClient):
    def __init__(self,ip,port):
        super().__init__(ip,port)
        self.ip = ip
        self.port = port
        self.isLoggedIn = False
        self.address = "http://{0}:{1}".format(ip,port)
    def LogIn(self, email, password):
        if(self.isLoggedIn):
            return True
        print("Trying to log in as {0}...".format(email))
        url = "http://{0}:{1}/LogIn".format(self.ip, self.port)
        try:
            r = requests.post(url, data={'email': email, 'password': password}, timeout = 1)
        except RequestException as e:
            raise Exception(str(e))
        if (r.status_code is not 200):
            try:
                response = r.json()
            except:
                raise Exception(r.text)
            else:
                raise Exception(response['message'])
        self.jar = r.cookies
        response = json.loads(r.text)
        print('Logged in')
        self.isLoggedIn = True
    def LogOut(self):
        if(not self.isLoggedIn):
            return
        print('Loggin Out...')
        try:
            r= requests.get(self.address+"/LogOut", timeout = 1)
        except RequestException as e:
            raise Exception(str(e))
        if(r.status_code is not 200):
            raise Exception("Error occured during logout")
        else:
            return True
    def SendReadings(self, readings):
        if(not self.isLoggedIn):
            raise Exception("You are not logged in")
        try:
            r = requests.post(self.address+"/AddItem", data = readings, cookies = self.jar, timeout = 1)
        except RequestException as e:
            raise Exception(str(e))
        if (r.status_code is not 200):
            try:
                response = r.json()
            except:
                raise Exception(r.text)
            else:
                raise Exception(response['message'])
        return True
    def GetStations(self):
        if(not self.isLoggedIn):
            raise Exception("You are not logged in")
        try:
            slaves = []
            r = requests.get(self.address+"/GetStations", cookies = self.jar, timeout = 1)
            stations = json.loads(r.text)
            stations = stations["stations"]
            for station in stations:
                slaves.append(Slave(int(station["StationID"]),station["Name"], int(station["refTime"]), station["enableSettings"]))
        except RequestException as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception("Error occurred during slaves loading")
        else:
            return slaves

