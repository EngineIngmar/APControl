#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""relais.py
simple script for switching a actuator pin
"""
import RPi.GPIO as IO
import sqlite3 as lite

IO.setwarnings(False)
IO.setmode(IO.BCM)

"""switch a GPIO pin"""
def switch(dbName,id,pin,state):
    IO.setup(pin, IO.OUT)
    IO.output(pin, state)
    #write state in database
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute("INSERT INTO Log_system(ID,STATE_target) VALUES(?,?)",(id,state))
        db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('relais.py switch',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

#switch a GPIO pin in condition of set target state
def conditionalSwitch(dbName,id,actTargetState,pin):
    if getActuatorTargetState(dbName,id) != actTargetState:
        switch(dbName,id,pin,actTargetState)

"""return List of actuators type relais
id    type    pin    433_on    433_off
"""
def getActuatorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_actuator WHERE type='PIN'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('relais.py getActuatorList',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return options

"""return last logged target state"""
def getActuatorTargetState(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,STATE_target FROM Log_system WHERE ID=? ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        actuatorState = cursor.fetchone()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('trans433.py getActuatorTargetState',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return actuatorState[1]

if __name__ == '__main__':
    print('no main function defined')