#!/usr/bin/python3

import ev3dev.ev3 as ev3

leftM = ev3.LargeMotor('outC')
rightM = ev3.LargeMotor('outB')
servoM=ev3.MediumMotor('outD')
leftM.stop_action='brake'
rightM.stop_action='brake'
servoM.stop_action='brake'
leftM.stop()
rightM.stop()
servoM.stop()
