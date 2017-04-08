#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""dbQuery.py
simple script for executing a sql query
input: dbName, sql query
return: query result
"""

import sqlite3 as lite
import sys, traceback

def dbQuerySelect(dbName, query):
    try:
        db = lite.connect(dbName)
        cursor = db.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        db.commit()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        cursor.execute("INSERT INTO Log_software(MODULE,MESSAGE) VALUES(?,?)",('dbQuery.py','sql error: ' + str(err)))
        db.commit()
        return 
    finally:
        db.close()
    return result

if __name__ == '__main__':
    print('no main function defined')