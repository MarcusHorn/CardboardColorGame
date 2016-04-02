import math
class Circle(object):
    def __init__(self, boardRadius, circleRadius, angle):
        radianAngle = angle * (math.pi/180) #Used for math.cos and math.sin
        self.x = (boardRadius + boardRadius*math.cos(radianAngle)) // 1
        self.y = (boardRadius + boardRadius*math.sin(radianAngle)) // 1
        self.r = circleRadius - (circleRadius*math.sin(radianAngle)) // 2
        
    def updateCircle(self, dAngle):
        self.angle += dAngle
        self.angle %= 360
        radianAngle = angle * (math.pi/180) #Used for math.cos and math.sin
        self.x = (boardRadius + boardRadius*math.cos(radianAngle)) // 1
        self.y = (boardRadius + boardRadius*math.sin(radianAngle)) // 1
        
        
    def getCoords(self):
        return self.x, self.y
        
    
