#Hack112 - CardBoard Client

from tkinter import *
import socket
from _thread import *
import string, math
from random import randint

def serverHandle(server,data):
    while True:
        msg = server.recv(1).decode("UTF-8")
        fullMsg = msg
        while True:
            msg = server.recv(1).decode("UTF-8")
            fullMsg += msg
            if "\n" in msg:
                break
        msg = fullMsg
        if "Max Players Reached" in msg:
            print(msg)
            data.connected = False #close thread
            closeWindow(data)
            return
        elif "Connected" in msg:
            print("Connected")
            data.whoAmI = msg.split("~")[1]
            data.connected = True
        elif "ping" in msg.lower():
            pass
        elif "dataStart~" in msg:
            data.board = dict()
            transmisson = msg.split("~")
            data.whoAmI = transmisson[1]
            for bit in transmisson[2:]:
                if "dataEnd" not in bit:
                    temp = eval(bit)
                    if str(temp[2]) not in data.board:
                        data.board[temp[2]] = dict()
                    data.board[temp[2]]["pos"] = temp[1]
                    data.board[temp[2]]["score"] = temp[3]
        elif "waiting" in msg:
            data.playersNeeded = int(msg.split("~")[1])
        elif "circles~" in msg:
            cir = msg.split("~")[-1]
            data.deltaAngle += float(msg.split("~")[1])
            try:
                cir = eval(cir)
                data.circleList = [ ]
                for tcir in range(len(cir)):
                    if tcir == 0:
                        data.targetCircle = TargetCircle(cir[tcir][0],cir[tcir][1],cir[tcir][2],cir[tcir][3])
                        continue
                    x,y,r,angle,color = cir[tcir][0],cir[tcir][1],cir[tcir][2],cir[tcir][3],cir[tcir][4]
                    nc = Circle(x,y,r,angle,color,data)
                    data.circleList.append(nc)
                data.numberOfCircles = len(data.circleList)
                data.circleRadius = int(getCircleRadius(data))
                data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
                getWinningCircle(data)
            except:
                pass #don't crash on bad transmit
        elif "playAnimation" in msg:
            data.clearedCircle = True
            getWinningCircle(data)
        else:
            print("UNKNOWN MESSAGE: %s" % msg)

class Circle(object):
    def __init__(self,x,y,r,angle,color,data):
        self.angle = angle
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.rotateR = data.boardRadius

    def rotate(self,data):
        self.angle += data.deltaAngle
        self.angle %= math.pi * 2
        self.x = int(data.centerBoardx + data.boardRadius * math.cos(self.angle))
        self.y = int(data.centerBoardy + data.boardRadius * math.sin(self.angle))
        self.r = data.circleRadius

    def updateCoords(self, data):
        self.x = int(data.centerBoardx + self.rotateR * math.cos(self.angle))
        self.y = int(data.centerBoardy + self.rotateR * math.sin(self.angle))

    def validClickInsideCircle(self, x, y):
        return ((x-self.x)**2 + (y-self.y)**2)**.5 <= self.r

    def __eq__(self,other):
        if isinstance(other,Circle):
            return self.color == other.color

class TargetCircle(object):
    def __init__(self,x,y,r,color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

def init(data):
    data.username = ""
    data.tempUsername = ""
    data.connected = False
    data.whoAmI = None
    data.board = dict()
    data.playersNeeded = -1
    data.circleList = [ ]
    data.targetCircle = (0,0,0)
    initTitle(data)
    data.divisor = 3
    data.deltaAngle = 0.05
    data.numberOfCircles = 0
    data.centerBoardx = data.width // 2
    data.centerBoardy = (1/10) * data.height + data.centerBoardx
    data.circleRadius = int(getCircleRadius(data))
    data.boardRadius = int(data.centerBoardx - 2 * data.circleRadius)
    data.targetRadius = data.width//10
    data.playerData = dict()
    data.clearedCircle = False
    data.winningCircle = None
    data.wonLevel = False
    data.timeElapsed = 0 #Used for transition between levels
    data.winDelay = 800

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

def getWinningCircle(data):
    for circle in data.circleList:
        if circle.color == data.targetCircle.color:
            data.winningCircle = circle

def getCircleRadius(data):
    if data.numberOfCircles <= 10:
        numberOfCircles = 9 #Reference number for standard board
    else:
        numberOfCircles = data.numberOfCircles
    circumferenceBoard = 2 * math.pi * data.width
    orbit = circumferenceBoard//(numberOfCircles // 3)
    return orbit//(math.pi*2)//4

def connectToServer(data):
    HOST = "25.130.151.205"
    PORT = 8081
    try:
        data.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data.server.connect((HOST,PORT))
        data.server.send(bytes(data.username, "UTF-8"))
        start_new_thread(serverHandle, (data.server,data))
    except:
        print("Can't connect to server!")
        data.connected = False
        closeWindow(data)

def closeWindow(data):
    if data.connected == True:
        print("Disconnected from server")
        msg = "disconnect_request"
        data.server.send(bytes(msg, "UTF-8"))
        data.server.shutdown(0)
        data.root.destroy()
    else:
        data.root.destroy()

def mousePressed(event, data):
    if data.connected:
        for circle in data.circleList:
            if circle.validClickInsideCircle(event.x, event.y) and circle.color == data.targetCircle.color:
                data.clearedCircle = True
                data.winningCircle = circle
        msg = "send_click(%d, %d)" % (event.x, event.y)
        data.server.send(bytes(msg, "UTF-8"))

def keyPressed(event, data):
    if data.username == "":
        if event.keysym in (string.ascii_letters+string.digits) and len(data.tempUsername) < 10:
            data.tempUsername += event.keysym
        elif event.keysym == "BackSpace":
            data.tempUsername = data.tempUsername[:-1]
        elif event.keysym == "Return":
            data.username = data.tempUsername
            connectToServer(data)

def timerFired(data):
    data.circleRadius = int(getCircleRadius(data))
    for circle in data.circleList:
        circle.rotate(data)
    if data.clearedCircle:
        data.timeElapsed += data.timerDelay
        if data.timeElapsed % data.winDelay != 0:
            getWinningCircle(data)
            data.winningCircle.rotateR += data.timerDelay
            data.winningCircle.updateCoords(data)
            return
        data.timeElapsed = 0
        data.clearedCircle = False
        data.circleList.remove(data.winningCircle)
        data.winningCircle = None
        newNumberOfCircles = len(data.circleList)
        msg = "send_correct"
        data.server.send(bytes(msg, "UTF-8"))

def drawTitle(canvas,data):
    canvas.create_text(data.width//2-data.tr_offsetX,50+data.tr_offsetY,text=data.gameName, 
        fill=data.tr_offsetFontColor, font=data.tr_font)
    canvas.create_text(data.width//2,50,text=data.gameName, 
        fill=data.tr_fontColor, font=data.tr_font)

def drawLevel(canvas,data):
    font = "Verdana 20"
    canvas.create_text(data.width//2,100,text="Level %d" % data.level, 
        fill=data.tr_fontColor, font=font)

def rgbString(rgb):
    red, green, blue = rgb
    return "#%02x%02x%02x" % (red, green, blue)

def redrawAll(canvas, data):
    if data.username == "":
        canvas.create_text(data.width//2,data.height//2,text="Enter Name: %s" % data.tempUsername)
    elif data.playersNeeded == 0:
        drawTitle(canvas,data)
        canvas.create_text(data.width//2,10,text="Player: %s" % data.username,font="Vernanda 10 bold")
        for player in data.board:
            x, y = data.board[player]["pos"][0], data.board[player]["pos"][1]
            canvas.create_text(x,y,text=player)
        for circle in data.circleList:
            (top, left) = (circle.x - circle.r, circle.y - circle.r)
            (bottom, right) = (circle.x + circle.r, circle.y + circle.r)
            if circle == data.winningCircle:
                if not data.clearedCircle:
                    canvas.create_line(circle.x, circle.y, data.centerBoardx, data.centerBoardy,
                                fill = circle.color, width = 5)
            else:
                canvas.create_line(circle.x, circle.y, data.centerBoardx, data.centerBoardy,
                    fill = circle.color, width = 5)
            canvas.create_oval(top, left, bottom, right, fill=circle.color)
        tr, color = data.targetCircle.r,data.targetCircle.color
        tx, ty = data.centerBoardx, data.centerBoardy
        canvas.create_oval(tx-tr,ty-tr,tx+tr,ty+tr,fill=color)
        scoreStep = 1
        canvas.create_text(50,80,text="SCORES:", font = "Vernanda 12 bold")
        for player in data.board:
            score = data.board[player]["score"]
            canvas.create_text(10,90+25*scoreStep,text="%s: %d" % (player,score),anchor=SW)
            scoreStep += 1
    elif data.connected == True:
        canvas.create_text(data.width//2,data.height//2,text="Waiting for %d player(s) to connect..." % data.playersNeeded)
    else:
        canvas.create_text(data.width//2,data.height//2,text="Connecting to server")


####################################
# Run
####################################

def runGame():
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
    data.root = root
    data.height = (14/16)* root.winfo_screenheight()
    data.width = (4/5) * root.winfo_screenheight()
    #data.height = 300
    #data.width = 300
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.protocol("WM_DELETE_WINDOW", lambda : closeWindow(data))
    # and launch the app
    root.mainloop()  # blocks until window is closed

runGame()
