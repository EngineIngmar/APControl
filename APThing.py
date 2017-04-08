#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""APThing.py
cloud logging script, upload database entries

dependencies:
installed database
thingspeak: install with 
pip3 install thingspeak
"""

from dbControl import dbLog,dbQuery
from sensors import DHT22, D18B20, HCSR04, LFM,BH1750
from actuators import relais, trans433

import sqlite3 as lite
import datetime
from datetime import timedelta
import time
import thingspeak
import sys, traceback


def main():
    dbName='APDatabase.sqlite'
    dbLog.softwareLog(dbName,'APThing.py','script started')
    time.sleep(1)
    """get sensor options list
    Options_sensor table:
    id    type    gpio    gpio_trig    gpio_echo    w1_id    bed_cm    increment_sec i2c_id"""
    sensorList = dbQuery.dbQuerySelect(dbName,'SELECT * FROM Opt_sensor')
    
    """get actuator options list 
    Options_sensor table:
    id    type    pin    433_on    433_off    time_opt"""
    actuatorList = dbQuery.dbQuerySelect(dbName,'SELECT * FROM Opt_actuator')
    
    """get thingspeak upload increment from general options"""
    thingIncrement = int(dbQuery.dbQuerySelect(dbName,'SELECT VALUE FROM Opt_general WHERE PARAMETER = "thingSpeakIncrement"')[0][0])
    thingStart = datetime.datetime.now()
    
    """get individual setup for the desired thing speak channel"""
    thingOpt = dbQuery.dbQuerySelect(dbName,'SELECT * FROM Opt_thing')[0]
    
    """set thingspeak channel options"""
    channel_id = thingOpt[0]
    write_key  = thingOpt[1]
    read_key   = thingOpt[2]
    channel = thingspeak.Channel(id=channel_id, write_key=write_key, api_key=read_key)
    updateList = [0,0,0,0,0,0,0,0]
    
    try:
        """start endless loop and wait for correct insert in database"""
        dbLog.softwareLog(dbName,'APThing.py','start endless loop...')
        time.sleep(1)
        while True:
            now = datetime.datetime.now()
            if thingStart < now:
                for colThing in range(0,8):
                    thingOptIndex = colThing + 3
                    
                    """check sensorList and update the thing speak response list"""
                    for row in sensorList:
                        id = row[0]
                        sensorType = row[1]
                        """Because the dht22 provides two values ​​must be differentiated here""" 
                        if sensorType == 'DHT22':
                            idDHT = str(id) + '_T'
                            if idDHT == thingOpt[thingOptIndex]: updateList[colThing] = DHT22.getSensorValue(dbName,id)[0]
                            idDHT = str(id) + '_H'
                            if idDHT == thingOpt[thingOptIndex]: updateList[colThing] = DHT22.getSensorValue(dbName,id)[1]
                        else:
                            if id == thingOpt[thingOptIndex]:
                                if sensorType == 'D18B20': updateList[colThing] = D18B20.getSensorValue(dbName,id)
                                if sensorType == 'HCSR04': updateList[colThing] = HCSR04.getSensorValue(dbName,id)
                                if sensorType == 'LFM': updateList[colThing] = LFM.getSensorValue(dbName,id)
                                if sensorType == 'BH1750': 
                                    updateList[colThing] = BH1750.getSensorValue(dbName,id)
                                    print(updateList[colThing])
                    
                    """check actuatorList and update the thing speak response list"""   
                    for row in actuatorList:
                        id = row[0]
                        actType = row[1]
                        if id == thingOpt[thingOptIndex]:
                            if actType == 'PIN': updateList[colThing] = relais.getActuatorTargetState(dbName,id)
                            if actType == '433': updateList[colThing] = trans433.getActuatorTargetState(dbName,id)
                    
                try:
                    response = channel.update({'field1': updateList[0], 'field2': updateList[1], 'field3': updateList[2], 'field4': updateList[3], 'field5': updateList[4],'field6': updateList[5],'field7': updateList[6],'field8': updateList[7]})
                except Exception as e:
                    dbLog.softwareLog(dbName,'APThing.py','upload error: ' + str(e))
                  
                thingStart = thingStart + timedelta(minutes = thingIncrement)
            """pause to limit the cpu usage"""
            time.sleep(0.1)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        dbLog.softwareLog(dbName,'APThing.py','critical error: ' + str(err)) 
    
if __name__ == '__main__':
    main()