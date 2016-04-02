from tkinter import *
import math
import random
from random import *

# circle class
class Circle(object):
    def __init__(self, angle, color, data):
        self.angle = angle
        self.rotateR = data.boardRadius
        self.x = int(data.centerBoardx + self.rotateR * math.cos(self.angle))
        self.y = int(data.centerBoardy + self.rotateR * math.sin(self.angle))
        self.r = data.circleRadius
        self.color = color
        self.centreX = data.centerBoardx
        self.centreY = data.centerBoardy

    def updateCoords(self, data):
        self.x = int(data.centerBoardx + self.rotateR * math.cos(self.angle))
        self.y = int(data.centerBoardy + self.rotateR * math.sin(self.angle))

    def drawLine(self, canvas, data):
        canvas.create_line(self.x, self.y, self.centreX, self.centreY,
                                              fill = self.color, width = 5)
       
    def rotate(self, data):
        self.angle += data.deltaAngle
        self.angle %= math.pi * 2
        self.x = int(data.centerBoardx + data.boardRadius * math.cos(self.angle))
        self.y = int(data.centerBoardy + data.boardRadius * math.sin(self.angle))
        self.r = data.circleRadius
        
    def validClickInsideCircle(self, x, y):
        return ((x-self.x)**2 + (y-self.y)**2)**.5 <= self.r

    def isOverlapping(self, other, data):
        sectorAngle = other.angle - self.angle
        distance = 2 * data.circleRadius**2 * (1 + math.cos(sectorAngle))
        #distance = (((other.x-self.x)**2 + (other.y-self.y)**2)**.5)
        return distance < 2 * data.circleRadius

    def __eq__(self, other):
        return self.color == other.color
        
    def draw(self, canvas, data):
        (top, left) = (self.x - self.r, self.y - self.r)
        (bottom, right) = (self.x + self.r, self.y + self.r)
        canvas.create_oval(top, left, bottom, right, fill=self.color)

class targetCircle(Circle):
    def __init__(self, color, data):
        self.x = data.centerBoardx
        self.y = data.centerBoardy
        self.r = data.targetRadius
        self.color = color


# game data
def init(data):
    data.centerBoardx = data.width//2
    data.centerBoardy = (1/10) * data.height + data.centerBoardx
    data.numberOfCircles = 10
    data.level = 0
    data.test = 10
    data.targetRadius = data.width//10
    data.deltaAngle = 0.1
    data.winDelay = 1700
    data.circleRadius = getCircleRadius(data)
    init_1(data)

# put it in the run function
def init_1(data):
    data.circleList = []
    data.step = 0
    data.clearedCircle = False
    data.winningCircle = None
    data.wonLevel = False
    data.timeElapsed = 0 #Used for transition between levels
    data.circleRadius = getCircleRadius(data)
    print(data.circleRadius)
    data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
    generateCircles(data)
    
def getCircleRadius(data):
    if data.numberOfCircles <= 10:
        numberOfCircles = 9 #Reference number for standard board
        print(numberOfCircles)
    else:
        numberOfCircles = data.numberOfCircles
    circumferenceBoard = 2 * math.pi * data.width
    orbit = circumferenceBoard//(numberOfCircles // 3)
    return orbit//(math.pi*2)//4

def generateCircles(data):
    angle = (math.pi * 2)/data.numberOfCircles
    for index in range(data.numberOfCircles):
        (r, g, b) = (randint(0,51), randint(0,51), randint(0,51))
        r *= 5
        g *= 5
        b *= 5
        color = rgbString(r, g, b)
        data.circleList.append(Circle(angle*index, color, data))
    if isOverlapping(angle, data):
        print("stop")
        data.circleRadius = getCircleRadius(data)
    targetIndex = randint(0, data.numberOfCircles - 1)
    targetColor = data.circleList[targetIndex].color
    data.targetCircle = targetCircle(targetColor, data)

def isOverlapping(angle, data):
    distance = 2 * data.circleRadius**2 * (1 + math.cos(angle))
    return distance < 2 * data.circleRadius

# from notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def mousePressed(event, data):
    x, y = event.x, event.y
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        if circle.validClickInsideCircle(x, y) and circle==data.targetCircle:
            data.clearedCircle = True
            data.winningCircle = circle

def difficulty(data):
    if not isOverlapping(data.deltaAngle, data):        
        if data.level % 2 == 0:
            data.numberOfCircles += 1
    if data.level % 10 == 0:
        if data.deltaAngle < 0:
            data.deltaAngle -= 0.05
        else:
            data.deltaAngle += 0.05
    if data.level % 5 == 0:
        data.deltaAngle *= -1


def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    data.step += 1
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        circle.rotate(data)
    if data.clearedCircle:
        data.timeElapsed += data.timerDelay
        if data.timeElapsed % data.winDelay != 0:
            data.winningCircle.rotateR += data.timerDelay
            data.winningCircle.updateCoords(data)
            return
        data.timeElapsed = 0
        data.clearedCircle = False
        data.circleList.remove(data.winningCircle)
        data.winningCircle = None
        newNumberOfCircles = len(data.circleList)
        if newNumberOfCircles == 0:
            data.level += 1
            difficulty(data)
            init_1(data)
        else:
            targetIndex = randint(0, len(data.circleList) - 1)
            targetColor = data.circleList[targetIndex].color
            data.targetCircle.color = targetColor
            data.timeElapsed += data.timerDelay

def redrawAll(canvas, data):
    # draw in canvas
    data.targetCircle.draw(canvas, data)
    drawSurroundingCircles(canvas, data)


def drawSurroundingCircles(canvas, data):
    for circle in range(len(data.circleList)):
        data.circleList[circle].draw(canvas, data)
    for circle in range(len(data.circleList)):
        if data.clearedCircle and data.circleList[circle] is data.winningCircle:
            continue
        else: data.circleList[circle].drawLine(canvas, data)


####################################
# use the run function as-is
####################################

def run():
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.timerDelay = 50 # milliseconds
    
    # create the root and the canvas
    root = Tk()
    data.height = (14/16)* root.winfo_screenheight()
    data.width = (4/5) * root.winfo_screenheight()
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
run()
