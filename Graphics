from tkinter import *
import math
import random
from random import *

# circle class
class Circle(object):
    def __init__(self, angle, color, data):
        self.angle = angle
        self.x = int(data.centerBoardx + data.boardRadius * math.cos(self.angle))
        self.y = int(data.centerBoardy + data.boardRadius * math.sin(self.angle))
        self.r = data.circleRadius
        self.color = color
       
    def rotate(self, data):
        self.angle += data.deltaAngle
        self.angle %= math.pi * 2
        self.x = int(data.centerBoardx + data.boardRadius * math.cos(self.angle))
        self.y = int(data.centerBoardy + data.boardRadius * math.sin(self.angle))
        self.r = data.circleRadius
        
    def validClickInsideCircle(self, x, y):
        return ((x-self.x)**2 + (y-self.y)**2)**.5 <= self.r

    def isOverlapping(self, other, data):
        distance = (((other.x-self.x)**2 + (other.y-self.y)**2)**.5)
        return distance <= 2 * data.circleRadius

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
    data.numberOfCircles = 8
    data.level = 0
    data.divisor = 3
    data.circleRadius = int(getCircleRadius(data))
    data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
    data.targetRadius = data.width//10
    data.deltaAngle = 0.1
    data.winDelay = 1000
    init_1(data)

# put it in the run function
def init_1(data):
    data.circleList = []
    data.step = 0
    data.wonLevel = False
    data.winningCircle = None
    data.timeElapsed = 0 #Used for transition between levels
    generateCircles(data)
    

def getCircleRadius(data):
    circumferenceBoard = 2 * math.pi * data.width
    orbit = circumferenceBoard//data.numberOfCircles
    return orbit//(math.pi*2)//data.divisor

def generateCircles(data):
    angle = (math.pi * 2)/data.numberOfCircles
    print(angle)
    print(data.numberOfCircles)
    for index in range(data.numberOfCircles):
        (r, g, b) = (randint(0,255), randint(0,255), randint(0,255))
        color = rgbString(r, g, b)
        data.circleList.append(Circle(angle*index, color, data))
    if data.circleList[0].isOverlapping(data.circleList[1], data):
        data.divisor += 1
        getCircleRadius(data)
    targetIndex = randint(0, data.numberOfCircles - 1)
    targetColor = data.circleList[targetIndex].color
    data.targetCircle = targetCircle(targetColor, data)


# from notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def mousePressed(event, data):
    x, y = event.x, event.y
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        if circle.validClickInsideCircle(x, y) and circle==data.targetCircle:
            data.wonLevel = True
            data.winningCircle = circle

def difficulty(data):
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
    if data.wonLevel:
        data.timeElapsed += data.timerDelay
        if data.timeElapsed % data.winDelay != 0:
            return
        data.timeElapsed = 0
        data.wonLevel = False
        data.level += 1
        difficulty(data)
        init_1(data)
        print("Yay")
    data.step += 1
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        circle.rotate(data)

def redrawAll(canvas, data):
    # draw in canvas
    data.targetCircle.draw(canvas, data)
    drawSurroundingCircles(canvas, data)
    if data.wonLevel == True:
        drawWinAnimation(canvas, data)

def drawSurroundingCircles(canvas, data):
    for circle in range(len(data.circleList)):
        data.circleList[circle].draw(canvas, data)

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
    data.timerDelay = 100 # milliseconds
    
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
