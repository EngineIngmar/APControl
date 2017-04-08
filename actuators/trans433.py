#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""trans433.py
input: 433Mhz code ready for transmit
output: NULL
simple script for switching a 443Mhz actuator
preparation
install wiring pi
git clone git://git.drogon.net/wiringPi && cd wiringPi &&./build
install 433Utils
git clone https://github.com/ninjablocks/433Utils.git --recursive
get code with installed 433Mhz receiver and sudo ./RFSniffer
install 433 transmitter ATAD-Pin at GPIO17
create new c-file in folder 433Utils/RPi_utils: sudo nano control.cpp
Code:
    #include "../rc-switch/RCSwitch.h"
    #include <stdlib.h>
    #include <stdio.h>
    
    int main(int argc, char *argv[]) {
        int PIN = 0; // wiring Pi pin layout
        int codeSocketDon = atoi(argv[1]);

        if (wiringPiSetup() == -1) return 1;

        RCSwitch mySwitch = RCSwitch();
        mySwitch.enableTransmit(PIN);

        mySwitch.send(codeSocketDon, 24);
        return 0;
    }
compile file
g++ -DRPI ../rc-switch/RCSwitch.cpp control.cpp -o control -lwiringPi
create new bash-script /usr/local/bin/433.sh
Code:
sudo path/to/433Utils/RPi_utils/control $1
add file to sudoers
"""

import subprocess
import sqlite3 as lite

"""simple script for call a script for sending the 433Mhz code"""
def send433(dbName,id,state,code):
    #call 433Mhz code send script with exception logging
    try:
        subprocess.call(['sudo','433.sh',str(code)])
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('trans433.py send433.sh',?)",[repr(e)])
        db.commit()
        db.close()
    #log set state in database
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute("INSERT INTO Log_system(ID,STATE_target) VALUES(?,?)",(id,state))
        db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('trans433.py log state',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""send 433MHz code in condition of set target state"""
def conditionalSend433(dbName,id,actTargetState,codeOn,codeOff):       
    if getActuatorTargetState(dbName,id) != actTargetState:
        if actTargetState == 1: 
            send433(dbName,id,1,int(codeOn))  
        else:
            send433(dbName,id,0,int(codeOff))
                    
"""return List of actuators type relais
id    type    pin    433_on    433_off
"""
def getActuatorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_actuator WHERE type='433'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('trans433.py getActuatorList',?)",[repr(e)])
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