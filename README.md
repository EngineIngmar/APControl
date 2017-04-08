# APControl
**control, monitor and logging of aquaponic systems**

a project by EngineIngmar

## introduction

APControl is designed to control and monitor aquaponic systems. The software is still in final development and there is still no stable release. APControl is developed for a Raspberry Pi 3. On other models, the software has not yet been tested.

Use is at your own risk. No liability is accepted for damages to fish, plants, humans or technology.

Look at the software structure for a better understanding: 
[APControl structure](https://github.com/EngineIngmar/APControl/blob/master/APControl%20structure%201704.pdf)

## functions

APControl has a modular structure and initially performs basic functions:
- Switching actuators by time (time) and by interval
- Reading of 5 sensor types
- Log into a sqlite database
- Upload of sensor values and states to thingspeak.com
- Monitor the condition of the equipment and the software

## module description
**APControl.py** 

Checks the actuators of the aquaponic system. The actuators are switched according to the switching times and switching intervals stored in the database. The state changes are written to the database.

**APLog.py** 

The module reads out the parameters recorded by the sensors according to the options stored in the database (eg pin assignment) and sets the values in the database. If the measured value does not deviate from the predecessor, no value is stored.

**APGuard.py** 

The module monitors the status of the other software modules and feeds deviations from the desired state into the database. Furthermore, the set limit values of individual sensors are checked and deviations stored in the database.

**APThing.py** 

Loads the last stored state in the database into a thingspeakchannel.
