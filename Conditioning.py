import random
import time
import queue
import math

class Conditioning:
    tricks=["wander","stay","rollover","come","fetch"] #constant
    commands={}
    default_probs=[.5,.2,.15,.10,.05] #constant, when a new command is taken it starts out as this
    gCONST=.2 #determines how fast it learns
    growth=gCONST #changes with time

    lastCommand=None #string of last command given
    lastActeion=0 #index of last trick performed
    
    lastTime=None
    tricksInSuccession=[]
    timeWindow=30

    #read in initial command probability lists from dogbrain.txt
    def readCommands(self):
        readFile=""
        try:
            readFile=open("dogbrain.txt","r")
        except FileNotFoundError:
            #should be their first time in the program, don't bother reading
            print("Welcome!")
            return
        #TODO
        numCommands=int(readFile.readline())
        timePassed=time.time()-float(readFile.readline())
        
        for i in range(numCommands):
            commandName=readFile.readline().rstrip()
            commandList=[]
            for i in range(len(self.tricks)):
                commandList.append(float(readFile.readline()))
            self.commands[commandName]=commandList
            print(commandList)
        self.deteriorateBrain(timePassed)
        readFile.close()

    #save current command states to dogbrain.txt
    def writeCommands(self):
        writeFile=open("dogbrain.txt","w")
        numCommands=len(self.commands)
        writeFile.write(str(numCommands))
        writeFile.write("\n")
        writeFile.write(str(time.time()))
        writeFile.write("\n")
        for key in self.commands:
            writeFile.write(key)
            writeFile.write("\n")
            for i in range(len(self.tricks)):
                writeFile.write(str(self.commands[key][i]))
                writeFile.write("\n")
        pass

    #take commands from last time, but bring any tricks that are above the default down, and wander() up in their place
    def deteriorateBrain(self,timePassed):
        #at 90% or above, it won't deteriorate
        h=min(100,timePassed/3600)
        for key in self.commands:
            for i in range(1,len(self.tricks)):
                p=self.commands[key][i]
                if p<.9 and p>self.default_probs[i]:
                    self.commands[key][i]=max(self.default_probs[i],p*(1-h/100)) #back to default after 100 hours
            sum=0
            for i in range(1,len(self.tricks)):
                sum+=self.commands[key][i]
            self.commands[key][0]=1-sum

    def _updateSize(self,q,currTime):
        while len(q)>0 and q[0]<(currTime-self.timeWindow):
            print("popped ",q.pop(0))

    #input command, returns a string: one of the tricks
    def takeCommand(self,str):
        if(str=="playdead"):
          return "playdead" #playdead always works
        if str in self.commands:
            ret=self.runCommand(self.commands[str])
        else:
            self.commands[str]=self.default_probs.copy()
            ret=self.runCommand(self.commands[str])
        self.lastCommand=str
        self.lastAction=ret

        currTime=time.time()
        if self.lastTime!=None:
            t=currTime-self.lastTime
            self._updateSize(self.tricksInSuccession,currTime)
            x=len(self.tricksInSuccession)
            self.growth=self.gCONST*(1/((x/2)+1))*math.exp(-1/t)
        print("Growth is ",self.growth)
        self.lastTime=currTime
        self.tricksInSuccession.append(currTime)
        
        return self.tricks[ret]

    #helper function, randomly selects an index in probList
    def runCommand(self,probList):
        num=random.random()
        for i in range(len(probList)):
            if num < probList[i]:
                return i
            else:
                num-=probList[i]
        print("runCommand is acting up...?")
        return 0

    def giveFeedback(self,good):
        if self.lastCommand is None:
            return
        cmdList=self.commands[self.lastCommand]
        if good:
            cmdList[self.lastAction]+=self.growth*(1-cmdList[self.lastAction])
            for i in range(len(cmdList)):
                if i==self.lastAction:
                    continue
                cmdList[i]-=self.growth*cmdList[i]
        else:
            for i in range(len(cmdList)):
                if i==self.lastAction:
                    continue
                cmdList[i]+=self.growth*(cmdList[self.lastAction])*(cmdList[i]/(1-cmdList[self.lastAction]))
            cmdList[self.lastAction]-=self.growth*(cmdList[self.lastAction])
        print("Probabilities for ",self.lastCommand,": ",cmdList)
        self.lastCommand=None

"""test=Conditioning()
print("start")
while(True):
    cmd=input()
    print(test.takeCommand(cmd))
    total=0
    for i in range(len(test.commands[cmd])):
        total+=test.commands[cmd][i]
    print(total)
    feedback=int(input())
    test.giveFeedback(feedback)
"""
