import pygame
from pygame import *

def size(x,y):
    pygame.init()
    screen = pygame.display.set_mode((x,y))
    global bg
    bg = Surface((x,y))
    return [screen,bg]

def rect(x,y,w,h,screen,fill=Color(150,150,150)):
    pygame.draw.rect(screen,fill,(x,y,w,h))