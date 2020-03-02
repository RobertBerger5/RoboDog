# A Potential Field control system

import SturdyBot
import math
import time

#-------------------------------------------
# 

class PotentialFieldBrain:
    """ This class represents a brain for a potential field reactive system.
    This continues to use the concept of a behavior, but potential field
    behaviors each produce a vector describing the force they compute on the
    robot. The brain does vector addition to combine those vectors, and then
    transforms the resulting force on the robot into a movement direction and
    speed"""


    #----------------------------------------
    #Initialization and destruction routines
    
    def __init__(self, robot, maxMagnitude = 100.0):
        """Initializes the brain with the robot it controls. Also takes
        an optional input to define the maximum magnitude of any vector."""

        self.robot = robot
        # set maximum possible magnitude
        self.maxMagnitude = maxMagnitude
        self.behaviors = []


    def add(self, behavior):
        """Takes a behavior object as input, and initializes it, and
        adds it to the list"""
        self.behaviors.append( behavior )


    def run(self, numSteps):
        """Takes in a number of steps, and runs the that many cycles"""
        for i in range(numSteps):
            self.step()
        self.robot.stop()

    def stopAll(self):
        """Stops the robot from moving, and could shut down anything else that was requried"""
        self.robot.stop()

    # 
    def step(self):
        """one step means figuring out the vectors for each of the behaviors, and performing
        vector addition to combine them.  Then the resulting vector is the action taken."""
        vectors = self._updateBehaviors()
        (magnitude, angle) = self._vectorAdd(vectors)

        transValue = self._scaleMagnitude(magnitude)
        # if the angle is forward-heading, translate forward, else backward
        # there is probably a more clever way to do this...

        # Convert angle so that runs from 0 to 180 counterclockwise, and from 0 to -180 clockwise
        if angle > 180:
            angle = -(360 - angle)

        # If angle is backward-looking, set negative translation speed
        if abs(angle) > 90:
            transValue = - transValue
            
        #print("type something when ready...")
        #dummy=input()
        if transValue == 0.0:
            # don't rotate if you aren't moving at all
            scaledSpeed = 0.0
        else:
            # scale rotation speed by size of angle we want
            scaledSpeed = angle / 180.0
        
        scaledSpeed = self._scaledRotation(scaledSpeed)
        self.robot.move(transValue, scaledSpeed)
        
        

    def _scaleMagnitude(self, magnitude):
        """Takes in a magnitude and scales it as a percentage of
        the maximum magnitude, so that it is between 0.0 and 1.0."""
        if magnitude > self.maxMagnitude:
            magnitude = self.maxMagnitude
        return magnitude / self.maxMagnitude
 
    def _scaledRotation(self, rotSpeed):
        """Takes in a rotation speed and scales it so that
        it is further from  zero than 0.2."""
        if rotSpeed > 0:
            # if scaled speed is too low, set to 0.2
            rotSpeed = max(0.2, rotSpeed)
        elif rotSpeed < 0:
          # if scaled speed is too low, set to 0.2
            rotSpeed = min(-0.2, rotSpeed)
        return rotSpeed
    
    
    def _updateBehaviors(self):
        """Run through all behaviors, and ask them to calculate the force
        they detect. Return the forces as a list. Note: forces are given as a
        tuple containing magnitude and direction"""
        vectors = []
        for behav in self.behaviors:
            vec = behav()
            vectors.append(vec)
        return vectors


    def _vectorAdd(self, vectors):
        """takes in a list of vectors and produces the final vector.  Notice
        that, for simplicity, the behaviors return a magnitude/angle description
        of a vector, but that having the vector described as an x and y offset is
        much easier, so first the values are converted, and then added."""
        xSum = 0
        ySum = 0
        for vec in vectors:
            (mag, angle) = vec
            radAngle = math.radians(angle)
            xVal = math.cos(radAngle) * mag
            yVal = math.sin(radAngle) * mag
            xSum += xVal
            ySum += yVal
        totalMag = math.hypot(xSum, ySum)
        totalAngle = math.atan2(ySum, xSum)
        degAngle = math.degrees(totalAngle)
        while degAngle < 0:
            degAngle += 360
        while degAngle > 360:
            degAngle -= 360
        return (totalMag, degAngle)
