##database = configReader.GetSectionMap("DATABASE")
##try:
##    db = MySQLdb.connect(host = database["ip"],user = database["user"],passwd = database["password"],db="SENSORDB")
##    print("connected do database")
##except MySQLdb.Error, e:
##    print("Can't connect to the database server")
##    print("Error code: %d"%e.args[0])
##    print("Error message: %s"%e.args[1])
##    sys.exit(1)
##sensorList = []
##try:
##    cursor = db.cursor
##    sql = "LIST TABLES"
##    cursor.execute(sql)
##    tables = cursor.fetchall()
##    for table in table:
##        cursor.execute("SELECT id FROM %s",(table,))
##        address = cursor.fetchone()
##        if(address == None):
##            break
##        cursor.execute("SELECT time FROM %s",(time,))
##        time = cursor.fetchone()
##        if(time == None):
##            break
##        sensorList.append(Slave(address,time,TimeOutHandler))
##except MySQLdb.Error, e:
##    print("Unable to fetch data")
##    print e
##cursor.close()
##db.close()
