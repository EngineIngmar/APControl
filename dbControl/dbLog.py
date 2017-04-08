#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""dbLog.py
input: dbName, module and message

simple script for logging system messages in database
"""
import sqlite3 as lite

def softwareLog(dbName, module, message):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES(?,?)",(module, message))
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db.close()

if __name__ == '__main__':
    print('no main function defined')