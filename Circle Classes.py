import math
class Circle(object):
    def __init__(self, boardRadius, circleRadius, angle, color):
        radianAngle = angle * (math.pi/180) #Used for math.cos and math.sin
        self.x = (boardRadius + boardRadius*math.cos(radianAngle)) // 1
        self.y = (boardRadius + boardRadius*math.sin(radianAngle)) // 1
        self.r = circleRadius - (circleRadius*math.sin(radianAngle)) // 2
        self.color = color
        self.connected = False
        
    def updateCircle(self, dAngle):
        self.angle += dAngle
        self.angle %= 360
        radianAngle = angle * (math.pi/180) #Used for math.cos and math.sin
        self.x = (boardRadius + boardRadius*math.cos(radianAngle)) // 1
        self.y = (boardRadius + boardRadius*math.sin(radianAngle)) // 1
        self.r = circleRadius - (circleRadius*math.sin(radianAngle)) // 2
        
    def getCoords(self):
        return self.x, self.y
        
    def getColor(self):
        return self.color
        
    def getRadius(self):
        return self.r
    
    def validClickInsideCircle(self, x, y):
        return ((x-self.x)**2 + (y-self.y)**2)**.5 <= self.r
        
    def __eq__(self, other):
        return self.color == other.color
        
    def connect(self):
        self.connected = True
        
class Board(object):
    def __init__(self, cx, cy, boardRadius, boardColor):
        self.color = boardColor
        self.x = cx
        self.y = cy
        self.r = boardRadius
