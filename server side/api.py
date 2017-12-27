from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
from flask import session
from functools import wraps
from flask import jsonify
import gc
from passlib.hash import sha256_crypt
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
            message = {
                'status': 511,
                'message': 'Login required'
            }
            resp = jsonify(message)
            resp.status_code = 511
            return resp
    return wrap
class LogOut(Resource):
    @LoginRequired
    def get(self):
        session.clear()
        gc.collect()
        return {'status':400, 'message':'Logged Out'}
        
class AuthenticateUser(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email address for Authentication')
            parser.add_argument('password', type=str, help='Password for Authentication')
            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('USE dbUsers')
            ss = "SELECT * FROM users WHERE Email = '%s'"%(_userEmail,)
            rowCnt = cursor.execute(ss)
            log.debug(rowCnt)
            if(rowCnt>0):
                data = cursor.fetchall()
                if(_userPassword == str(data[0][3])):
                    session['logged_in'] = True
                    session['username'] = str(data[0][1])
                    message = {
                        'status': 200,
                        'message': 'OK'
                    }
                    resp = jsonify(message)
                    resp.status_code = 200
                    return resp
            message = {
                    'status': 422,
                    'message': 'Wrong username or password'
                }
            resp = jsonify(message)
            resp.status_code = 422
            return resp
        except Exception as e:
            message = {
                'status': 422,
                'message': str(e)
            }
            resp = jsonify(message)
            resp.status_code = 422
            return resp


##class GetAllItems(Resource):
##    def post(self):
##        try: 
##            # Parse the arguments
##            parser = reqparse.RequestParser()
##            parser.add_argument('id', type=str)
##            args = parser.parse_args()
##
##            _userId = args['id']
##
##            conn = mysql.connect()
##            cursor = conn.cursor()
##            cursor.callproc('sp_GetAllItems',(_userId,))
##            data = cursor.fetchall()
##
##            items_list=[];
##            for item in data:
##                i = {
##                    'Id':item[0],
##                    'Item':item[1]
##                }
##                items_list.append(i)
##
##            return {'StatusCode':'200','Items':items_list}
##
##        except Exception as e:
##            return {'error': str(e)}
##
class AddItem(Resource):
    def post(self):
        try:
            #if( not Authorized()):
             #   return {'StatusCode':422, 'message':'Authorization failure'}
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('stationID', type=int, required=True)
            parser.add_argument('temperature', type=str, required = True)
            parser.add_argument('humidity', type=str, required = True)
            parser.add_argument('lux', type=int, required = True)
            parser.add_argument('soil', type=str, required = True)
            parser.add_argument('co2', type=int, required = True)
            parser.add_argument('battery', type=int, required = True)
            args = parser.parse_args()
            
            _stationID = int(args['stationID'])
            _temperature = float(args['temperature'])
            _humidity = float(args['humidity'])
            _lux = int(args['lux'])
            _soil = int(args['soil'])
            _co2 = int(args['co2'])
            _battery = int(args['battery'])
            log.debug('%s, %s, %s, %s, %s, %s, %s'%(_stationID,_temperature,_humidity,_lux,_soil,_co2,_battery))
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('USE environment')
            #cursor.execute("INSERT INTO stations (StationID, Name) values (%s,'%s')"%(_stationID,"No name"))
            cursor.execute('INSERT INTO measurements (StationID,temperature,humidity,lux,soil,co2,battery) VALUES (%s, %s, %s, %s, %s, %s, %s)'%(_stationID,_temperature,_humidity,_lux,_soil,_co2,_battery))
            conn.commit()
            return {'StatusCode':'200','Message': 'Success'}

        except Exception as e:
            log.debug('exception!!')
            log.debug(e)
            return {'error': str(e)}
        
class CreateUser(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('userName', type = str, help='username')
            parser.add_argument('email', type=str, help='Email address to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            parser.add_argument('phone', type = str, help = 'User phone number')
            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = (args['password'])
            _userName = args['userName']
            _userPhone = args['phone']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('USE dbUsers')
            cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE Email = '%s')"%(_userEmail,))
            data = cursor.fetchall()
            if(data[0][0] == 1):
                return {'StatusCode':422, 'Message': 'Email already taken'}
            else:
                cursor.execute("INSERT INTO users (UserName,Email,Password,Phone) values ('%s', '%s', '%s' ,'%s')"%(_userName,_userEmail,_userPassword,_userPhone))
                cursor.execute("CREATE DATABASE %s"%(_userName,))
                cursor.execute("USE %s"%(_userName,))
                cursor.execute("CREATE TABLE stations (StationID INT NOT NULL, Name varchar(45), PRIMARY KEY(StationID))")
                cursor.execute("CREATE TABLE measurements (StationID INT NOT NULL, temperature DECIMAL(3,1), humidity DECIMAL(4,1), lux SMALLINT UNSIGNED, soil DECIMAL(4,1), co2 SMALLINT UNSIGNED, battery DECIMAL(3,0), measurementDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, FOREIGN KEY (StationID) REFERENCES stations(StationID))")
                conn.commit()
                return {'StatusCode': 200, 'Message': 'Done'}
        except Exception as e:
            return {'error': str(e)}
class CheckEmail(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type = str, help = 'Email address to check')
            args = parser.parse_args()
            userEmail = args['email']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('USE dbUsers')
            cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE Email = '%s')"%(userEmail,))
            data = cursor.fetchall()
            if(data[0][0] == 1):
                return {'StatusCode':422, 'Message': 'Email already taken'}
            else:
                return {'StatusCode': 200, 'Message': 'Email available'}
        except Exception as e:
            log.debug(e)
        return {'StatusCode': 404, 'Message': str(e)}
class GetDaily(Resource):
    @LoginRequired
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('date', type=str, help='Date that we are insterested in')
            parser.add_argument('stationID', type=int, help ='From what station to extract data')
            args = parser.parse_args()
            date = args['date']
            station = args['stationID']
            conn = mysql.connect()
            cursor = conn.cursor()
            dateb = date+' 00:00:00'
            datee = date+' 23:59:59'
            cursor.execute('USE %s'%(session['username'],))
            cursor.execute("SELECT * from measurements WHERE measurementDate BETWEEN '%s' AND '%s' AND StationID = '%s'"%(dateb,datee,station))
            rows = cursor.fetchall()
            a = []
            for row in rows:
                message={}
                message['StationID']=str(row[0])
                message['temperature']=str(row[1])
                message['humidity'] = str(row[2])
                message['lux'] = str(row[3])
                message['soil'] = str(row[4])
                message['so2'] = str(row[5])
                message['battery'] = str(row[6])
                message['measurementDate'] = str(row[7])
                a.append(message)
            resp = jsonify({'measurements':a})
            resp.status_code = 200
            return resp
        except Exception as e:
            return {'error':str(e)}
api.add_resource(CreateUser, '/CreateUser')
api.add_resource(AuthenticateUser, '/AuthenticateUser')
api.add_resource(LogOut,'/LogOut')
api.add_resource(AddItem, '/AddItem')
api.add_resource(CheckEmail,'/CheckEmail')
api.add_resource(GetDaily, '/GetDaily')

if __name__ == '__main__':
    app.run(debug=True)
