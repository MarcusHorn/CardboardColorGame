#Scoket Lecture

import socket
from _thread import *
from queue import Queue
import time, math
from random import randint

HOST = "25.130.151.205"
PORT = 8081
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(BACKLOG)

maxPlayers = 5
minPlayers = 1
playerData = dict()
playerCount = 0

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
        sectorAngle = other.angle - self.angle
        distance = 2 * data.circleRadius**2 * (1 + math.cos(sectorAngle))
        #distance = (((other.x-self.x)**2 + (other.y-self.y)**2)**.5)
        return distance < 2 * data.circleRadius
        
class targetCircle(Circle):
    def __init__(self, color, data):
        self.x = data.centerBoardx
        self.y = data.centerBoardy
        self.r = data.targetRadius
        self.color = color

def init(data):
    data.height = (14/16)* 1920
    data.width = (4/5) * 1080
    data.centerBoardx = data.width//2
    data.centerBoardy = (1/10) * data.height + data.centerBoardx
    data.numberOfCircles = 3
    data.level = 0
    data.divisor = 3
    data.circleRadius = int(getCircleRadius(data))
    data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
    data.targetRadius = data.width//10
    data.deltaAngle = 0.1
    data.startTime = time.time()
    data.timeElapsed = 0
    data.timerDelay = 50 # milliseconds
    init_1(data)
    data.gameOver = False
    start_new_thread(serverThread,(playerData,playerCount,serverChannel,data))
    #start_new_thread(timer, (playerData,data))

def init_1(data):
    data.circleList = []
    data.step = 0
    generateCircles(data)
    data.timer = 2 #secs

def getCircleRadius(data):
    circumferenceBoard = 2 * math.pi * data.width
    orbit = circumferenceBoard//data.numberOfCircles
    return orbit//(math.pi*2)//3

def generateCircles(data):
    angle = (math.pi * 2)/data.numberOfCircles
    print(data.numberOfCircles)
    for index in range(data.numberOfCircles):
        (r, g, b) = (randint(0,51), randint(0,51), randint(0,51))
        r *= 5
        g *= 5
        b *= 5
        color = rgbString(r, g, b)
        data.circleList.append(Circle(angle*index, color, data))
    if data.circleList[0].isOverlapping(data.circleList[1], data):
        data.divisor += 1
        getCircleRadius(data)
    targetIndex = randint(0, data.numberOfCircles - 1)
    targetColor = data.circleList[targetIndex].color
    data.targetCircleColor = targetColor
    getWinningCircle(data)

def getWinningCircle(data):
    for circle in data.circleList:
        if circle.color == data.targetCircleColor:
            data.winningCircle = circle
            break

def isOverlapping(angle, data):
    distance = 2 * data.circleRadius**2 * (1 + math.cos(angle))
    return distance < 2 * data.circleRadius

# from notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def difficulty(data):
    if not isOverlapping(data.deltaAngle, data):        
        if data.level % 2 == 1:
            data.numberOfCircles += 1
    if data.level % 10 == 0:
        if data.deltaAngle < 0:
            data.deltaAngle -= 0.05
        else:
            data.deltaAngle += 0.05
    if data.level % 5 == 0:
        data.deltaAngle *= -1

def handleClient(client, serverChannel, playerData):
    while client in playerData:
        try:
            msg = client.recv(100).decode("UTF-8")
            serverChannel.put((msg,client))
        except:
            return

def initiateBoard(playerData):
    for client in playerData.keys():
                msg = ""
                msg += ("dataStart")
                msg += ("~"+str(playerData[client]["number"]))
                for clientData in playerData.keys():
                    msg += ("~[%d,(%d,%d),'%s',%d]" % (playerData[clientData]["number"],
                                                playerData[clientData]["x_coord"],
                                                playerData[clientData]["y_coord"],
                                                playerData[clientData]["username"],
                                                playerData[clientData]["score"]))
                msg += ("~dataEnd\n")
                client.send(bytes(str(msg), "UTF-8"))

def serverThread(playerData, playerCount, serverChannel,data):
    global minPlayers
    while True:
        msg = serverChannel.get(True, None)
        if "send_click" in msg[0] and len(playerData) >= minPlayers:
            coords = msg[0].split("send_click")[1:]
            coords = [eval(temp) for temp in coords][0]
            playerData[msg[1]]["x_coord"] = coords[0]
            playerData[msg[1]]["y_coord"] = coords[1]
            print("Click recieved at %s from Player %d" % (str(coords),playerData[msg[1]]["number"]))
            #mousePressed(int(coords[0]),int(coords[1]),data)
            for client in playerData.keys():
                msg = ""
                msg += ("dataStart")
                msg += ("~"+str(playerData[client]["number"]))
                for clientData in playerData.keys():
                    msg += ("~[%d,(%d,%d),'%s',%d]" % (playerData[clientData]["number"],
                                                playerData[clientData]["x_coord"],
                                                playerData[clientData]["y_coord"],
                                                playerData[clientData]["username"],
                                                playerData[clientData]["score"]))
                msg += ("~dataEnd\n")
                client.send(bytes(str(msg), "UTF-8"))
        elif msg[0] == "disconnect_request":
            client = msg[1]
            print("Player %d disconnected" % playerData[client]["number"])
            del playerData[client]
            client.shutdown(0)
            playersNeeded = max((minPlayers - len(playerData)),0)
            updatePlayerCount(playerData,playersNeeded)
        elif "send_correct" in msg[0]:
            client = msg[1]
            playerData[client]["score"] += 1
            #sendCircleAnimation(playerData,data)
            data.circleList.remove(data.winningCircle)
            if len(data.circleList) == 0:
                data.level +=  1
                difficulty(data)
                init_1(data)
                sendCircleData(playerData,data)
            else:
                targetIndex = randint(0, len(data.circleList) - 1)
                targetColor = data.circleList[targetIndex].color
                data.targetCircleColor = targetColor
                getWinningCircle(data)
                data.timeElapsed += data.timerDelay
                sendCircleData(playerData,data)

def updatePlayerCount(playerData,playersNeeded):
    time.sleep(0.1)
    for uclient in playerData: #update waiting players
        print("Waiting on %d player(s)..." % playersNeeded)
        uclient.send(bytes("waiting~%d\n" % playersNeeded, "UTF-8"))
        initiateBoard(playerData)

def timer(playerData,data):
    while True:
        global minPlayers
        msToFire = 4000
        if len(playerData) >= minPlayers:
            msToFire -= 1000
        if data.timeFire % msToFire == 0:
                data.timer -= 1
                print(data.timer)
        if data.timer <= 0:
            data.gameOver = True
            print("GAME OVER")

def sendCircleData(playerData,data):
    summary = getCircleList(data)
    playerList = [c for c in playerData.keys()]
    for client in playerList:
        msg = "circles~" + str(data.deltaAngle) + "~" + str(summary) +"\n"
        client.send(bytes(msg, "UTF-8"))

def sendCircleAnimation(playerData,data):
    playerList = [c for c in playerData.keys()]
    for client in playerList:
        msg = "playAnimation" + "\n"
        client.send(bytes(msg, "UTF-8"))

def getCircleList(data):
    circleSummary = [ ]
    #rotateCircles(data)
    circleSummary.append((data.centerBoardx,data.centerBoardy,data.targetRadius,data.targetCircleColor))
    for circle in data.circleList:
        circleSummary.append((circle.x,circle.y,circle.r,circle.angle,circle.color))
    return circleSummary

clients = [ ]
serverChannel = Queue(100)
class Struct(object): pass
data = Struct()
init(data)

while True:
    client, address = server.accept()
    username = client.recv(12).decode("UTF-8")
    if len(playerData) < maxPlayers:
        playerCount += 1
        playerData[client] = dict()
        playerData[client]["username"] = username
        playerData[client]["number"] = playerCount
        playerData[client]["x_coord"] = -100
        playerData[client]["y_coord"] = -100
        playerData[client]["score"] = 0
        print("Player %d Connected as %s" % (playerData[client]["number"],username))
        playersNeeded = max((minPlayers - len(playerData)),0)
        client.send(bytes("Connected~%d\n" % playerData[client]["number"], "UTF-8"))
        sendCircleData(playerData,data)
        updatePlayerCount(playerData,playersNeeded)
        start_new_thread(handleClient, (client,serverChannel,playerData))
    else:
        client.send(bytes("Max Players Reached\n", "UTF-8"))
        client.close()

