import json
import requests
class DummyClient():
    def __init__(self):
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
        super().__init__(self)
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
            r = requests.post(url, data={'email': email, 'password': password})
            response = json.loads(r.text)
        except:
            return False
        if (r.status_code == 422):
            print(response['message'])
            return False
        else:
            print('Logged in')
            self.isLoggedIn = True
            return True
    def LogOut(self):
        if(not self.isLoggedIn):
            return
        print('Loggin Out...')
        try:
            r= requests.get(self.address+"/LogOut")
            response = json.loads(r.text)
        except:
            return False
        print(response['message'])
    def SendReadings(self, readings):
        if(not self.isLoggedIn):
            return False
        r = requests.post(self.address+"/AddItem", data = readings)
        response = json.loads(r.text)
        if(r.status_code == 200):
            return True
        elif(r.status_code == 422):
            self.isLoggedIn  = False
            return False
        else:
            return False
    def RegisterUser(self):
        while True:
            username = raw_input('Please type username: ')
            if(len(username) < 3):
                print('Username should be at least 3 characters long')
                continue
            break
        while True:
            email = raw_input('Please type email: ')
            if(CheckEmail(email)):
                break
            print('Email already taken')
        while True:
            password1 = raw_input('Please type password: ')
            if(len(password1) < 5):
                print('Password length should be at least 5 characters long')
                continue
            passwrod2 = raw_input('Please repeat the password: ')
            if(password1 != passwrod2):
                print('Passwords do not match.')
                continue
            break


