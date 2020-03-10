#!/usr/bin/python3

from ev3dev.ev3 import Leds
from time import sleep
import SturdyBot #TODO: rename to DogBot or something that makes more sense
import _thread #separate thread listens for commands so main can do its thing
import socket #get voice commands from app
from os import system #to make the text size bigger
import Conditioning #our conditioning class
import PotentialFieldBrain #really good at obstacle avoidance
from random import randint

dog=SturdyBot.SturdyBot("Ytterboe") #neverforget
fields=PotentialFieldBrain.PotentialFieldBrain(dog)
brain=Conditioning.Conditioning()


#TODO: move all commands into SturdyBot?
def playDead():
    dog.stop("coast")
    brain.writeCommands() #write commands to a text file to remember for next time
    exit()

def stay():
    print("staying")
    dog.stop()
    sleep(5)

def wander():
    print("wandering/ignoring")

def rollover():
    print("rolling")
    startAngle=dog.readHeading()
    dog.turnRight(.5)
    turnedEnough=False
    while True:
        current=dog.readHeading()
        print(current)
        if current<startAngle:
            turnedEnough=True
        elif turnedEnough: #passed 0 at some point and current>=angle
            break
        else:
            x=2 #doesn't work without an "else" statment (?)
    dog.stop("coast")

def come():
    print("coming")
    dog.pointerTo(45)
    turning=False
    #TODO: turn ultrasonic to front, then just measure distance
    while(True):
        x,y,w,h=dog.findSignature(2)
        if x>400: #off-camera
            dog.turnLeft(.3) #can turn faster, person will probably move a little to be infront
            turning=True
        else:
            #print(w,"x",h)
            if turning: #take one camera frame to stop momentum
                dog.stop("hold")
                turning=False
            if dog.readDistance()<10: #right in front of the camera
                break
            midX=x+(w/2)
            offset=(316/2)-midX #resolution is 316x208, middle of screen-midX
            dog.leftMotor.speed_sp=min(max(300+offset,-300),dog.leftMotor.max_speed*.9)
            dog.rightMotor.speed_sp=min(max(300-offset,-300),dog.rightMotor.max_speed*.9)
            dog.leftMotor.run_forever()
            dog.rightMotor.run_forever()
    dog.stop("coast")
    
def fetch():
    print("fetching")
    turning=False
    while(True):
        x,y,w,h=dog.findSignature(1)
        if x>400: #off-camera
            dog.turnLeft(.2)
            turning=True
        else:
            #print(w,"x",h)
            if turning: #take one camera frame to stop momentum
                dog.stop("hold")
                turning=False
            if h>150: #right in front of the camera
                break
            midX=x+(w/2)
            offset=(316/2)-midX #resolution is 316x208, middle of screen-midX
            offset*=2
            dog.leftMotor.speed_sp=min(max(750+offset,-200),dog.leftMotor.max_speed*.99)
            dog.rightMotor.speed_sp=min(max(750-offset,-200),dog.rightMotor.max_speed*.99)
            dog.leftMotor.run_forever()
            dog.rightMotor.run_forever()
    dog.stop("coast")

command=""
commandDict={'playdead':playDead,
             'stay':stay,
             'wander':wander,
             'rollover':rollover,
             'come':come,
             'fetch':fetch
            }


usProgress=0
def obstacleForce():
  global usProgress
  global dog
  #dog.servoMotor.wait_until_not_moving() #still buggy for some reason
  sleep(.2)
  dist=dog.readDistance()
  if(usProgress==0):
    angle=315
    dog.pointerTo(-45)
    usProgress=1
  elif(usProgress==1):
    angle=0
    dog.pointerTo(0)
    usProgress=2
  elif(usProgress==2):
    angle=45
    dog.pointerTo(45)
    usProgress=0
  else: #weird things happened
    usProgress=0
    return (0,0)
  #magnitude of the vector it gives off: https://www.desmos.com/calculator/qcciv0mbux
  magnitude=(10000/dist)-175
  #print(magnitude," at angle ",angle)
  return(magnitude*(-.1),angle) #go backwards and reduce how strong the force is
  #return(0,0)

def moveForward():
    angle=(315+randint(0,90))%360
    return(30,angle)


#rus on another thread - sets up a socket server and waits for input from the app
def getInput():
    global command
    system('setfont Lat15-TerminusBold14') #so it can be run without SSH, displays on the lil screen - TODO: don't print anything else out?

    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #gross way to get ip of wifi interface
    s.connect(("8.8.8.8",80))
    ip=s.getsockname()[0]
    #TODO: disconnect dummy socket?
    s=socket.socket()
    port=50000 #maybe try this and change it until something works? probably not necessary
    s.bind(('',port))
    s.listen(5)

    while True: #accept incoming connections
        print("listening on:\n",ip)
        Leds.set_color(Leds.LEFT,Leds.RED)
        Leds.set_color(Leds.RIGHT,Leds.RED)
        c,addr=s.accept() #wait for connection
        print("CONNECTED")
        Leds.set_color(Leds.LEFT,Leds.GREEN)
        Leds.set_color(Leds.RIGHT,Leds.GREEN)
        while True: #handle commands from that connection
            command=str(c.recv(1024)[:-1],"utf-8") #chop off newline and convert to utf-8
            if(command=="disconnect" or command=="playdead" or command==""):
                c.close()
                print("disconnecting")
                break
            _thread.interrupt_main() #sends a KeyboardInterrupt for some reason
            #wait for the main thread to handle exception, then reset
            #proper IPC would be to have main communicate that it was received somehow, but we don't really lose anything from having the voice command thread wait for just a second
            sleep(1)
            command=""
        #got here from disconnect/playdead/(blank)
        if(command=="playdead"):
            print("exiting...")
            s.close()
            #let main know something's up
            _thread.interrupt_main()
            break
    #(thread exits at the end of this function)

def executeCommand(cmd):
    if cmd in commandDict:
        inputted=commandDict[cmd]
        inputted()
    else:
        print("ERROR: Conditioning returned a string that doesn't have a matching function")

def run():
    global command
    _thread.start_new_thread(getInput,())

    brain.readCommands() #read in commands from text file from last time

    #set things up for the wander behavior
    dog.servoMotor.stop_action='brake'
    dog.servoMotor.speed_sp=dog.servoMotor.max_speed/2
    fields.add(obstacleForce)
    fields.add(obstacleForce)
    fields.add(obstacleForce)
    fields.add(moveForward)

    while(True): #continuously check if command, then wander until interrupt
        try: 
            if command!="": #TODO: check if playdead while the last command was executing, or the app will disconnect while the dog just keeps going...
                if command=="goodboy":
                    brain.giveFeedback(1)
                    command=""
                elif command=="baddog":
                    brain.giveFeedback(0)
                else:
                    print("GOT COMMAND: ",command)
                    #what the dog heard, uses the Conditioning class
                    interpreted=brain.takeCommand(command)
                    #if the ball is within sight
                    if dog.findSignature(1)[0]<400:
                        print("BALL!")
                        for i in range(0,2): #roll for "fetch" thrice
                            interpreted=brain.takeCommand(command)
                            if interpreted=="fetch":
                                break
                    executeCommand(interpreted)
                command="" #back to normal after the command is executed
            while(True):
                if dog.button.any():
                    playDead()
                    break
                if randint(0,25)==0:
                    dog.bork()
                fields.step()
        except KeyboardInterrupt:
            #other thread interrupted it, continue outer while loop
            continue

#do the thing !
run()
