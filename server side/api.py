from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
from flask import session
from functools import wraps
import gc

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'environment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


mysql.init_app(app)
app.secret_key = "bazant"
api = Api(app)
def LoginRequired(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if('logged_in' in session):
            return f(*args, **kwargs)
        else:
            return 'Login required'
    return wrap
class LogOut(Resource):
    @LoginRequired
    def get(self):
        session.clear()
        gc.collect()
        return 'LoggedOut'
        
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
            cursor.callproc('sp_AuthenticateUser',(_userEmail,))
            data = cursor.fetchall()

            
            if(len(data)>0):
                if(str(data[0][2])==_userPassword):
                    session['logged_in'] = True
                    session['username'] = str(data[0][1])
                    return {'status':200,'UserId':str(data[0][0])}
                else:
                    return {'status':100,'message':'Authentication failure'}

        except Exception as e:
            return {'error': str(e)}


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
##class AddItem(Resource):
##    def post(self):
##        try: 
##            # Parse the arguments
##            parser = reqparse.RequestParser()
##            parser.add_argument('id', type=str)
##            parser.add_argument('item', type=str)
##            args = parser.parse_args()
##
##            _userId = args['id']
##            _item = args['item']
##
##            print _userId;
##
##            conn = mysql.connect()
##            cursor = conn.cursor()
##            cursor.callproc('sp_AddItems',(_userId,_item))
##            data = cursor.fetchall()
##
##            conn.commit()
##            return {'StatusCode':'200','Message': 'Success'}
##
##        except Exception as e:
##            return {'error': str(e)}
        
                

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
            _userPassword = args['password']
            _userName = args['userName']
            _userPhone = args['phone']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('spCreateUser',(_userName,_userPassword,_userEmail,_userPhone))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return {'StatusCode':'200','Message': 'User creation success'}
            else:
                return {'StatusCode':'1000','Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}



api.add_resource(CreateUser, '/CreateUser')
api.add_resource(AuthenticateUser, '/AuthenticateUser')
api.add_resource(LogOut,'/LogOut')
#api.add_resource(AddItem, '/AddItem')
#api.add_resource(GetAllItems, '/GetAllItems')

if __name__ == '__main__':
    app.run(debug=True)
