from tkinter import *
import math
import random
from random import *

# circle class
class Circle(object):
    def __init__(self, angle, color, data):
        self.angle = angle
        self.rotateR = data.boardRadius #Rotation radius
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
    data.numberOfCircles = 3
    data.colorOffset = max(18 - data.numberOfCircles, 5)
    data.level = 1
    data.score = 0
    data.targetRadius = data.width//10
    data.deltaAngle = 0.1
    data.animDelay = 500
    data.winDelay = 500
    data.circleRadius = getCircleRadius(data)
    init_1(data)
    initTitle(data)

def initTitle(data):
    data.tr_height = data.height/6
    data.tr_width = data.width
    data.gameName =  "C O L O R  C L I C K E R"
    fontName = "Verdana"
    fontSize = 30
    fontStyle = "bold"
    data.tr_fontColor = rgbString((50, 50, 50)) #dark gray
    data.tr_offsetFontColor = rgbString((191, 191, 191))
    data.tr_offsetX = 2
    data.tr_offsetY = 2
    data.tr_font = "%s %d %s" % (fontName, fontSize, fontStyle)

def rgbString(rgb):
    red, green, blue = rgb
    return "#%02x%02x%02x" % (red, green, blue)

# put it in the run function
def init_1(data):
    data.circleList = []
    data.step = 0
    data.clearedCircle = False
    data.winningCircle = None
    data.wonLevel = False
    data.timeElapsed = 0 #Used for transition between levels
    data.circleRadius = getCircleRadius(data)
    data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
    data.winTimeElapsed = 0
    generateCircles(data)
    
def getCircleRadius(data):
    if data.numberOfCircles < 9:
        radiusReference = 12 #Reference number for standard board
    else:
        radiusReference = data.numberOfCircles + 4
    circumferenceBoard = 2 * math.pi * data.width
    orbit = circumferenceBoard//(radiusReference / 4)
    return orbit//(math.pi*2)//4

def generateCircles(data):
    angle = (math.pi * 2)/data.numberOfCircles
    for index in range(data.numberOfCircles):
        colorOffset = data.colorOffset
        maxInt = 255//colorOffset
        (r, g, b) = (randint(0,maxInt), randint(0,maxInt), randint(0,maxInt))
        r *= colorOffset
        g *= colorOffset
        b *= colorOffset
        color = rgbString((r, g, b))
        data.circleList.append(Circle(angle*index, color, data))
    if isOverlapping(angle, data):
        data.circleRadius = getCircleRadius(data)
    targetIndex = randint(0, data.numberOfCircles - 1)
    targetColor = data.circleList[targetIndex].color
    data.targetCircle = targetCircle(targetColor, data)

def isOverlapping(angle, data):
    distance = 2 * data.circleRadius**2 * (1 + math.cos(angle))
    return distance < 2 * data.circleRadius

def mousePressed(event, data):
    x, y = event.x, event.y
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        if circle.validClickInsideCircle(x, y) and circle==data.targetCircle:
            data.clearedCircle = True
            data.winningCircle = circle
            data.circleList.remove(data.winningCircle)
            newNumberOfCircles = len(data.circleList)
            if newNumberOfCircles == 0:
                data.wonLevel = True
            else:
                targetIndex = randint(0, len(data.circleList) - 1)
                targetColor = data.circleList[targetIndex].color
                data.targetCircle.color = targetColor
                data.timeElapsed += data.timerDelay
            return

def difficulty(data):
    if not isOverlapping(data.deltaAngle, data):        
        if data.level % 2 == 0:
            data.numberOfCircles += 1
            if data.colorOffset > 5:
                data.colorOffset -= 1
    if data.level % 10 == 0:
        if data.deltaAngle < 0:
            data.deltaAngle -= 0.05
        else:
            data.deltaAngle += 0.05
    if data.level % 5 == 0:
        data.deltaAngle *= -1


def keyPressed(event, data):
    pass


def timerFired(data):
    data.step += 1
    for index in range(len(data.circleList)):
        circle = data.circleList[index]
        circle.rotate(data)
    if data.clearedCircle:
        data.timeElapsed += data.timerDelay
        if data.timeElapsed % data.animDelay != 0:
            data.winningCircle.rotateR += data.timerDelay
            data.winningCircle.updateCoords(data)
            return
        data.timeElapsed = 0
        data.clearedCircle = False
        data.winningCircle = None
    elif data.wonLevel:
        data.winTimeElapsed += data.timerDelay
        if data.winTimeElapsed % data.winDelay != 0:
            return
        else:
            data.level += 1
            difficulty(data)
            init_1(data)

def redrawAll(canvas, data):
    # draw in canvas
    drawSurroundingCircles(canvas, data)
    data.targetCircle.draw(canvas, data)
    drawTitle(canvas, data)
    drawLevel(canvas, data)

def drawSurroundingCircles(canvas, data):
    if data.clearedCircle:
        data.winningCircle.draw(canvas, data)
    for circle in range(len(data.circleList)):
        data.circleList[circle].draw(canvas, data)
    for circle in range(len(data.circleList)):
        if data.clearedCircle and data.circleList[circle] is data.winningCircle:
            continue
        else: data.circleList[circle].drawLine(canvas, data)

def drawTitle(canvas,data):
    canvas.create_text(data.width//2-data.tr_offsetX,50+data.tr_offsetY,text=data.gameName, 
        fill=data.tr_offsetFontColor, font=data.tr_font)
    canvas.create_text(data.width//2,50,text=data.gameName, 
        fill=data.tr_fontColor, font=data.tr_font)

def drawLevel(canvas,data):
    font = "Verdana 20"
    canvas.create_text(data.width//2,100,text="Level %d" % data.level, 
        fill=data.tr_fontColor, font=font)


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
run()
