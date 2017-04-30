#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""DHT22.py
module script vor DHT22-sensor

dependencies:
Driver for python3
git clone https://github.com/JoBergs/Adafruit_Python_DHT
sudo apt-get install build-essential python3-dev
cd Adafruit_Python_DHT
sudo python3 setup.py install"""

import Adafruit_DHT
import sys
import sqlite3 as lite

"""read temperature and humdity of a DHT22 sensor
exception handling and write in database
return values"""
def readTempHum(dbname,pin):
    try:
        humidity = None
        temperature = None
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
    except Exception as e:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('DHT22.py readTempHum',?)",[repr(e)])
        db.commit()
        db.close()
    return temperature, humidity

"""return List of sensors type DHT22
id    type    gpio    gpio_trig    gpio_echo    w1_id    bed_cm    increment_sec
"""
def getSensorList(dbName):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Opt_sensor WHERE type='DHT22'")
        options = cursor.fetchall()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('DHT22.py getSensorList',?)",[repr(e)])
        db.commit()
    finally:
        db.close()
    return options

"""log sensors values in database"""
def logSensorValue(dbName,id,temp,hum):
    try:
        lastvalue = []
        db = lite.connect(dbName)
        cursor = db.cursor()
        #id    TIMESTAMP    STATE_actual    STATE_target    TEMP_C    HUM_per    LEVEL_cm    FLOW_lmin
        cursor.execute('SELECT TIMESTAMP,TEMP_C FROM Log_system WHERE ID=? AND TEMP_C IS NOT NULL ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        """Check whether there is already a value in the database. If not, lastValue set to zero."""
        lastTemp = cursor.fetchone()[1]
        cursor.execute('SELECT TIMESTAMP,HUM_per FROM Log_system WHERE ID=? AND HUM_per IS NOT NULL ORDER BY TIMESTAMP DESC LIMIT 1',[id])
        """Check whether there is already a value in the database. If not, lastValue set to zero."""
        lastHum = cursor.fetchone()[1]
        
        if lastTemp is None:
            lastTemp = 0
        else:
            lastTemp = lastTemp
        print(temp)
        if (temp != lastTemp) or (hum != lastHum):
            if (0 <= hum <= 100):
                cursor.execute("INSERT INTO Log_system(ID,HUM_per) VALUES(?,?)",(id,hum))
                db.commit()
            if (abs(lastTemp - temp) <= 5):
                cursor.execute("INSERT INTO Log_system(ID,TEMP_C) VALUES(?,?)",(id,temp))
                db.commit()
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('DHT22.py logSensorValue',?)",[repr(e)])
        db.commit()
    finally:
        db.close()

"""return last logged temperature and humidity"""
def getSensorValue(dbName,id):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("SELECT TIMESTAMP,TEMP_C FROM Log_system WHERE ID=? AND TEMP_C IS NOT NULL ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        temp = cursor.fetchone()[1]
        cursor.execute("SELECT TIMESTAMP,HUM_per FROM Log_system WHERE ID=? AND HUM_per IS NOT NULL ORDER BY TIMESTAMP DESC LIMIT 1",[id]);
        hum = cursor.fetchone()[2]
        sensorValue = [temp,hum]
    except Exception as e:
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES('DHT22.py getSensorValue',?)",[repr(e)])
        db.commit()
        return []
    finally:
        db.close()
    return sensorValue
        
if __name__ == '__main__':
    print('no main function defined')
