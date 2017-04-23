#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""APControl.py
control system actuators and log states

dependencies:
actuator modules
"""

from actuators import relais, trans433, defaultState
from dbControl import dbLog

import sqlite3 as lite
import time, datetime
from datetime import timedelta
import sys, traceback


def main():
    """set database name"""
    dbName='APDatabase.sqlite'
    
    dbLog.softwareLog(dbName,'APControl.py','script started')
    actuatorTimePeriod = []
    actuatorTimeIncrement= []
    time.sleep(1)
    
    """get options list per actuator type
    Options_sensor table:
    id    type    pin    433_on    433_off    time_opt
    """
    actuatorListOptions = relais.getActuatorList(dbName) + trans433.getActuatorList(dbName)
    dbLog.softwareLog(dbName,'APControl.py','%s actuators imported' % len(actuatorListOptions))
    time.sleep(1)
    """The actuatorList is split into two lists according to the switching option."""
    for row in actuatorListOptions:
        try:
            id = str(row[0])
            time_opt = str(row[5])
            db = lite.connect(dbName)
            cursor = db.cursor()
            
            """actuators switching by time"""
            if time_opt == "period":
                cursor.execute("SELECT ID,START,END FROM Opt_time WHERE ID=?",[row[0]])
                actuatorTimePeriod = actuatorTimePeriod + cursor.fetchall()
            
            """actuators switching by increment and duration"""
            if time_opt == "increment":
                cursor.execute("SELECT ID,INCREMENT_min,DURATION_min FROM Opt_time WHERE ID=?",[row[0]])
                actuatorTimeIncrement = actuatorTimeIncrement + cursor.fetchall()
        
        except Exception as e:
            cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('APControl.py Opt_time',?)",[repr(e)])
            db.commit()
        finally:
            db.close
            
    """create list for actuators switched by increment to set initial start and end time"""
    now = datetime.datetime.now()
    actuatorTimeIncrementPoints =[]
    for row in actuatorTimeIncrement:
        duration = float(row[2])
        actuatorTimeIncrementPoints = actuatorTimeIncrementPoints + [[row[0], now, now + timedelta(seconds=duration*60)]]  
    
    """set default actuator states"""
    defaultState.deactivateAll(dbName,actuatorListOptions)
    
    """start endless control loop and wait for correct insert"""
    dbLog.softwareLog(dbName,'APControl.py','start endless loop...')
    time.sleep(1)
    try:
        while True:
            now = datetime.datetime.now()
            
            """check target state by actuator"""
            for rowOpt in actuatorListOptions:
                id = str(rowOpt[0])
                time_opt = str(rowOpt[5])
                actType = str(rowOpt[1])
                
                """switch actuators by time"""
                if time_opt == 'period':
                    now = datetime.datetime.now()
                    
                    """check target states by time table"""
                    for rowTime in actuatorTimePeriod:
                        rowStart = rowTime[1]
                        rowEnd = rowTime[2]
                        if rowTime[0] == id:
                            
                            """set start and end time to current date"""
                            actStart = now.replace(hour=int(rowStart[:2]),minute=int(rowStart[3:]),second=0,microsecond=0)
                            actEnd = now.replace(hour=int(rowEnd[:2]),minute=int(rowEnd[3:]),second=0,microsecond=0)
                            
                            """if target state is 1"""
                            if actStart <= now <= actEnd:
                                actTargetState = 1
                                """leave inner loop"""
                                break
                            else:
                                """target state is 0"""
                                actTargetState = 0
                    
                    """call conditional switch functions of the actuators"""
                    if actType == 'PIN': relais.conditionalSwitch(dbName,id,actTargetState,rowOpt[2])
                    if actType == '433': trans433.conditionalSend433(dbName,id,actTargetState,rowOpt[3],rowOpt[4])
                               
                """switch actuators by increment"""
                if time_opt == 'increment':
                    now = datetime.datetime.now()
                    """check target states by time table"""
                    for row in range(0, len(actuatorTimeIncrementPoints)):
                        now = datetime.datetime.now()
                        
                        """if id of actuator of inner loop (increment points) is equal to id of outer loop"""
                        if id == actuatorTimeIncrementPoints[row][0]:
                            
                            """get duration an incrment of actual actuator"""
                            duration = float(actuatorTimeIncrement[row][2])
                            increment = float(actuatorTimeIncrement[row][1])
                            
                            """if it is later than the start time set state witch actuator on"""
                            if actuatorTimeIncrementPoints[row][1] < now:
                                actTargetState = 1
                                
                                """call conditional switch functions of the actuators"""
                                if actType == 'PIN': relais.conditionalSwitch(dbName,id,actTargetState,rowOpt[2])
                                if actType == '433': trans433.conditionalSend433(dbName,id,actTargetState,rowOpt[3],rowOpt[4])
                                
                                """set new start an end time in dependence of the increment and duration"""
                                actuatorTimeIncrementPoints[row][2] = actuatorTimeIncrementPoints[row][1] + timedelta(minutes=duration)
                                actuatorTimeIncrementPoints[row][1] = actuatorTimeIncrementPoints[row][1] + timedelta(minutes=increment)
                            
                            """if it is later than the end time set wtich actuator off"""     
                            if actuatorTimeIncrementPoints[row][2] < now: 
                                """target state is 0"""
                                actTargetState = 0
                               
                                """call conditional switch functions of the actuators"""
                                if actType == 'PIN': relais.conditionalSwitch(dbName,id,actTargetState,rowOpt[2])
                                if actType == '433': trans433.conditionalSend433(dbName,id,actTargetState,rowOpt[3],rowOpt[4])
            
            """pause to limit the cpu usage"""
            time.sleep(0.1)                   
                       
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        dbLog.softwareLog(dbName,'APControl.py','critical error: ' + str(err))
        defaultState.deactivateAll(dbName,actuatorListOptions)

if __name__ == '__main__':
    main()
