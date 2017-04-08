#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""APLog.py
logging script, taking snapshots of the system

dependencies:
sensor and actuator modules
"""

from sensors import DHT22, D18B20, HCSR04, LFM, BH1750
from dbControl import dbLog

import sqlite3 as lite
import datetime
from datetime import timedelta
import time
import sys, traceback


def main():
   
    #set database name
    dbName='APDatabase.sqlite'
    dbLog.softwareLog(dbName,'APLog.py','script started')
    time.sleep(1)
    
    """get options list per sensor type
    Options_sensor table:
    id    type    gpio    gpio_trig    gpio_echo    w1_id    bed_cm    increment_sec    i2c_id
    """
    DHT22List = DHT22.getSensorList(dbName)
    D18B20List = D18B20.getSensorList(dbName)
    HCSR04List = HCSR04.getSensorList(dbName)
    LFMList = LFM.getSensorList(dbName)
    BH1750List = BH1750.getSensorList(dbName)
    dbLog.softwareLog(dbName,'APLog.py','sensors imported (DHT22: %s, D18B20: %s, HCSR04: %s, LFM: %s, BH1750: %s)' % (len(DHT22List),len(D18B20List),len(HCSR04List),len(LFMList),len(BH1750List)))
    time.sleep(1)
    #set intitial log time
    logTime = datetime.datetime.now()
    
    """read snapshot increment time in min from database"""
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT VALUE FROM Opt_general WHERE PARAMETER='snapshotIncrement'")
        snapInc = int(cursor.fetchone()[0])
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('APLog.py Opt_general',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    
    """start endless logging loop and wait for correct insert in database"""
    dbLog.softwareLog(dbName,'APLog.py','start endless loop...')
    time.sleep(1)
    try:
        while True:
            try:
                if logTime < datetime.datetime.now():
            
                    #read and log all D18B20 sensors
                    for row in D18B20List:
                        id = row[0]
                        temp = D18B20.readTemp(dbName,row[5])
                        D18B20.logSensorValue(dbName,id,round(temp,2))
                    #read and log all DHT22 sensors
                    for row in DHT22List:
                        id = row[0]
                        temp = DHT22.readTempHum(dbName,row[2])[0]
                        hum = DHT22.readTempHum(dbName,row[2])[1]
                        if (hum != None) and (temp != None):
                            DHT22.logSensorValue(dbName,id,round(temp,2),round(hum,2))
                        
                    #read and log all HCSR04 sensors
                    for row in HCSR04List:
                        id = row[0]
                        level = HCSR04.readLevel(dbName,row[3],row[4],row[6])
                        HCSR04.logSensorValue(dbName,id,round(level,2)) 
                    
                    #read and log all LFM sensors
                    for row in LFMList:
                        id = row[0]
                        flow = LFM.readFlow(dbName,row[2])
                        LFM.logSensorValue(dbName,id,round(flow,2))
                    
                    """read and log all BH1750 sensors"""
                    for row in BH1750List:
                        id = row[0]
                        light = BH1750.readLight(dbName,row[8])
                        BH1750.logSensorValue(dbName,id,round(light,2))
                    
                    #set new logging time with general increment
                    logTime = logTime + timedelta(minutes=snapInc)
            except TypeError as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                dbLog.softwareLog(dbName,'APLog.py','sensor error: ' + str(err)) 
            """pause to limit the cpu usage"""
            time.sleep(0.1)  
            
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        dbLog.softwareLog(dbName,'APLog.py','critical error: ' + str(err)) 

if __name__ == '__main__':
    main()