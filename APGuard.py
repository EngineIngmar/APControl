#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""APGuard.py
check software and system status 

dependencies:
installed database
"""

from dbControl import dbLog,dbQuery
from sensors import DHT22, D18B20, HCSR04, LFM

import sqlite3 as lite
import datetime
from datetime import timedelta,datetime
import time
import sys, traceback,os
import subprocess
import os

def checkProcess(dbName,procName,currentPath,critical):
    try:
        processCommand = 'python3 ' + currentPath +'/' + procName
        pgrepCall = subprocess.check_output('pgrep -x -f "%s"' %processCommand, shell = True)
        pgrepCall = int(pgrepCall.decode('utf-8'))
        processState = 1
    except subprocess.CalledProcessError as e:
        if e.returncode > 1:
            raise
        
        dbLog.softwareLog(dbName,'APGuard.py','%s error: %s not running' % (critical, procName))
        processState = 0
        
    return processState

def checkOnline(dbName):
    """check online status with google dns server"""
    response = os.system('ping -c 3 ' + '8.8.8.8')
    # check the response
    if response == 0:
        pingstatus = 'online'
    else:
        pingstatus = 'offline'
    return pingstatus

def main():
    dbName='APDatabase.sqlite'
    currentPath = os.getcwd()
    criticalErrors, minorErrors, connectionErrors = 0, 0, 0 
    
    dbLog.softwareLog(dbName,'APGuard.py','script started')
    time.sleep(1)
    
    """get cooldown time for reboot"""
    rebootCooldown = dbQuery.dbQuerySelect(dbName,'SELECT VALUE FROM Opt_general WHERE PARAMETER = "rebootCooldown"')[0][0]
    
    """get TIMESTAMP of last reboot log and convert string to datetime and set to now, if no reboot time is logged"""
    try:
        rebootTime = dbQuery.dbQuerySelect(dbName,'SELECT TIMESTAMP FROM Log_software WHERE MODULE = "APGuard.py" AND MESSAGE LIKE "raspberry reboot%" ORDER BY TIMESTAMP DESC LIMIT 1')[0][0]
        rebootTime = datetime.strptime(rebootTime, '%Y-%m-%d %H:%M:%S')
        minRebootTime = rebootTime + timedelta(minutes=rebootCooldown)
    except (UnboundLocalError, IndexError) as e:
        minRebootTime = datetime.now()
        
    """get system limitations"""
    limitList = dbQuery.dbQuerySelect(dbName,'SELECT * FROM Opt_limit')
    
    """get sensor options list
    Options_sensor table:
    id    type    gpio    gpio_trig    gpio_echo    w1_id    bed_cm    increment_sec
    """
    sensorList = dbQuery.dbQuerySelect(dbName,'SELECT * FROM Opt_sensor')
    
    checkTime = datetime.now()
    """get increment for checking the system and software status"""
    checkInc = dbQuery.dbQuerySelect(dbName,'SELECT VALUE FROM Opt_general WHERE PARAMETER = "checkIncrement"')[0][0]
    
    dbLog.softwareLog(dbName,'APGuard.py','start endless loop...')
    time.sleep(1)
    while True:
        if checkTime < datetime.now():
            """check software status"""
            if checkProcess(dbName,'APControl.py',currentPath,'critical') == 0:
                criticalErrors = criticalErrors + 1
            if checkProcess(dbName,'APLog.py',currentPath,'critical') == 0:
                criticalErrors = criticalErrors + 1
            if checkProcess(dbName,'APThing.py',currentPath,'') == 0:
                minorErrors = minorErrors + 1
            
            """check system status"""
            for rowLimit in limitList:
                for rowSensor in sensorList:
                    if rowLimit[0] == rowSensor[0]:
                        """check each sensor type"""
                        if rowSensor[1] == 'D18B20': sensorValue = D18B20.getSensorValue(dbName,rowLimit[0])
                        if rowSensor[1] == 'HCSR04': sensorValue = HCSR04.getSensorValue(dbName,rowLimit[0])
                        if rowSensor[1] == 'LFM': sensorValue = LFM.getSensorValue(dbName,rowLimit[0])
                        if rowSensor[1] == 'DHT22':
                            if rowLimit[1] == 'C': sensorValue = DHT22.getSensorValue(dbName,rowLimit[0])[0]
                            if rowLimit[1] == '%': sensorValue = DHT22.getSensorValue(dbName,rowLimit[0])[1]
                        
                        #insert external communication modul
                        if sensorValue <= rowLimit[2]:
                            dbLog.softwareLog(dbName,'APGuard.py','system min error: %s (lower limit: %s %s - actual value: %s %s)' % (rowLimit[0],rowLimit[2],rowLimit[1],sensorValue,rowLimit[1]))
                        if sensorValue >= rowLimit[3]:
                            dbLog.softwareLog(dbName,'APGuard.py','system max error: %s (upper limit: %s %s - actual value: %s %s)' % (rowLimit[0],rowLimit[3],rowLimit[1],sensorValue,rowLimit[1]))
            
            """check online status"""
            if checkOnline(dbName) == 'offline':
                connectionErrors = connectionErrors + 1
                dbLog.softwareLog(dbName,'APGuard.py','system offline (connection errors: %s)' %connectionErrors)
                time.sleep(1)
            else:
                connectionErrors = 0
             
            """if the connection test is ten times false, a critical error is logged"""
            if connectionErrors > 9:
                criticalErrors = criticalErrors + 1
            
            now = datetime.now()
            
            if criticalErrors > 0 and now > minRebootTime:
                dbLog.softwareLog(dbName,'APGuard.py','raspberry reboot (critical errors: %s)' %criticalErrors)
                #insert external communication modul
                time.sleep(3)
                os.system('sudo shutdown -r now')
            
            """set new check time with general increment"""
            checkTime = checkTime + timedelta(minutes=checkInc)
        
        time.sleep(0.1)    
if __name__ == '__main__':
    main()
