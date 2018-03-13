import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

class DBException(Exception):
    def __init__(self, msg):
        super.__init__()
        self.msg = msg
##===============================================

class DatabaseUtility:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='root',
                                           password='',
                                           host='localhost')
        self.cursor = self.cnx.cursor()
    def ChangeDatabase(self, databaseName):
        try:
            self.cnx.database = databaseName
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                raise DBException("Unable to find database associated with databaseName")
            else:
                print(err.msg)

    def CreateDatabase(self):
        try:
            self.RunCommand("CREATE DATABASE %s DEFAULT CHARACTER SET 'utf8';" % self.db)
        except mysql.connector.Error as err:
            raise DBException("Failed creating database: {}".format(err))


    def RunCommand(self, cmd):
        print("RUNNING COMMAND: " + cmd)
        try:
            self.cursor.execute(cmd)
        except mysql.connector.Error as err:
            print('ERROR MESSAGE: ' + str(err.msg))
            print('WITH ' + cmd)
            raise DBException("Error occurred during query execution.")
        try:
            msg = self.cursor.fetchall()
        except:
            msg = self.cursor.fetchone()
        return msg

    def __del__(self):
        self.cnx.commit()
        self.cursor.close()

