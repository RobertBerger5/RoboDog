#!/usr/bin/python3

import ev3dev.ev3 as ev3
import ev3dev.fonts as fonts
import time
import random
import SturdyBot
import threading #separate thread listens for commands so main can do its thing
import socket #get voice commands from app
import os #to make the text size bigger
import Conditioning #our conditioning class

#TODO: don't wander if the app isn't connected, kinda stressful to enter the IP as fast as possible
#(good boy just wants attention, doesn't act up if no one's watching)

dog=SturdyBot.SturdyBot("greg the dog")

def playDead():
    dog.leftMotor.stop()
    dog.rightMotor.stop()
    exit()

def stay():
    dog.leftMotor.stop()
    dog.rightMotor.stop()
    time.sleep(5)

def wander():
    print("wandering")
def rollover():
    print("rolling")
def come():
    print("coming")
def fetch():
    print("fetching")


command=""
commandDict={'playdead':playDead,
             'stay':stay,
             'wander':wander,
             'rollover':rollover,
             'come':come,
             'fetch':fetch
            }

def getInput():
    global command
    os.system('setfont Lat15-TerminusBold14')

    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #gross way to get ip of wifi interface
    s.connect(("8.8.8.8",80))
    ip=s.getsockname()[0]
    #TODO: disconnect?
    s=socket.socket()
    port=50000 #maybe try this and change it until something works? probably not necessary
    s.bind(('',port))
    s.listen(5)

    while True:
        print("listening on:\n",ip)
        ev3.Leds.set_color(ev3.Leds.LEFT,ev3.Leds.RED)
        ev3.Leds.set_color(ev3.Leds.RIGHT,ev3.Leds.RED)
        c,addr=s.accept() #wait for connection
        print("CONNECTED")
        ev3.Leds.set_color(ev3.Leds.LEFT,ev3.Leds.GREEN)
        ev3.Leds.set_color(ev3.Leds.RIGHT,ev3.Leds.GREEN)
        while True:
            command=str(c.recv(1024)[:-1],"utf-8") #chop off newline and convert to utf-8
            if(command=="disconnect" or command=="playdead" or command==""):
                c.close()
                print("disconnecting")
                break
            #wait for main thread to find it, then reset
            time.sleep(1)
            command=""
        if(command=="playdead"):
            print("exiting...")
            s.close()
            break
        #command=input("type things")
        #if(command=="playdead"):
        #  break
        #time.sleep(1) #hope that the main thread catches it in the window of time where it actually has something...
        #command=""
    #thread exits

def executeCommand(cmd):
    if cmd in commandDict:
        inputted=commandDict[cmd]
        inputted()

def run():
    global command
    threading.Thread(target=getInput).start()
    while(True):
        leftSpeed=random.random() #TODO: change distribution
        rightSpeed=random.random()
        wanderTime=random.random()*3+.5
        dog.curve(leftSpeed,rightSpeed)
        startTime=time.time()
        elapsedTime=0
        while elapsedTime<wanderTime:
            if command!="": #TODO: check if playdead while the last command was executing
                print("GOT COMMAND: ",command)
                interpreted=brain.takeCommand(command) #what the dog heard, uses the Conditioning class
                executeCommand(interpreted)
                #TODO: wait for feedback immediately? or keep wandering?
                print("waiting for command to be goodboy or baddog")
                while(command!="goodboy" and command!="baddog"):
                    x=3 #TODO: idk if I can just leave it blank, python whitespace as syntax scares me.
                #assert: command should either be "goodboy" or "baddog" right here, right? unless they have some wild fast timing...
                if(command=="goodboy"):
                    brain.giveFeedback(1)
                else:
                    brain.giveFeedback(0)
                #print(brain.commands[interpreted])
                command="" #back to normal after the command is executed
                break
            elapsedTime=time.time()-startTime

brain=Conditioning.Conditioning()
run()
