# Snake
import math
import random
import pygame
import random
import tkinter as tk
from tkinter import messagebox
# from network import network
from genomeHandler import genomeHandler

class cube(object):
    rows = 20
    w = 500
    def __init__(self,start,dirnx=1,dirny=0,color=(255,0,0)):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1,j * dis + 1,dis - 2,dis - 2))

class snake(object):
    body = []
    turns = {}
    def __init__(self,color,pos):
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self, outputs):
        global state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == "RUN":
                        state = "PAUSE"
                    else:
                        state = "RUN"

            #keys = pygame.key.get_pressed()
            #keys[pygame.K_DOWN]
        max = 0
        mi = 0 # max index
        for i in range(len(outputs)):
            if outputs[i] > max:
                max = outputs[i]
                mi = i
        if mi == 0 and self.dirnx != 1: #left
            self.dirnx = -1
            self.dirny = 0
        elif mi == 1 and self.dirnx != -1: #right
            self.dirnx = 1
            self.dirny = 0
        elif mi == 2 and self.dirny != 1: #up
            self.dirnx = 0
            self.dirny = -1
        elif mi == 3 and self.dirny != -1: #down
            self.dirnx = 0
            self.dirny = 1
        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        if state == "RUN":
            for i, c in enumerate(self.body):
                p = c.pos[:]
                if p in self.turns:
                    turn = self.turns[p]
                    c.move(turn[0],turn[1])
                    if i == len(self.body) - 1:
                        self.turns.pop(p)
                else: c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0] - 1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0] + 1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1] + 1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

def randomSnack(rows, item):
    positions = item.body
    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x,y), positions))) > 0:
            continue
        else:
            break
    return (x,y)

def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (255,255,255), (x,0),(x,w))
        pygame.draw.line(surface, (255,255,255), (0,y),(w,y))
    pass

def redrawWindow(surface):
    global rows, width, s, snack
    surface.fill((0,0,0))
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width, rows, surface)

def drawPositions(surface, distances):
    font = pygame.font.Font('freesansbold.ttf', 20)
    black = (0, 0, 0)
    white = (255, 255, 255)

    disCount = 0
    for dis in distances:
        text = font.render(str(dis), True, black, white)
        textRect = text.get_rect()
        textRect.left = 10
        textRect.top = disCount
        disCount += 20
        surface.blit(text, textRect)

def drawInputs(surface, inputs):
    font = pygame.font.Font('freesansbold.ttf', 20)
    black = (0, 0, 0)
    white = (255, 255, 255)

    gapCount = 0
    colCount = 0
    t = ""
    for i in inputs:
        t += str(i) + " "
        colCount += 1
        if colCount >= rows:
            text = font.render(t, True, white, black)
            t = ""
            colCount = 0
            textRect = text.get_rect()
            textRect.left = 510
            textRect.top = gapCount
            gapCount += 20
            surface.blit(text, textRect)

def getInputs():
    inputs = []

    xPos = s.head.pos[0]
    yPos = s.head.pos[1]
    #Wall distances
    inputs.append(abs(yPos) / rows)
    inputs.append(abs(xPos) / rows)
    inputs.append(1 - (abs(yPos) / rows))
    inputs.append(1 - (abs(xPos) / rows))
    #Snack
    inputs.append(findSnack("y", -1))
    inputs.append(findSnack("y", 1))
    inputs.append(findSnack("x", -1))
    inputs.append(findSnack("x", 1))

    return inputs
    # for y in range(0, rows):
    #     for x in range(0, rows):
    #         #Check if Body
    #         filled = False
    #         for i in range(0, len(s.body)):
    #             if x == s.body[i].pos[0] and y == s.body[i].pos[1]:
    #                 inputs.append(1)
    #                 filled = True
    #                 break
    #         #Check if snack
    #         if filled != True:
    #             if x == snack.pos[0] and y == snack.pos[1]:
    #                 inputs.append(-1)
    #             else:
    #                 inputs.append(0)
    
    # return inputs

def findSnack(axis, dir):
    pos1 = s.head.pos[0]
    pos2 = s.head.pos[1]
    snackPos1 = snack.pos[0]
    snackPos2 = snack.pos[1]
    if axis == "y":
        pos1 = s.head.pos[1]
        pos2 = s.head.pos[0]
        snackPos1 = snack.pos[1]
        snackPos2 = snack.pos[0]

    snackFound = 0
    if dir == 1:
        while pos1 < rows - 1:
            if pos1 == snackPos1 and pos2 == snackPos2:
                snackFound = 1
            pos1 += dir
    else:
        while pos1 > 0:
            if pos1 == snackPos1 and pos2 == snackPos2:
                snackFound = 1
            pos1 += dir

    return snackFound

def getIdealOutputs():
    io = [0,0,0,0] #ideal outputs
    difX = snack.pos[0] - s.head.pos[0]
    difY = snack.pos[1] - s.head.pos[1]

    if s.dirnx == -1:
        if difX >= 0:
            if difY < 0:
                io[2] = 1 #up
            else:
                io[3] = 1 #down
        else:
            io[0] = 1 # continue
    elif s.dirnx == 1:
        if difX <= 0:
            if difY < 0:
                io[2] = 1 #up
            else:
                io[3] = 1 #down
        else:
            io[1] = 1 # continue 
    elif s.dirny == -1: # Currently Up
        if difY >= 0:
            if difX < 0:
                io[0] = 1 #left
            else:
                io[1] = 1 #right
        else:
            io[2] = 1 # continue
    elif s.dirny == 1: # Currently Down
        if difY >= 0:
            if difX < 0:
                io[0] = 1 #left
            else:
                io[1] = 1 #right
        else:
            io[3] = 1 # continue

    return io

def main():
    global width, rows, s, snack, state
    width = 500
    rows = 20
    win = pygame.display.set_mode((width, width))
    s = snake((255,0,0), (10,10))
    snack = cube(randomSnack(rows, s), color=(0,255,0))
    flag = True
    count = 0
    iterations = 10000
    clock = pygame.time.Clock()
    pygame.init()

    net = genomeHandler()
    net.init(8, 4, 100)

    state = "RUN"
    aliveCount = 0
    score = 0
    while flag:
        aliveCount += 1
        pygame.time.delay(0)
        clock.tick(1000000)

        inputs = getInputs()
        toPrint = inputs.copy()
        outputs = net.feedInputs(inputs)
        
        prevDiff = abs(snack.pos[0] - s.head.pos[0]) + abs(snack.pos[1] - s.head.pos[1])
        s.move(outputs)
        newDiff = abs(snack.pos[0] - s.head.pos[0]) + abs(snack.pos[1] - s.head.pos[1])

        if prevDiff > newDiff:
            score += 1
        else:
            score -= 1

        if s.body[0].pos == snack.pos:
            s.addCube()
            snack = cube(randomSnack(rows, s), color=(0,255,0))

        for x in range(len(s.body)):
            if (s.body[x].pos in list(map(lambda z:z.pos,s.body[x + 1:]))
                or (aliveCount >= 100 and  len(s.body) == 1)
                or (aliveCount >= 750 and  len(s.body) <= 5)
                or (aliveCount >= 5000 and  len(s.body) <= 15)
                or s.head.pos[0] < 0 or s.head.pos[0] >= rows
                or s.head.pos[1] < 0 or s.head.pos[1] >= rows):

                score += (len(s.body)-1) * 100
                net.endSimulation(score)
                print('Score: ', score)
                score = 0
                count += 1
                aliveCount = 0
                if(count < iterations):
                    s.reset((10,10))
                    #snack = cube(randomSnack(rows, s), color=(0,255,0))
                else:
                    flag = False
                break
        if aliveCount % 4 == 0:
            redrawWindow(win)
            drawPositions(win, toPrint)
            # drawInputs(win, toPrint2)
            pygame.display.update()
    pass

main()
