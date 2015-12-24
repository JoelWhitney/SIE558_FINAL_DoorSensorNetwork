__author__ = 'joelwhitney'
# SIE 558 - Final Take - Read from DB and write to Plotly
# this file:
# 1) gets credentials for plotly access
# 2) set up graph
# 3) opens connection to mysql db and returns results since last update
# 4) the results are then wrote to the plotly graph and the last update time is updated

# imports
import plotly.plotly as py # plotly library
import json # used to parse config.json
import serial
import time
import datetime
import plotly.tools as tls
from plotly.graph_objs import *
import pymysql

def to_unix_time(dt):
    epoch =  datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

# 1) gets credentials for plotly access
with open('./config.json') as config_file:
    plotly_user_config = json.load(config_file)
    py.sign_in('whitneyjb5', '8kvvcrsnoo')
    # get stream id from stream id list in the json file
    stream_id1 = plotly_user_config['plotly_streaming_tokens'][0]
    stream_id2 = plotly_user_config['plotly_streaming_tokens'][1]
    stream_id3 = plotly_user_config['plotly_streaming_tokens'][2]
    stream_id4 = plotly_user_config['plotly_streaming_tokens'][3]

# make instance of stream id object
stream1 = Stream(
    token=stream_id1,  # (!) link stream id to 'token' key
)
stream2 = Stream(
    token=stream_id2,  # (!) link stream id to 'token' key
)
stream3 = Stream(
    token=stream_id3,  # (!) link stream id to 'token' key
)
stream4 = Stream(
    token=stream_id4,  # (!) link stream id to 'token' key
)

# 2) set up graph
# graph layout
layout = Layout(
    title='Door Statuses Over Time',
    titlefont=dict(
        family='Arial, sans-serif',
        size=24,
        color='lightgrey'),
    paper_bgcolor='rgb(68, 68, 68)',
    plot_bgcolor='rgb(68, 68, 68)',
    showlegend=True,
    xaxis=dict(
        title='Insert Time',
        titlefont=dict(
            family='Arial, sans-serif',
            size=18,
            color='white'),
        autorange=True,
        rangemode='tozero',
        range=[to_unix_time(datetime.datetime.utcnow() - datetime.timedelta(hours=4)), to_unix_time(datetime.datetime.utcnow())],
        showgrid=True,
        zeroline=True,
        zerolinecolor='white',
        gridcolor="rgb(128, 128, 128)",
        showline=True,
        linecolor='white',
        autotick=True,
        ticks='outside',
        showticklabels=True,
        tickfont=dict(
            family='Arial, sans-serif',
            size=12,
            color='white'),
        tickangle=-45,
        type='date'
    ),
    yaxis=dict(
        title='Door Status',
        titlefont=dict(
            family='Arial, sans-serif',
            size=18,
            color='white'),
        autorange='reversed',
        tickmode='array',
        ticktext=['Closed', 'Opened'],
        tickvals=[1,0],
        showgrid=True,
        gridcolor="rgb(128, 128, 128)",
        range=[1.25,-0.25],
        showline=True,
        linecolor='white',
        zeroline=False,
        autotick=True,
        ticks='outside',
        showticklabels=True,
        tickfont=dict(
            family='Arial, sans-serif',
            size=12,
            color='white')
    ),
    legend=dict(
        bordercolor='white',
        traceorder='normal',
        bgcolor='rgb(68, 68, 68)',
        borderwidth=0.4,
        font=dict(
            color='white',
            family='Arial, sans-serif',
            size=12,
        )
    )
)
# Initialize trace of streaming plot by embedding the unique stream_id
outsideDoor = Scatter( # trace 0
    x=[],
    y=[],
    name='Outside Door',
    mode='lines+markers',
    showlegend=True,
    line=dict(
        color="rgb(255, 102, 102)",
    ),
    stream=stream1)         # (!) embed stream id, 1 per trace
kitchenDoor = Scatter( # trace 1
    x=[],
    y=[],
    name='Kitchen Door',
    mode='lines+markers',
    showlegend=True,
    line=dict(
        color="rgb(255, 255, 102)",
    ),
    stream=stream2)         # (!) embed stream id, 1 per trace
freezer = Scatter( # trace 2
    x=[],
    y=[],
    name='Freezer',
    mode='lines+markers',
    showlegend=True,
    line=dict(
        color="rgb(102, 255, 102)",
    ),
    stream=stream3)         # (!) embed stream id, 1 per trace
refrigerator = Scatter( # trace 3
    x=[],
    y=[],
    name='Refrigerator',
    mode='lines+markers',
    showlegend=True,
    line=dict(
        color="rgb(102, 255, 255)",
    ),
    stream=stream4)         # (!) embed stream id, 1 per trace
data = Data([outsideDoor, kitchenDoor, freezer, refrigerator])
# Make a figure object
fig = Figure(data=data, layout=layout)
# (@) Send fig to Plotly, initialize streaming plot, open new tab
unique_url = py.plot(fig, filename='s7_first-stream')
time.sleep(2)

# 3) opens connection to mysql db and returns results since last update
# initialize last door states
lastDoorState1 = '1'
lastDoorState2 = '1'
lastDoorState3 = '1'
lastDoorState4 = '1'
lastUpdate = '2015-11-15 01:01:01.111111'

# loop to retrieve tuples greater than lastupdate
while True:
    # open a connection to the database
    cnx = pymysql.connect(host='localhost',
                          port=3306,
                          user='joelw',
                          passwd='Raptor5099',
                          db='SIE558FinalProject')

    # sets up cursor object to interact with MYSQL connection
    cursor = cnx.cursor()

    # SQL insert statement
    query = ("SELECT * FROM SIE558FinalProject.DoorSensors WHERE insertTime > '%s' ORDER BY insertTime ASC; ")

    # use execute function on cursor and retrieve data from db
    cursor.execute(query.replace("%s", "{}").format(lastUpdate))

    # get length of tuples
    count = cursor.execute(query.replace("%s", "{}").format(lastUpdate))
    # print tuples returned
    if count > 0:
        print("Query is: " + query.replace("%s", "{}").format(lastUpdate))
        print("Query returned " + str(count) + " results" + '\n')
    else:
        print("Query is: " + query.replace("%s", "{}").format(lastUpdate))
        print(str(count) + " rows affected" + '\n')

    # 4) the results are then wrote to the plotly graph and the last update time is updated
    # iterate through each tuple
    for line in cursor:
        fid = str(line[0])
        doorID = str(line[1])
        doorState = str(line[2])
        insertTime = line[3]

        # make instance of the Stream link object, with same stream id as Stream id object
        s1 = py.Stream(stream_id1)
        s2 = py.Stream(stream_id2)
        s3 = py.Stream(stream_id3)
        s4 = py.Stream(stream_id4)
        # open the stream
        s1.open()
        s2.open()
        s3.open()
        s4.open()

        # set x and y columns and write for each trace
        x, y = insertTime, doorState

        # write to trace list depending on doorID
        if doorID == '1':
            # write to plotly
            s1.write(dict(x=x, y=lastDoorState1))
            s1.write(dict(x=x, y=y))
            lastDoorState1 = y
        if doorID == '2':
            # write to plotly
            s2.write(dict(x=x, y=lastDoorState2))
            s2.write(dict(x=x, y=y))
            lastDoorState2 = y
        if doorID == '3':
            # write to plotly
            s3.write(dict(x=x, y=lastDoorState3))
            s3.write(dict(x=x, y=y))
            lastDoorState3 = y
        if doorID == '4':
            # write to plotly
            s4.write(dict(x=x, y=lastDoorState4))
            s4.write(dict(x=x, y=y))
            lastDoorState4 = y

    # if length of cursor is greater than 0 update lastUpdate - causes error if no tuples returned.
    if count > 0:
        lastUpdate = str(insertTime)

    # repeat every 10 seconds
    time.sleep(10)

# close the stream when done plotting
s.close()
f.close()
cursor.close()
cnx.close()
