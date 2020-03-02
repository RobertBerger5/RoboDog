import ev3dev.ev3 as ev3
from ev3dev2.sensor import INPUT_1
from ev3dev2.port import LegoPort
from smbus import SMBus
from time import sleep
from random import randint

class PixyCam():
    def __init__(self):
        #set LEGO port for input 1
        self.in1=LegoPort(INPUT_1)
        self.in1.mode='other-i2c'
        sleep(0.5)
        #I2C bus settings
        self.bus=SMBus(3)
        self.address=0x54
        #w and h for its view
        try:
            data=[174,193,32,2,1,1]
            self.bus.write_i2c_block_data(self.address,0,data)
            self.bus.read_i2c_block_data(self.address,0,20)
        except OSError:
            print("ERROR! Check PixyCam connection")

    def findSignature(self,signature):
        data=[174,193,32,2,signature,1]
        self.bus.write_i2c_block_data(self.address,0,data)
        block=self.bus.read_i2c_block_data(self.address,0,20)
        x = block[9]*256 + block[8]
        y = block[11]*256 + block[10]
        w = block[13]*256 + block[12]
        h = block[15]*256 + block[14]
        #note: the camera resolution is 316x208
        return(x,y,w,h)
    
class SturdyBot(object):
    """This provides a higher-level interface to the sturdy Lego robot we've been working
    with."""

    # ---------------------------------------------------------------------------
    # Constants for the configDict
    LEFT_MOTOR = 'left-motor'
    RIGHT_MOTOR = 'right-motor'
    SERVO_MOTOR = 'servo-motor'
    LEFT_TOUCH = 'left-touch'
    RIGHT_TOUCH = 'right-touch'
    ULTRA_SENSOR = 'ultra-sensor'
    COLOR_SENSOR = 'color-sensor'
    GYRO_SENSOR = 'gyro-sensor'
    PIXY_CAM='pixy-cam'

    # ---------------------------------------------------------------------------
    # Setup methods, including constructor

    def __init__(self, robotName, configDict=None):
        """Takes in a string, the name of the robot, and an optional dictionary
        giving motor and sensor ports for the robot."""
        self.name = robotName
        self.leftMotor = ev3.LargeMotor('outC')
        self.rightMotor = ev3.LargeMotor('outB')
        self.servoMotor = ev3.MediumMotor('outD')
        self.servoMotor.reset()
        self.leftTouch = None
        self.rightTouch = None
        self.ultraSensor = ev3.UltrasonicSensor('in4')
        self.colorSensor = None
        self.gyroSensor = ev3.GyroSensor('in2')
        self.pixyCam=PixyCam() #input_1
        self.button=ev3.Button()
        ev3.Sound.set_volume(100)
        if configDict is not None:
            self.setupSensorsMotors(configDict)
        if self.leftMotor is None:
            self.leftMotor = ev3.LargeMotor('outC')
        if self.rightMotor is None:
            self.rightMotor = ev3.LargeMotor('outB')

    def setupSensorsMotors(self, configs):
        """Takes in a dictionary where the key is a string that identifies a motor or sensor
        and the value is the port for that motor or sensor. It sets up all the specified motors
        and sensors accordingly."""
        for item in configs:
            port = configs[item]
            if item == self.LEFT_MOTOR:
                self.leftMotor = ev3.LargeMotor(port)
            elif item == self.RIGHT_MOTOR:
                self.rightMotor = ev3.LargeMotor(port)
            elif item == self.SERVO_MOTOR:
                self.servoMotor = ev3.MediumMotor(port)
            elif item == self.LEFT_TOUCH:
                self.leftTouch = ev3.TouchSensor(port)
            elif item == self.RIGHT_TOUCH:
                self.rightTouch = ev3.TouchSensor(port)
            elif item == self.ULTRA_SENSOR:
                self.ultraSensor = ev3.UltrasonicSensor(port)
            elif item == self.COLOR_SENSOR:
                self.colorSensor = ev3.ColorSensor(port)
            elif item == self.GYRO_SENSOR:
                self.gyroSensor = ev3.GyroSensor("in1")
            else:
                print("Unknown configuration item:", item)

    def setMotorPort(self, side, port):
        """Takes in which side and which port, and changes the correct variable
        to connect to that port."""
        if side == self.LEFT_MOTOR:
            self.leftMotor = ev3.LargeMotor(port)
        elif side == self.RIGHT_MOTOR:
            self.rightMotor = ev3.LargeMotor(port)
        elif side == self.SERVO_MOTOR:
            self.servoMotor = ev3.MediumMotor(port)
        else:
            print("Incorrect motor description:", side)

    def setTouchSensor(self, side, port):
        """Takes in which side and which port, and changes the correct
        variable to connect to that port"""
        if side == self.LEFT_TOUCH:
            self.leftTouch = ev3.TouchSensor(port)
        elif side == self.RIGHT_TOUCH:
            self.rightTouch = ev3.TouchSensor(port)
        else:
            print("Incorrect touch sensor description:", side)

    def setColorSensor(self, port):
        """Takes in the port for the color sensor and updates object"""
        self.colorSensor = ev3.ColorSensor(port)

    def setUltrasonicSensor(self, port):
        """Takes in the port for the ultrasonic sensor and updates object"""
        self.ultraSensor = ev3.UltrasonicSensor(port)

    def setGyroSensor(self, port):
        """Takes in the port for the gyro sensor and updates object"""
        self.gyroSensor = ev3.GyroSensor(port)

    # ---------------------------------------------------------------------------
    # Methods to read sensor values

    def findSignature(self,signature):
        return self.pixyCam.findSignature(signature)
    

    def readTouch(self):
        """Reports the value of both touch sensors, OR just one if only one is connected, OR
        prints an alert and returns nothing if neither is connected."""
        if self.leftTouch is not None and self.rightTouch is not None:
            return self.leftTouch.is_pressed, self.rightTouch.is_pressed
        elif self.leftTouch is not None:
            return self.leftTouch.is_pressed, None
        elif self.rightTouch is not None:
            return None, self.rightTouch
        else:
            print("Warning, no touch sensor connected")
            return None, None

    def readReflect(self):
        if self.colorSensor is not None:
            reflected_value = self.colorSensor.reflected_light_intensity
            return reflected_value
        else:
            return None

    def readAmbient(self):
        if self.colorSensor is not None:
            ambient_value = self.colorSensor.ambient_light_intensity
            return ambient_value
        else:
            return None
    def readColor(self):
        if self.colorSensor is not None:
            color_value = self.colorSensor.color
            return color_value
        else:
            return None

    def readDistance(self):
        if self.ultraSensor is not None:
            distance = self.ultraSensor.distance_centimeters
            return distance
        else:
            return None
        
    def readHeading(self):
        if self.gyroSensor is not None:
            heading = self.gyroSensor.rate_and_angle[0]
            return heading % 360
        else:
            return None


    # ---------------------------------------------------------------------------
    # Methods to move robot

    def bork(self):
        ev3.Sound.play("bark"+str(randint(1,7))+".wav")

    def isStalled(self):
        if(self.leftMotor.is_stalled or self.rightMotor.is_stalled):
            return True
        return False

    def curve(self, leftspeed,rightspeed, time = None):
        self.leftMotor.speed_sp = max(min(self.leftMotor.max_speed * leftspeed,self.leftMotor.max_speed*.9),self.leftMotor.max_speed*-.9)
        self.rightMotor.speed_sp = max(min(self.rightMotor.max_speed * rightspeed,self.rightMotor.max_speed*.9),self.rightMotor.max_speed*-.9)
        if time != None:
            self.leftMotor.run_timed(time_sp = time)
            self.rightMotor.run_timed(time_sp = time)
            self.leftMotor.wait_until_not_moving()
        else:
            self.leftMotor.run_forever()
            self.rightMotor.run_forever()

    def forward(self, speed, time=None):
        max = self.leftMotor.max_speed
        self.leftMotor.speed_sp = max * speed
        self.rightMotor.speed_sp = max * speed

        if (time == None):
            self.leftMotor.run_forever()
            self.rightMotor.run_forever()
        else:
            self.leftMotor.run_timed(time_sp = time)
            self.rightMotor.run_timed(time_sp = time)
            self.leftMotor.wait_until_not_moving()
            
    def backward(self, speed, time=None):
        max = self.leftMotor.max_speed
        self.leftMotor.speed_sp = max * (-1.0) * speed
        self.rightMotor.speed_sp = max * (-1.0) * speed

        if (time == None):
            self.leftMotor.run_forever()
            self.rightMotor.run_forever()
        else:
            self.leftMotor.run_timed(time_sp = time)
            self.rightMotor.run_timed(time_sp = time)
            self.leftMotor.wait_until_not_moving()

    def turnLeft(self, speed, time=None):
        max = self.leftMotor.max_speed
        self.leftMotor.speed_sp = max * (-1.0) * speed
        self.rightMotor.speed_sp = max * speed

        if (time == None):
            self.leftMotor.run_forever()
            self.rightMotor.run_forever()
        else:
            self.leftMotor.run_timed(time_sp = time)
            self.rightMotor.run_timed(time_sp = time)
            self.leftMotor.wait_until_not_moving()
    
    def turnRight(self, speed, time=None):
        max = self.leftMotor.max_speed
        self.leftMotor.speed_sp = max * speed
        self.rightMotor.speed_sp = max * (-1.0) * speed

        if (time == None):
            self.leftMotor.run_forever()
            self.rightMotor.run_forever()
        else:
            self.leftMotor.run_timed(time_sp = time)
            self.rightMotor.run_timed(time_sp = time)
            self.leftMotor.wait_until_not_moving()

    def stop(self,action=None):
        if action!=None: #brake or coast
            self.leftMotor.stop_action = action
            self.rightMotor.stop_action = action
        self.leftMotor.stop()
        self.rightMotor.stop()

    def move(self, translateSpeed, rotateSpeed, runTime=None):
    	"""Takes in two speeds, a translational speed in the direction the robot is facing,
    	and a rotational speed both between -1.0 and 1.0 inclusively. Also takes in an
    	optional time in seconds for the motors to run.
    	It converts the speeds to left and right wheel speeds, and thencalls curve."""
    	wheelDist = 12 * 19.5
    	assert self.leftMotor is not None
    	assert self.rightMotor is not None
    	assert -1.0 <= translateSpeed <= 1.0
    	assert -1.0 <= rotateSpeed <= 1.0
    	transMotorSp = translateSpeed * self.leftMotor.max_speed
    	rotMotorSp = rotateSpeed * 2 # Note that technically rotational speed doesn't have the same units...
   	
    	# Here are formulas for converting from translate and rotate speeds to left and right
    	# These formulas need to know the distance between the two wheels in order to work
    	# which I measured to be 12 cm on my robot. But we have to watch out for units here
    	# the speeds are in "ticks" (degrees) per second, so we need to map rotational ticks
    	# to centimeters. I measured 360 ticks moving the robot 18.5 cm forward, so 1cm is
    	# 19.5 tics. Thus the wheel distance is 12 * 19.5 = 234 ticks.
    	leftSpeed = max(min((transMotorSp - (rotMotorSp * wheelDist) / 2.0),self.leftMotor.max_speed*3/4),self.leftMotor.max_speed*(-3)/4)
    	rightSpeed = max(min((transMotorSp + (rotMotorSp * wheelDist) / 2.0),self.rightMotor.max_speed*3/4),self.rightMotor.max_speed*(-3)/4)
    	#print("SPEEDS:", leftSpeed, rightSpeed)
    	self.leftMotor.speed_sp = leftSpeed
    	self.rightMotor.speed_sp = rightSpeed
    	self._moveRobot(runTime)
        #return rotateSpeed

    def _moveRobot(self, runTime):
    	"""Helper method, takes in a time in seconds, or time is None if no time limit,
    	and it runs the motors at the current speed either forever or for the given time.
    	Blocks and waits if a time is given."""
    	if runTime is None:
        		self.leftMotor.run_forever()
        		self.rightMotor.run_forever()
    	else:
        		milliSecTime = runTime * 1000.0
        		self.leftMotor.run_timed(time_sp = milliSecTime)
        		self.rightMotor.run_timed(time_sp = milliSecTime)
        		self.rightMotor.wait_until_not_moving()


    def pointerRight(self,speed=None, time=None):
        if speed != None:
            self.servoMotor.speed_sp = self.servoMotor.max_speed * speed
        else:
            self.servoMotor.speed_sp = self.servoMotor.max_speed
        if time != None:
            self.servoMotor.run_timed(time_sp = time)
            self.servoMotor.wait_until_not_moving()
        else:
            self.servoMotor.run_forever()

    def pointerLeft(self,speed=None, time=None):
        if speed != None:
            self.servoMotor.speed_sp = -self.servoMotor.max_speed * speed
        else:
            self.servoMotor.speed_sp = -self.servoMotor.max_speed
        if time != None:
            self.servoMotor.run_timed(time_sp = time)
            self.servoMotor.wait_until_not_moving()
        else:
            self.servoMotor.run_forever()

    def pointerTo(self,angle):
        """self.servoMotor.position_sp = DEFAULT_POINTER_POS + angle
        self.servoMotor.run_to_abs_pos()
        self.servoMotor.wait_until_not_moving()
        self.servoMotor.stop_action = 'brake'"""
        self.servoMotor.position_sp=angle
        self.servoMotor.run_to_abs_pos()
         
# Sample of how to use this
if __name__ == "__main__":
    firstConfig = {SturdyBot.LEFT_MOTOR: 'outc',
                   SturdyBot.RIGHT_MOTOR: 'outb',
                   SturdyBot.SERVO_MOTOR: 'outd',
                   SturdyBot.LEFT_TOUCH: 'in1',
                   SturdyBot.RIGHT_TOUCH: 'in2'}



