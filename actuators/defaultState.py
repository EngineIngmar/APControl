#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""defaultState.py
simple script to deactivate all actuators
"""
import time
from actuators import relais
from actuators import trans433

"""set default actuator states"""
def deactivateAll(dbName,actuatorListOptions):
    for row in actuatorListOptions:
        id = str(row[0])
        actType = str(row[1])
        if actType == "PIN":
            pin = int(row[2])
            relais.switch(dbName,id,pin,0)
        if actType == "433":
            t433_off = int(row[4])
            trans433.send433(dbName,id,0,t433_off)