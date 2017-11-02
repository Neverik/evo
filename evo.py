from __future__ import division
import random
from nn import *
from gamelib import *
import numpy as np
from pygame import *
from mathematics import *
import pygame
from pygame.locals import Color
import math
import copy
import time
import pickle
import sys

print('''
Evolution simulator by Stepan Shabalin. Copyright 2017.

Libraries: pygame, numpy, noise.
Features: Return to save, Tab to load.

''')

#creature class
class creature (object):
    #constructor
    def __init__(self,startsize,startnet,startx,starty,index):
        self.psize = startsize
        self.pnetwork = startnet
        self.size = startsize
        self.network = startnet
        self.x = startx
        self.y = starty
        self.px = self.x
        self.py = self.y
        self.speech = 0
        self.index = index
        self.age = 0
        self.memory = [0,0,0,0]
    #decision making
    def decision(self, inputs):
        return self.network.run(inputs)
    #life cycle
    def eachframe(self):
        if self.x > numtiles - 5:
            self.x = 5
        if self.y > numtiles - 5:
            self.y = 5
        if self.x < 5:
            self.x = numtiles - 5
        if self.y < 5:
            self.y = numtiles - 5
        #get information about the world
        under = tiles[int(self.x)][int(self.y)]/255
        u = tiles[int(self.x)][int(self.y+1)]/255
        r = tiles[int(self.x+1)][int(self.y)]/255
        d = tiles[int(self.x)][int(self.y-1)]/255
        l = tiles[int(self.x-1)][int(self.y)]/255
        #check distance to creatures
        nearest = 10
        nearest_creature = self
        for creat in creatures:
            cx = abs(creat.x - self.y)
            cy = abs(creat.y - self.y)
            dist = math.hypot(cx,cy)
            if dist < nearest and creat != self:
                nearest = dist
                nearest_creature = creat
        drawcolor = Color(255,255,50)
        #feed that information to net
        inputdata = [under,self.speech,nearest/numtiles,self.x/numtiles,self.y/numtiles,u,r,d,l,self.memory[0],self.memory[1],self.memory[2],self.memory[3]]
        response = self.decision(inputdata)
        #reformat response
        for i in range(len(response)-1):
            if response[i] < 0:
                response[i] *= -1
            if response[i] > 10:
                response[i] = 10
            response[i] *= 0.1
        #move
        self.x += response[3] * creature_size
        self.x -= response[2] * creature_size
        self.y += response[1] * creature_size
        self.y -= response[0] * creature_size
        if self.x > numtiles - 10:
            self.x = 10
        if self.y > numtiles - 10:
            self.y = 10
        if self.x < 10:
            self.x = numtiles - 10
        if self.y < 10:
            self.y = numtiles - 10
        #eat
        if response[5] > 0.5:
            self.size -= 0.5
            self.size += tiles[int(abs(self.x))][int(abs(self.y))]/255
            tiles[int(abs(self.x))][int(abs(self.y))] -= tiles[int(abs(self.x))][int(abs(self.y))]/255
        #learn
        if self.size < self.psize:
            self.network = copy.deepcopy(self.pnetwork)
        else:
            self.network.weights = self.network.mutate(0.05)
        self.psize = self.size
        self.pnetwork = copy.deepcopy(self.network)
        #reset speech variable
        self.speech = 0
        #interact with other creatures
        nearest_creature.speech = response[7]
        #vomit
        if response[6] > 0.5:
            drawcolor = Color(0,255,0)
            nearest_creature.size += 1
            self.size -= 1
        #give birth
        if self.size > birthrate:
            self.birth()
        if len(creatures) < mincreatures:
            network = net(numinputs,layersdeep,neuronsperlayer,numoutputs)
            csize = random.randint(minsize,maxsize)
            poosx = random.randint(maxsize,numtiles-maxsize)
            poosy = random.randint(maxsize,numtiles-maxsize)
            generated = creature(csize, network, poosx, poosy,len(creatures))
            creatures.append(generated)
        #die
        self.size -= 0.1
        if self.size < 5:
            tiles[int(self.x)][int(self.y)] += 100
            creatures.remove(self)
        #attack
        if response[8] > 0.5 and nearest_creature.size > 5:
            if nearest_creature != self:
                drawcolor = (255,0,0)
                nearest_creature.size -= 5
                self.size += 5
        #draw lines
        if nearest != self:
            selfx = int((self.x+xo)*ppt + self.size/2)
            selfy = int((self.y+yo)*ppt + self.size/2)
            neax = int((nearest_creature.x+xo)*ppt + nearest_creature.size/2)
            neay = int((nearest_creature.y+yo)*ppt + nearest_creature.size/2)
            try:
                pygame.draw.line(screen, drawcolor, (selfx,selfy), (neax,neay), 1)
            except:
                pass
            
        #memory
        self.memory = response[9:13]

    def birth(self):
        creat = creature(self.size/2, self.network, self.x, self.y, len(creatures))
        creat.network.layers = creat.network.mutate(0.2)
        creatures.append(creat)
        self.size /= 2
    
birthrate = 30            
            
screensize = 800
        
info = size(screensize,screensize)
        
numtiles = 100

scale = 5

def generateterrain(numtiles,r,scale):
    tiles = np.random.randn(numtiles,numtiles).tolist()
    for x in range(numtiles):
        for y in range(numtiles):
            tiles[x][y] = perlin(x/numtiles+r,y/numtiles+r,scale)
    for x in range(len(tiles)):
        for y in range(len(tiles)):
            colour = int(tiles[x][y]*350)
            if(colour < 0):
                colour = 0
            if(colour > 254):
                colour = 255
            tiles[x][y] = colour
    return tiles

r = random.randint(0,50000)

screen = info[0]
bg = info[1]

tiles = generateterrain(numtiles,r,scale)

ppt = screensize/numtiles

numcreatures = 40

creatures = []

ori_tiles = copy.deepcopy(tiles)

layersdeep = 5
neuronsperlayer = 10
numoutputs = 13
numinputs = 13

minsize = 5
maxsize = 10

def generatecreatures():
    for tobegenerated in range(numcreatures):
        network = net(numinputs,layersdeep,neuronsperlayer,numoutputs)
        csize = random.randint(minsize,maxsize)
        posx = random.randint(maxsize,numtiles-maxsize)
        posy = random.randint(maxsize,numtiles-maxsize)
        generated = creature(csize, network, posx, posy,len(creatures))
        creatures.append(generated)

generatecreatures()
        
col_creature = Color(255,230,0)
  
mincreatures = 5

restore_speed = 1
tick = 0
restore_speed_2 = 100

creature_size = 0.5

creature_scale = 0.05

xo = 0
yo = 0
zoom = 1

fps = 20

def save(filename):
    global creatures
    global tiles
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump([creatures,tiles], f)
    print("Saved as: " + filename)
    
def load(filename):
    global creatures
    global tiles
    with open(filename + '.pkl', 'rb') as f:
        return pickle.load(f)

def draw():
    global xo
    global yo
    global zoom
    global tiles
    global creatures
    global ori_tiles
    keys=pygame.key.get_pressed()
    if keys[K_LEFT]:
        xo += 10/zoom
    if keys[K_RIGHT]:
        xo -= 10/zoom
    if keys[K_UP]:
        yo += 10/zoom
    if keys[K_DOWN]:
        yo -= 10/zoom
    if keys[K_RETURN]:
        print("Filename to save:")
        inp = input()
        save(inp)
    if keys[K_TAB]:
        print("Filename to load: ")
        inp = input()
        restored = load(inp)
        creatures = copy.deepcopy(restored[0])
        tiles = copy.deepcopy(restored[1])
        ori_tiles = copy.deepcopy(restored[1])
    if keys[K_SPACE]:
        while True:
            if pygame.key.get_pressed()[K_SPACE]:
                return
    
    global ppt
    global tick
    global screensize
    for e in pygame.event.get():
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4:
                ppt *= 2
                zoom *= 2
            elif e.button == 5:
                ppt /= 2
                zoom /= 2
        if e.type == QUIT:
            raise SystemExit
    
    screen.blit(bg, (0,0))
    screen.fill(Color(255,255,255))
    tick += 1
    for x in range(len(tiles)):
        for y in range(len(tiles)):
            colour = int(tiles[x][y])
            if(colour < 0):
                colour = 0
            if(colour > 254):
                colour = 255
            tiles[x][y] = colour
            real_colour = Color(5,colour,5)
            if colour < 99:
                real_colour = Color(0,87,255)
            pygame.draw.rect(screen,real_colour,((x+xo)*ppt,(y+yo)*ppt,ppt,ppt))
            if tick > restore_speed_2:
                if tiles[x][y] < ori_tiles[x][y]:
                    tiles[x][y] += restore_speed
    if tick > restore_speed_2:
        tick = 0
    
    for creat in creatures:
        try:
            posx = int((creat.x + xo) * ppt + creat.size/2)
            posy = int((creat.y + yo) * ppt + creat.size/2)
            pygame.draw.circle(screen, col_creature, (posx,posy), int(abs(creat.size*creature_scale)*ppt))
            creat.eachframe()
        except:
            pass
    pygame.display.update()
    time.sleep(1/fps)

def main():
    while True:
        draw()
main()
