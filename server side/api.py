from flask import Flask
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from flask import session
from flask import request
from functools import wraps
from flask import jsonify
import mysql.connector
import gc

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'environment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


mysql.init_app(app)
app.secret_key = "bazant"
api = Api(app)
def LoginRequired(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if('logged_in' in session):
            return f(*args, **kwargs)
        else:
            return {'message': 'Please log in'},511
    return wrap
class LogOut(Resource):
    @LoginRequired
    def get(self):
        session.clear()
        gc.collect()
        return {'status':200, 'message':'Logged Out'},200
        
class AuthenticateUser(Resource):
    def post(self):
        try:
            _userEmail = request.form['email']
            _userPassword = request.form['password']
        except KeyError as e:
            return {'message': 'There are missing arguments in the request.'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'Can\'t connect to the database'}, 503
        try:
            cursor.execute('USE dbUsers')
            rowCnt = cursor.execute("SELECT * FROM users WHERE Email = (%s)", (_userEmail,))
        except:
            return {'message': 'Query Error'}, 502
        if(rowCnt>0):
            data = cursor.fetchall()
            if(_userPassword == str(data[0][3])):
                session['logged_in'] = True
                session['username'] = str(data[0][1])
                return {'message':'OK'},200
            else:
                return {'message': 'Wrong username or password'},422
        return {'message':'No username found'},422

class AddItem(Resource):
    @LoginRequired
    def post(self):
        try:
            _stationID = str(request.form['stationID'])
            _temperature = str(request.form['temperature'])
            _humidity = str(request.form['humidity'])
            _lux = str(request.form['lux'])
            _soil = str(request.form['soil'])
            _co2 = str(request.form['co2'])
            _battery = str(request.form['battery'])
        except KeyError as e:
            return {'message':'keyError'},400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message':'No MySQL connection'},503
        try:
            cursor.execute("USE %s"%(session['username'],))
            cursor.execute("INSERT INTO measurements (StationID,temperature,humidity,lux,soil,co2,battery) VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s))",(_stationID,_temperature,_humidity,_lux,_soil,_co2,_battery))
            conn.commit()
        except:
            return {'message': 'Error during execution of MySQL commands'},502
        return {'StatusCode':'200','Message': 'Success'}
        
class CreateUser(Resource):
    def post(self):
        try:
            _userEmail = request.form['email']
            _userPassword = request.form['password']
            _userName = request.form['userName']
            _userPhone = request.form['phone']
        except KeyError as e:
            return {'message': 'keyError'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'No MySQL connection'}, 503
        try:
            cursor.execute('USE dbUsers')
            cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE Email = (%s))",(_userEmail))
            data = cursor.fetchall()
            if(data[0][0] == 1):
                return {'StatusCode':422, 'Message': 'Email already taken'}
            else:
                cursor.execute("INSERT INTO users (UserName,Email,Password,Phone) values ((%s), (%s), (%s) ,(%s))", (_userName,_userEmail,_userPassword,_userPhone))
                cursor.execute("CREATE DATABASE %s"%(_userName,))
                cursor.execute("USE %s"%(_userName,))
                cursor.execute("CREATE TABLE stations (StationID INT NOT NULL, Name varchar(45), PRIMARY KEY(StationID))")
                cursor.execute("CREATE TABLE measurements (StationID INT NOT NULL, temperature DECIMAL(3,1), humidity DECIMAL(4,1), lux SMALLINT UNSIGNED, soil DECIMAL(4,1), co2 SMALLINT UNSIGNED, battery DECIMAL(3,0), measurementDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, FOREIGN KEY (StationID) REFERENCES stations(StationID))")
                conn.commit()
                return {'StatusCode': 200, 'Message': 'Done'}
        except Exception as e:
            return{'message': 'Error during execution of MySQL commands'}, 502
class CheckEmail(Resource):
    def post(self):
        try:
            userEmail = request.form['email']
        except KeyError as e:
            return {'message': 'keyError'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'No MySQL connection'}, 503
        try:
            cursor.execute('USE dbUsers')
            cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE Email = (%s))", (userEmail))
            data = cursor.fetchall()
        except:
            return {'message': 'Error during execution of MySQL commands'}, 502
        if(data[0][0] == 1):
            return {'StatusCode':422, 'Message': 'Email already taken'}
        else:
            return {'StatusCode': 200, 'Message': 'Email available'}
class GetDaily(Resource):
    @LoginRequired
    def get(self):
        try:
            dateStart = request.args.get('date1', default=None, type = str)
            dateEnd = request.args.get('date2', default=None, type=str)
            station = request.args.get('station',default='1', type=str)
            #measurement = request.args.get('m', default = 'temperature', type=str)
            session['username'] = 'environment'
            if(dateStart is None):
                return {'message':'Start date not specified'},404
            try:
                conn = mysql.connect()
                cursor = conn.cursor()
            except:
                return {'message': 'No MySQL connection'}, 503
            try:
                cursor.execute('USE %s' % (session['username'],))
                if(dateEnd is None):
                    cursor.execute("SELECT * from measurements WHERE measurementDate >= (%s) AND StationID = (%s)" , (dateStart,station))
                else:
                    cursor.execute("SELECT * from measurements WHERE measurementDate BETWEEN (%s) AND (%s) AND StationID = (%s)", (dateStart, dateEnd, station))
                rows = cursor.fetchall()
            except:
                return {'message': 'Error during execution of MySQL commands'}, 502
            a = []
            for row in rows:
                message={}
                message['StationID']=str(row[0])
                message['temperature']=str(row[1])
                message['humidity'] = str(row[2])
                message['lux'] = str(row[3])
                message['soil'] = str(row[4])
                message['co2'] = str(row[5])
                message['battery'] = str(row[6])
                message['measurementDate'] = str(row[7])
                a.append(message)
            resp = jsonify({'measurements': a})
            resp.status_code = 200
            return resp
        except Exception as e:
            return {'error',str(e)},404
class GetPeriodical(Resource):
    @LoginRequired
    def get(self):
        try:
            period = request.args.get('period', default='week', type = str)
            type = request.args.get('type', default='temperature', type=str)
            station = request.args.get('station',default='1', type=str)
            nrOfintervals = request.args.get('interval', default = '100', type=str)
            session['username'] = 'environment'
            intervals = int(nrOfintervals)
            try:
                conn = mysql.connect()
                cursor = conn.cursor()
            except:
                return {'message': 'No MySQL connection'}, 503
            try:
                cursor.execute('USE %s' % (session['username'],))
                dict = {'day':1,'week':7,'3days':3,'month':31,'3months':93,'year':365 }
                az = "select StationID,avg({0}) as {0}, convert(min(measurementDate),datetime) as time from measurements where measurementDate between date_sub(now(), interval {1} day) and now() and StationID={2} group by measurementDate div (select ((unix_timestamp() - unix_timestamp())+ ({1} * 864000)) div {3} as tmp),StationID".format(type,dict[period],station,nrOfintervals)
                ay="select count(StationID) from measurements where measurementDate between date_sub(now(), interval {0} day) and now() and StationID = {1}".format(dict[period],station)
                cursor.execute(ay)
                nr = cursor.fetchone()
                log.debug(nr[0])
                if(int(nr[0]) <= int(nrOfintervals)):
                    cursor.execute("select StationID,{0},measurementDate from measurements where measurementDate between date_sub(now(), interval {1} day) and now() and StationID = {2}".format(type,dict[period],station))
                else:
                    cursor.execute(az)
            except:
                return {'message': 'error'}, 502
            rows = cursor.fetchall()
            a = []
            for row in rows:
                message={}
                message['StationID']=str(row[0])
                message[type]=str(row[1])
                message['time'] = str(row[2])
                a.append(message)
            resp = jsonify({'measurements': a})
            resp.status_code = 200
            return resp
        except Exception as e:
            return {'error',str(e)},404

class GetStations(Resource):
    @LoginRequired
    def get(self):
        try:
            try:
                conn = mysql.connect()
                cursor = conn.cursor()
            except:
                return {'message': 'No MySQL connection'}, 503
            try:
                cursor.execute('USE %s' % (session['username'],))
                cursor.execute("select StationID,Name,DATE_FORMAT(refTime,'%T') as refTime,temperature,humidity,lux,soil,battery,co2 from stations")
                rows = cursor.fetchall()
            except:
                return {'message': 'Error during execution of MySQL commands'}, 502
            a = []
            for row in rows:
                message={}
                message['StationID']=str(row[0])
                message['Name']=str(row[1])
                message['refTime'] = str(row[2])
                message['enableSettings'] = str(row[3])+str(row[4])+str(row[5])+str(row[6])+str(row[7])+str(row[8])
                a.append(message)
            resp = jsonify({'stations': a})
            resp.status_code = 200
            return resp
        except Exception as e:
            return {'error',str(e)},404
class ModStation(Resource):
    @LoginRequired
    def post(self):
        try:
            _stationID = request.form['StationID']
            _stationName = request.form['Name']
            _stationrefTime = request.form['refTime']
            _stationSettings = request.form['settings']
        except KeyError as e:
            return {'message': 'There are missing arguments in the request.'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'No MySQL connection'}, 503
        try:
            cursor.execute('USE %s' % (session['username'],))
            rowCnt = cursor.execute("SELECT * FROM stations WHERE StationID = (%s)", (_stationID,))
        except:
            return {'message': 'Error during execution of MySQL commands'}, 502
        if(rowCnt>0):
            cursor.execute("UPDATE stations SET Name=(%s), refTime=(%s), temperature=(%s), humidity=(%s), lux=(%s), soil=(%s), battery=(%s), co2=(%s) WHERE StationID=(%s)",
                           (_stationName, _stationrefTime,
                            _stationSettings[0], _stationSettings[1],
                            _stationSettings[2], _stationSettings[3], _stationSettings[4]
                            , _stationSettings[5], _stationID))
            return {'message': 'OK'}, 200
        return {'message':'Station does not exist'},422

class AddStation(Resource):
    @LoginRequired
    def post(self):
        try:
            _stationID = request.form['StationID']
            _stationName = request.form['Name']
            _stationrefTime = request.form['refTime']
            _stationSettings = request.form['settings']
        except KeyError as e:
            return {'message': 'There are missing arguments in the request.'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'No MySQL connection'}, 503
        try:
            cursor.execute('USE %s' % (session['username'],))
            rowCnt = cursor.execute("SELECT * FROM stations WHERE StationID = (%s)", (_stationID,))
        except:
            return {'message': 'Error during execution of MySQL commands'}, 502
        if(rowCnt==0):
            cursor.execute("INSERT INTO stations (StationID, Name, refTime, temperature, humidity, lux, soil, battery, co2) values ((%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s))",
                           (_stationID, _stationName,_stationrefTime,_stationSettings[0],_stationSettings[1],
                            _stationSettings[2],_stationSettings[3],_stationSettings[4]
                            ,_stationSettings[5]))
            return {'message': 'OK'}, 200
        return {'message':'Station already exist'},422
class RemoveStation(Resource):
    @LoginRequired
    def post(self):
        try:
            _stationID = request.form['StationID']
        except KeyError as e:
            return {'message': 'keyError'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
        except:
            return {'message': 'No MySQL connection'}, 503
        try:
            cursor.execute('USE %s' % (session['username'],))
            rowCnt = cursor.execute("DELETE FROM stations WHERE StationID = (%s)", (_stationID,))
            return {'message': 'OK'}, 200
        except:
            return {'message': 'Error during execution of MySQL commands'}, 502
api.add_resource(CreateUser, '/CreateUser')
api.add_resource(AuthenticateUser, '/LogIn')
api.add_resource(LogOut,'/LogOut')
api.add_resource(AddItem, '/AddItem')
api.add_resource(CheckEmail,'/CheckEmail')
api.add_resource(GetDaily, '/GetDaily')
api.add_resource(GetStations, '/GetStations')
api.add_resource(GetPeriodical,'/GetPeriodical')
api.add_resource(ModStation, '/ModStation')
api.add_resource(AddStation, '/AddStation')
api.add_resource(RemoveStation, '/RemoveStation')
if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')
