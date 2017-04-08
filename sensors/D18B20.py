#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""D18B20.py
module script für D18B20 Sensor

dependencies:
get ID from /sys/bus/w1/devices"""

import os #zugriff auf Dateisystem
import Adafruit_DHT
import sys
import sqlite3 as lite

"""read temperature of a D18B20 sensor
exception handling and write in database
return value"""
def readTemp(dbName,ID):
    try:
        # read sensor output in file
        datafile = open('/sys/bus/w1/devices/' + ID + '/w1_slave')
        datareader = datafile.read()
        datafile.close()
        # get temperature and convert
        string_val = datareader.split("\n")[1].split(" ")[9]
        temperature = float(string_val[2:]) / 1000
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('D18B20.py readTemp',?)",[repr(e)])
        db.commit()
        db.close()
    return temperature

"""return List of sensors type D18B20"""
def getSensorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_sensor WHERE type='D18B20'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('D18B20.py getSensorList',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    return options

"""log sensor value in database"""
def logSensorValue(dbName,id,temp):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute('SELECT TEMP_C FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        """Check whether there is already a value in the database. 
        If not, lastValue set to zero."""
        lastValue = cursor.fetchone()
        if lastValue is None:
            lastValue = [0]
        else:
            lastValue = lastValue[0]
        if temp != lastValue:
            cursor.execute("INSERT INTO Log_system(ID,TEMP_C) VALUES(?,?)",(id,temp))
        db.commit()
    except Exception as e:
        print (e)
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('D18B20.py logSensorValue',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""return last logged temperature"""
def getSensorValue(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,TEMP_C FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        sensorValue = cursor.fetchone()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('D18B20.py getSensorValue',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return sensorValue[1]
    
if __name__ == '__main__':
    print('no main function defined')
