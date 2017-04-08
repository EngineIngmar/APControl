# APControl
control, monitor and logging of aquaponic 

APControl is designed to control and monitor aquaponic systems. The software is still in final development and there is still no stable release. APControl is developed for a Raspberry Pi 3. On other models, the software has not yet been tested.

Use is at your own risk. No liability is accepted for damages to fish, plants, humans or technology.

Look at the software structure for a better understanding: [APControl structure](APControl structure 1704.pdf)

APControl has a modular structure and initially performs basic functions:
  Switching actuators by time (time) and by interval
  Reading of 5 sensor types
  Log into a sqlite database
  Upload of sensor values and states to thingspeak.com
  Monitor the condition of the equipment and the software
