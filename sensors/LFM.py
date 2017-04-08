#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""LFM.py
module script for LFM sensor
"""

import RPi.GPIO as IO
import time
import sys
import sqlite3 as lite

IO.setmode(IO.BCM)

#counter for pulse event listener    
def countPulse(channel):
    global count
    if start_counter == 1:
        count = count+1
    
def readFlow(dbName,pin):
    try:
        #setup for event listener
        IO.setup(pin, IO.IN, pull_up_down = IO.PUD_UP)
        global count
        count = 0
        global start_counter
        start_counter = 1
        #add event listener, count pulses
        IO.add_event_detect(pin, IO.FALLING, callback=countPulse) #
        time.sleep(1)
        start_counter = 0
        IO.remove_event_detect(pin)
        #convert countet pulses in flow rate in l/min
        flow = (count * 60 * 2.25 / 1000)
        count = 0
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('LFM.py readFlow',?)",[repr(e)])
        db.commit()
        db.close()
    return flow

"""return List of sensors type LFM"""
def getSensorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_sensor WHERE type='LFM'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('LFM.py getSensorList',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    return options

"""log sensor value in database"""
def logSensorValue(dbName,id,flow):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute('SELECT FLOW_lmin FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        """Check whether there is already a value in the database. 
        If not, lastValue set to zero."""
        lastValue = cursor.fetchone()
        if lastValue is None:
            lastValue = [0]
        else:
            lastValue = lastValue[0]
        if flow != lastValue:
            cursor.execute("INSERT INTO Log_system(ID,FLOW_lmin) VALUES(?,?)",(id,flow))
        db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('LFM.py logSensorValue',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""return last logged flow"""
def getSensorValue(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,FLOW_lmin FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        sensorValue = cursor.fetchone()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('LFM.py getSensorValue',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return sensorValue[1]

if __name__ == '__main__':
    print('no main function defined')