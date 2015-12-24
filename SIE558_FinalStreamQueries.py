__author__ = 'joelwhitney'
# SIE 558 - Final Take - Query for events and send emails
# this file:
# 1) def function for sending messages
# 2) def main function (re-run every ~1 sec)
    # 3) open connection to mysql db
    # 4) grab most recent tuple for each door
    # 5) check doors for open/close scenarios

# goal check if any door is open longer than threshold
    # outsideDoor > 45 seconds
    # kitchenDoor > 45 seconds
    # freezerDoor > 45 seconds
    # refrigeratorDoor > 45 seconds

# imports
import time
import datetime
import pymysql
import smtplib

def sendMessage(msg):
    # gmail credentials
    username = 'whitney.joel.b@gmail.com'
    password = 'Raptor5099'
    fromaddr = 'Joel Whitney'
    toaddrs  = '2072499538@txt.att.net'

    # The actual mail send. 'msg' can't have symbols, just plain text
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, str(msg))
    server.quit()

def main():
    # set some variables as lists to match up with for loop for each door(i) (outside, kitchen, freezer, refrigerator)
    # last fid for each door - only compares different fid's
    lastfid = [0, 0, 0, 0]
    # set event statuses to closed (1) - used to check if opened
    eventStatus = ['1', '1', '1', '1']
    # set the tresholds as time in seconds - used as thresholds for alerts
    threshold = [45, 45, 45, 45]
    # set the counters - used to check how many times same event has been opened and resends bsaed on occurenceAlert factor
    counter = [0, 0, 0, 0]
    # set re-occurrence alert factor (this will check if seconds since insertTime is evenly divisible by below)
    occurrenceAlert = 300
    # messages list with items as list
    door1Message = [('NEW EVENT OutsideDoor open >' + str(threshold[0]) + 'seconds!'), ('EVENT CONT OutsideDoor still open') , ('EVENT CLOSED OutsideDoor closed')]
    door2Message = [('NEW EVENT KitchenDoor open >' + str(threshold[1]) + 'seconds!'), ('EVENT CONT KitchenDoor still open') , ('EVENT CLOSED KitchenDoor closed')]
    door3Message = [('NEW EVENT Freezer open >' + str(threshold[2]) + 'seconds!'), ('EVENT CONT Freezer still open') , ('EVENT CLOSED Freezer closed')]
    door4Message = [('NEW EVENT Refrigerator open >' + str(threshold[3]) + 'seconds!'), ('EVENT CONT Refrigerator still open') , ('EVENT CLOSED Refrigerator closed')]
    message = [door1Message, door2Message, door3Message, door4Message]

    # open file to write tuples to and start while loop to recursively run checks
    with open('eventOutput.txt', 'w') as f:
        while True:
            # 1) open connection to mysql db
            # open a connection to the database
            cnx = pymysql.connect(host='localhost',
                                  port=3306,
                                  user='joelw',
                                  passwd='Raptor5099',
                                  db='SIE558FinalProject')

            # 2) grab most recent tuple for each door
            # sets up cursor object to interact with MYSQL connection
            cursor = cnx.cursor()

            # SQL select statements <- returns max tuple for each doorID
            query1 = "SELECT * FROM SIE558FinalProject.DoorSensors d " \
                     "INNER JOIN (SELECT MAX(insertTime) AS max_insertTime " \
                     "FROM SIE558FinalProject.DoorSensors GROUP BY doorID" \
                     ") e ON d.insertTime = e.max_insertTime WHERE d.doorID = '1'; "
            query2 = "SELECT * FROM SIE558FinalProject.DoorSensors d " \
                     "INNER JOIN (SELECT MAX(insertTime) AS max_insertTime " \
                     "FROM SIE558FinalProject.DoorSensors GROUP BY doorID" \
                     ") e ON d.insertTime = e.max_insertTime WHERE d.doorID = '2'; "
            query3 = "SELECT * FROM SIE558FinalProject.DoorSensors d " \
                     "INNER JOIN (SELECT MAX(insertTime) AS max_insertTime " \
                     "FROM SIE558FinalProject.DoorSensors GROUP BY doorID" \
                     ") e ON d.insertTime = e.max_insertTime WHERE d.doorID = '3'; "
            query4 = "SELECT * FROM SIE558FinalProject.DoorSensors d " \
                     "INNER JOIN (SELECT MAX(insertTime) AS max_insertTime " \
                     "FROM SIE558FinalProject.DoorSensors GROUP BY doorID" \
                     ") e ON d.insertTime = e.max_insertTime WHERE d.doorID = '4'; "
            queryList = [query1, query2, query3, query4]

            # use for loop to execute function on cursor and retrieve data from db for each query
            for i in range(len(queryList)):
                cursor.execute(queryList[i])
                #print("Query is:", queryList[i])

                # DO THIS WITHOUT FOR LOOP CUZ ONLY 1 TUPLE WILL BE RETURNED
                for line in cursor:
                    #print(line)
                    fid = str(line[0])
                    doorID = str(line[1])
                    doorState = str(line[2])
                    insertTime = line[3]


                    if fid != lastfid[i]:
                        # 3a) check door1 for open scenarios
                        # if doorState1 is open
                        if doorState == '0':
                            # if eventStatus1 is closed
                            if eventStatus[i] == '1':
                                # if door1 is open longer than threshold1 (deltaTime1 of now() - insertTime > threshold1)
                                a = datetime.datetime.strptime(insertTime, "%Y-%m-%d %H:%M:%S.%f")
                                b = datetime.datetime.now()
                                deltaTime = (b - a).total_seconds()
                                #print(deltaTime)
                                if deltaTime > threshold[i]:
                                    # send appropiate response "Event is open" and write to a different table within db (EventsTable)
                                    sendMessage(str(message[i][0]))
                                    print(str(message[i][0]) + " (" + str(datetime.datetime.now()) + ")")
                                    # write tuple to file
                                    tuple = str(cursor) + ',' + str(message[i][0])
                                    f.write(tuple)
                                    # flush to make sure all writes are committed
                                    f.flush()
                                    # change eventStatus1 to open
                                    eventStatus[i] = '0'
                                    # counter1 += 1 <- this signifies occurrence of same event
                                    counter[i] += 1
                                    # update last fid
                                    lastfid[i] = fid
                            # else if eventStatus1 is open
                            elif eventStatus[i] == '0':
                                # if counter1 / 60 seconds % 5 min = 0 <- if counter of occurrences is divisible by 5 send reminder
                                if counter[i] % occurrenceAlert == 0:
                                    # do appropiate response and write to a different table within db (EventsTable)
                                    sendMessage(str(message[i][1]))
                                    print(message[i][1] + " (" + str(datetime.datetime.now()) + ")")
                                    # write tuple to file
                                    tuple = str(cursor) + ',' + str(message[i][1])
                                    f.write(tuple)
                                    # flush to make sure all writes are committed
                                    f.flush()
                                    # counter1 += 1 <- this signifies occurrence of same event
                                    counter[i] += 1
                                    # update last fid
                                    lastfid[i] = fid
                                # else still add 1 to counter
                                else:
                                    counter[i] += 1
                                    # update last fid
                                    lastfid[i] = fid
                        # 3b) check door1 for closed scenarios
                        else:
                            # if doorState1 is closed and eventStatus1 is opened
                            if doorState == '1' and eventStatus[i] == '0':
                                # send appropiate response "Event is closed" and write to a different table within db (EventsTable)
                                sendMessage(str(message[i][2]))
                                print(message[i][2] + " (" + str(datetime.datetime.now()) + ")")
                                # write tuple to file
                                tuple = str(cursor) + ',' + str(message[i][2])
                                f.write(tuple)
                                # flush to make sure all writes are committed
                                f.flush()
                                # change eventStatus1 to closed
                                eventStatus[i] = '1'
                                # change eventStatus1 to closed
                                counter[i] = 0
                                # update last fid
                                lastfid[i] = fid
                            # else do nothing and move on
            # sleep 1 second before going through again
            time.sleep(1)

    # close connections when done
    f.close()
    cursor.close()
    cnx.close()

main()
