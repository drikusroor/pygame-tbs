import itertools
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.best_first import BestFirst
from enum import Enum
from random import randrange
import copy

#!/usr/bin/python
import time

GRID_SIZE = 48


class SSGrid:
    def __init__(self, config):
        self.TILE_SIZE = 8
        self.GRID = []
        self.entities = []

        for _x in itertools.repeat(None, GRID_SIZE):
            GRID_SLICE = []
            for _y in itertools.repeat(None, GRID_SIZE):
                tile = 1
                GRID_SLICE.append(tile)
            self.GRID.append(GRID_SLICE)

    def get_walkable_grid(self, client):
        walkable_grid = copy.deepcopy(self.GRID)
        for entity in self.entities:
            if client != entity:
                y, x = entity.position
                walkable_grid[y][x] = 0
        return walkable_grid

    def get_row(self, index):
        return self.GRID[index]

    def get_column(self, index):
        COLUMN = []
        for y in itertools.repeat(None, len(self.GRID)):
            COLUMN.append(self.GRID[y][index])
        return COLUMN

    def get_entities_alive(self):
        return list(filter(lambda x: not x.is_dead(), self.entities))

    def find_path(self, a, b, grid):
        path_grid = Grid(matrix=grid)
        start = path_grid.node(a[0], a[1])
        end = path_grid.node(b[0], b[1])
        finder = BestFirst(diagonal_movement=DiagonalMovement.always)
        path, _runs = finder.find_path(start, end, path_grid)
        return path

    def register_entity(self, entity):
        self.entities.append((entity))

    def register_turn_handler(self, turn_handler):
        self.turn_handler = turn_handler


class EntityTypes(Enum):
    NPC = (0,)
    PLAYER = 1


class Entity:
    def __init__(self, name, entity_type, grid, position):
        self.name = name
        self.type = entity_type
        self.grid = grid
        self.position = position
        self.max_hp = 10
        self.hp = self.max_hp
        self.max_ap = 20
        self.ap = self.max_ap
        grid.register_entity(self)

    def reset_turn(self):
        self.ap = self.max_ap

    def is_dead(self):
        return self.hp <= 0

    def find_nearest_target(self):
        target_paths = []
        walkable_grid = self.grid.get_walkable_grid(self)

        for entity in self.grid.entities:
            if entity.type != self.type and not entity.is_dead():
                target = entity
                path_to_target = self.grid.find_path(
                    self.position, target.position, walkable_grid
                )
                target_paths.append((target, path_to_target))

        if len(target_paths) < 1:
            return (None, None)
        else:

            def sort_entities(target_path):
                return len(target_path[1])

            target_paths.sort(key=sort_entities)
            return target_paths[0]

    def do_action(self):
        if self.type == EntityTypes.NPC or self.type == EntityTypes.PLAYER:

            if self.is_dead():
                return self.grid.turn_handler.next_turn()

            target_path = self.find_nearest_target()

            target, path_to_target = target_path

            if target == None or path_to_target == None:
                return self.grid.turn_handler.next_turn()

            if self.ap >= 10:
                if len(path_to_target) < 3:
                    amount = randrange(0, 5)
                    target.hp -= amount
                    self.ap = self.ap - 10
                else:
                    step = path_to_target[1]
                    self.position = step
                    self.ap = self.ap - 2
            elif self.ap >= 2:
                if len(path_to_target) > 2:
                    step = path_to_target[1]
                    self.position = step
                    self.ap = self.ap - 2
                else:
                    return self.grid.turn_handler.next_turn()
            else:
                return self.grid.turn_handler.next_turn()


class TurnHandler:
    def __init__(self, entities, rounds=100):
        self.entities = entities
        self.rounds = rounds
        self.rounds_left = self.rounds
        self.current_entity = 0

    def register_grid(self, grid):
        self.grid = grid

    def get_current_entity(self):
        return self.entities[self.current_entity]

    def next_round(self):
        self.rounds_left = self.rounds_left - 1
        self.entities = self.grid.get_entities_alive()
        self.current_entity = 0

    def next_turn(self):
        self.current_entity += 1
        if len(self.entities) <= self.current_entity:
            self.next_round()
        else:
            entity = self.entities[self.current_entity]
            entity.reset_turn()


grid = SSGrid(None)

for i in range(10):

    exists = True

    while exists:
        position = (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE))
        exists = any(position == e.position for e in grid.entities)

    player = Entity(
        "Drikus no. {no}".format(no=i),
        EntityTypes.PLAYER,
        grid,
        (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE)),
    )

    exists = True

    while exists:
        position = (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE))
        exists = any(position == e.position for e in grid.entities)

    npc = Entity(
        "NPC no. {no}".format(no=i),
        EntityTypes.NPC,
        grid,
        (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE)),
    )

turn_handler = TurnHandler([player, npc])
grid.register_turn_handler(turn_handler)
turn_handler.register_grid(grid)

###################################################
################### GAME LOOP #####################
###################################################

# PyGame template.

# Import standard modules.
import sys

# Import non-standard modules.
import pygame
from pygame.locals import *

# Initialize the font system and create the font and font renderer
pygame.font.init()
default_font = pygame.font.get_default_font()
font_renderer = pygame.font.Font(default_font, 13)


def update(dt):
    """
  Update game. Called once per frame.
  dt is the amount of time passed since last frame.
  If you want to have constant apparent movement no matter your framerate,
  what you can do is something like
  
  x += v * dt
  
  and this will scale your velocity based on time. Extend as necessary."""

    # Go through events that are passed to the script by the window.
    for event in pygame.event.get():
        # We need to handle these events. Initially the only one you'll want to care
        # about is the QUIT event, because if you don't handle it, your game will crash
        # whenever someone tries to exit.
        if event.type == QUIT:
            pygame.quit()  # Opposite of pygame.init
            sys.exit()  # Not including this line crashes the script on Windows. Possibly
            # on other operating systems too, but I don't know for sure.
        # Handle other events as you wish.

    entity = grid.turn_handler.get_current_entity()
    entity.do_action()


def draw_hud(screen, grid):

    # Draw Name / HP / AP
    entity = grid.turn_handler.get_current_entity()
    entity_info_text = "{name} / {hp}/{max_hp}HP / {ap}/{max_ap}AP".format(
        name=entity.name,
        hp=entity.hp,
        max_hp=entity.max_hp,
        ap=entity.ap,
        max_ap=entity.max_ap,
    )

    entity_info_render = font_renderer.render(
        entity_info_text, 1, (255, 255, 255)  # The font to render  # With anti aliasing
    )  # RGB Color

    screen.blit(
        entity_info_render, (0, 0)  # The text to render
    )  # Where on the destination surface to render said font


def draw(screen):
    """
  Draw things to the window. Called once per frame.
  """
    screen.fill((0, 0, 0))  # Fill the screen with black.

    # Redraw screen here.
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(
                x * grid.TILE_SIZE, y * grid.TILE_SIZE, grid.TILE_SIZE, grid.TILE_SIZE
            )
            color = 255 - (255 / (grid.GRID[y][x] + 1))
            color_triple = (color, color, color)
            pygame.draw.rect(screen, color_triple, rect)

    for entity in grid.entities:
        rect = pygame.Rect(
            entity.position[1] * grid.TILE_SIZE,
            entity.position[0] * grid.TILE_SIZE,
            grid.TILE_SIZE,
            grid.TILE_SIZE,
        )
        color = (255, 255, 255)
        if entity.type == EntityTypes.PLAYER:
            color = (0, 128, 0)
        elif entity.type == EntityTypes.NPC:
            color = (128, 0, 0)
        if entity.is_dead():
            color = (255, 0, 0)
        pygame.draw.rect(screen, color, rect)

    draw_hud(screen, grid)

    # Flip the display so that the things we drew actually show up.
    pygame.display.flip()


def runPyGame():
    # Initialise PyGame.
    pygame.init()

    # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
    fps = 60.0
    fpsClock = pygame.time.Clock()

    # Set up the window.
    width, height = 640, 480
    screen = pygame.display.set_mode((width, height))

    # screen is the surface representing the window.
    # PyGame surfaces can be thought of as screen sections that you can draw onto.
    # You can also draw surfaces onto other surfaces, rotate surfaces, and transform surfaces.

    # Main game loop.
    dt = 1 / fps  # dt is the time since last frame.
    while True:  # Loop forever!
        update(dt)  # You can update/draw here, I've just moved the code for neatness.
        draw(screen)
        dt = fpsClock.tick(fps)


runPyGame()
