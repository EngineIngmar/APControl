#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""HCSR04.py
module script for HCSR04 sensor

dependencies:
GPIO module for python
https://pypi.python.org/pypi/RPi.GPIO
"""

import RPi.GPIO as IO
import time, datetime
from datetime import timedelta
import sys
import sqlite3 as lite

IO.setmode(IO.BCM)
IO.setwarnings(False)

"""read distance of a HCSR04 sensor
exception handling and write in database
return values"""
def readLevel(dbName,trig,echo,ground):
    try:
        """trig send ultrasonic signal"""
        IO.setup(trig, IO.OUT)
        """echo receive signal"""
        IO.setup(echo, IO.IN)
        """send ultrasonic signal"""
        IO.output(trig, True)
        time.sleep(0.00001)
        IO.output(trig, False)
        """set time measurement"""
        start = datetime.datetime.now()
        stop = datetime.datetime.now()
        """Because the sound pulse sometimes does not return, the measuring time must be limited."""
        measurementDur = datetime.datetime.now() + timedelta(milliseconds = 500)
        """The monitoring of the echo is limited to 0.5 seconds."""
        while (IO.input(echo) == 0) and (datetime.datetime.now() < measurementDur):
            start = datetime.datetime.now()
        measurementInc = datetime.datetime.now() + timedelta(milliseconds = 500)
        while (IO.input(echo) == 1) and (datetime.datetime.now() < measurementDur):
            stop = datetime.datetime.now()
        delta =  (stop - start).total_seconds()
        """multiply by sonic speed and divide by 2"""
        distance = (delta * 34300) / 2
        level = ground-distance
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('HCSR04.py readLevel',?)",[repr(e)])
        db.commit()
        db.close()
    return level

"""return List of sensors type HCSR04"""
def getSensorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_sensor WHERE type='HCSR04'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('HCSR04.py getSensorList',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    return options

"""log sensor value in database"""
def logSensorValue(dbName,id,level):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute('SELECT LEVEL_cm FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        """Check whether there is already a value in the database. 
        If not, lastValue set to zero."""
        lastValue = cursor.fetchone()
        if lastValue is None:
            lastValue = [0]
        else:
            lastValue = lastValue[0]
        if level != lastValue:
            cursor.execute("INSERT INTO Log_system(ID,LEVEL_cm) VALUES(?,?)",(id,level))
        db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('HCSR04.py logSensorValue',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""return last logged level"""
def getSensorValue(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,LEVEL_cm FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        sensorValue = cursor.fetchone()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('HCSR04.py getSensorValue',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return sensorValue[1]

if __name__ == '__main__':
    print('no main function defined')

