__author__ = 'joelwhitney'
# SIE 558 - Final Take - Insert into DB
# this file:
# 1) opens connection to mysql db and sets up insert statement
# 2) set up pi serial connection
# 3) opens file to write results to and start reading from serial

# imports
import serial
import time
import datetime
import pymysql

# 1) opens connection to mysql db and sets up insert statement
# open a connection to the database
cnx = pymysql.connect(host='localhost',
                      port=3306,
                      user='joelw',
                      passwd='Raptor5099',
                      db='SIE558FinalProject')
# SQL insert statement
insert_observation_query = ("INSERT INTO SIE558FinalProject.DoorSensors "
                            "(doorID, doorState, insertTime) "
                            "VALUES (%s, %s, %s);")

# Sets up cursor object to interact with MYSQL connection
cursor = cnx.cursor()

# 2) set up pi serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)

# clean out serial connection
ser.flushInput()

time.sleep(2)

print("doorID, doorState, insertTime")

# 3) opens file to write results to and start reading from serial
with open('arduinoOutput.txt', 'w') as f:
    while True:
        # create variable for each serial readline result
        response = ser.readline().decode("ascii")
        # add current datetime for insertTime values
        response = response[:-2] + "," + str(datetime.datetime.now())

        # print response
        print(response)

        # write tuple to file
        tuple=str(response)
        f.write(tuple)
        # flush to make sure all writes are committed
        f.flush()

        # split response string using "," as delimiter
        split = tuple.split(",")

        # assign the observation counter to id and value to value from the split string array
        doorID = split[0]
        doorState = split[1]
        insertTime = split[2]

        # generate the query to insert the value into the SensorData table
        observation_data = (str(doorID), str(doorState), str(insertTime))
        print("Query is: " + insert_observation_query.replace("%s", "{}").format(observation_data[0],
                                                                                 observation_data[1],
                                                                                 observation_data[2]))
        print("\n" + "*" * 80)

        # ping the connection before cursor execution so the connection is re-opened if it went idle in downtime
        cnx.ping()
        # use execute function on cursor and insert data from arduino
        cursor.execute(insert_observation_query, observation_data)
        # make sure data is committed to the database before looping through again
        cnx.commit()

# close file, cursor, and connection when done writing
f.close()
cursor.close()
cnx.close()