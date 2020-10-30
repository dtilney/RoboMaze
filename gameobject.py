import pygame
import constants
from pygame import Vector2
import abc
import random
import math
import pymunk

# HMM, maybe it doesn't need to be an abstract class
class Component(abc.ABC):

    def __init__(self):
        self.gameobject = None

    def setup(self):
        pass

    def update(self, dt):
        pass

class Wiggle(Component):
    def __init__(self, wiggle_amount):
        self.wiggle_amount = wiggle_amount

    def update(self, dt):
        self.gameobject.components[Physics].body.velocity += random.uniform(0, self.wiggle_amount) * random_vector()

class WASDControlled(Component):
    def __init__(self, speed):
        super().__init__()
        self.speed = speed

    def update(self, dt):
        pressed = pygame.key.get_pressed()
        self.gameobject.components[Physics].body.velocity = self.speed * self.get_move_vector(pressed)

    def get_move_vector(self, pressed):
        move_vector = pymunk.Vec2d(0, 0)
        if pressed[pygame.K_w]:
            move_vector += Vector2(0, -1)
        if pressed[pygame.K_s]:
            move_vector += Vector2(0, 1)
        if pressed[pygame.K_a]:
            move_vector += Vector2(-1, 0)
        if pressed[pygame.K_d]:
            move_vector += Vector2(1, 0)

        return try_normalize(move_vector)

class Follow(Component):
    def __init__(self, target, speed):
        '''
        target - GameObject to follow
        '''
        super().__init__()
        self.speed = speed
        self.target = target

    def update(self, dt):
        pass
        v = self.target.components[Physics].body.position - self.gameobject.components[Physics].body.position
        v = try_normalize(v)
        self.gameobject.components[Physics].body.velocity = self.speed * v

class Physics(Component):
    def __init__(self, pos = Vector2(constants.DISPLAY_WIDTH/2, constants.DISPLAY_HEIGHT/2), size = Vector2(30,30), color = (255,255,255,100), moveable = True):
        # Well, this stuff shouldn't really be used except for setup
        self.pos = pos
        self.size = size
        self.color = color
        self.moveable = moveable

    def setup(self):
        body_type = pymunk.Body.DYNAMIC if self.moveable else pymunk.Body.STATIC
        self.body = pymunk.Body(1, pymunk.inf, body_type)
        self.body.position = self.pos

        self.poly = pymunk.Poly.create_box(self.body, self.size, 3) #roundedness
        self.poly.color = self.color
        
        self.gameobject.game.space.add(self.body, self.poly)

    def update(self, dt):
        self.gameobject.pos = Vector2(self.body.position)

class GameObject:
    def __init__(self, game, components):
        ''' 
        components -- list of Components objects
        '''
        self.game = game
        # self.components is a Dict mapping Component classes (the keys) to Component objects (the values)
        self.components = {type(comp) : comp for comp in components}
        for component in components:
            component.gameobject = self
            component.setup()
    
    def update(self, dt):
        for component in self.components.values():
            component.update(dt)

    def draw(self, display):
        # The physics debug drawing is done outside GameObject.draw
        pass
    #     pygame.draw.rect(display, constants.CYAN, self.get_rect())
    #     print(self.get_rect())

    # def get_rect(self):
    #     return pygame.Rect(self.components[Physics].body.position - self.components[Physics].size/2, self.components[Physics].size)

### Utility functions ###

def try_normalize(v):
    if v == Vector2(0,0):
        return v
    return v.normalized()

def random_vector():
    theta = random.uniform(0, 2*math.pi)
    return Vector2(math.cos(theta), math.sin(theta))

### The GameObjects ###

def make_player(game):
    return GameObject(game, components = [WASDControlled(200), Physics(color = (0,255,0,50))])

def make_enemy(game, target):
    return GameObject(game, components = [Follow(target, 50), Wiggle(1), Physics(size = Vector2(15,15), color = (255,0,0,50))])

def make_wall(game, pos):
    return GameObject(game, components = [Physics(pos = pos, size = Vector2(60,60), color = (150,150,255,50), moveable=False)])