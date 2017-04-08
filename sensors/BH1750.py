#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""BH1750.py
module script for light sensor BH 1750

dependencies:
installed sensor on I2C Bus
"""

import smbus
import time
import sys
import sqlite3 as lite

"""read light data
exception handling and write in database
return values"""
def readLight(dbName,i2cId):
    try:
        """set sensor control codes from datasheet"""
        ONE_TIME_LOW_RES_MODE = 0x23 #read mode
        """set bus to smbus"""
        bus = smbus.SMBus(1) 
        light = bus.read_i2c_block_data(int(i2cId,0),ONE_TIME_LOW_RES_MODE)
        """convert to decimal value"""
        light = ((light[1] + (256 * light[0])) / 1.2)
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('BH1750.py readLight',?)",[repr(e)])
        db.commit()
        db.close()
    return light

"""return List of sensors type BH1750"""
def getSensorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_sensor WHERE type='BH1750'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('BH1750.py getSensorList',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    return options

"""log sensor value in database"""
def logSensorValue(dbName,id,light):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin Light_lux
        cursor.execute('SELECT LIGHT_lux FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        
        """Check whether there is already a value in the database. 
        If not, lastValue set to zero."""
        lastValue = cursor.fetchone()
        if lastValue is None:
            lastValue = [0]
        else:
            lastValue = lastValue[0]
        if light != lastValue:
            cursor.execute("INSERT INTO Log_system(ID,LIGHT_lux) VALUES(?,?)",(id,light))
        db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('BH1750.py logSensorValue',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""return last logged light data"""
def getSensorValue(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,LIGHT_lux FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        sensorValue = cursor.fetchone()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('BH1750.py getSensorValue',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return sensorValue[1]

if __name__ == '__main__':
    print('no main function defined')