import pygame

import math
import numpy

from time import sleep

pygame.init()

# number of cells per generation
POPULATIONSIZE = 50
# number of generations to display
GENERATIONS = 5

# segment size of a square cell, in px
CELLSIZE_PX = 15
# time to highlight newly drawn cells, in ms
CELL_DRAWTIME_MS = 10.0
# time between drawing generations, in ms
GENERATION_DRAWTIME_MS = 25.0

# event processing loop delay, in ms
# prevents program from starving CPU
# and results in faster response to user inputs
EVENT_LOOP_MS = 5.0

AUTOPLAY = True

# return a new, blank canvas
def surface_init() -> pygame.Surface:
    # cavas dimensions in pixels (H, W)
    dimensions = (
        CELLSIZE_PX * POPULATIONSIZE,
        CELLSIZE_PX * GENERATIONS)
    surface = pygame.display.set_mode(dimensions)
    surface.fill((255, 255, 255))
    return surface

# return a new game grid containing an initial population
def grid_init(population0: list[bool]) -> list[list[bool]]:
    if len(population0) != POPULATIONSIZE:
        raise ValueError("ERROR: initial population size is " + len(population0) + " but should be " + POPULATIONSIZE)
    # 2D array, each row is a generation, row 0 is the intial popuation
    grid = [ [False] * POPULATIONSIZE ] * GENERATIONS
    grid[0] = population0
    return grid

# draw a grid onto the canvas
def draw_grid(surface: pygame.Surface, grid: list[list[bool]]):
    # clear the canvas
    surface.fill((127, 127, 127))

    # for each population, and each cell, draw the cell
    for (generation_index, population) in enumerate(grid):
        draw_grid_generation(surface, generation_index, population)

# draw a single generation in the grid
def draw_grid_generation(
        surface: pygame.Surface,
        generation_index: int,
        population: list[bool],
        cell_drawtime_ms: float = 0.0 ):
    for (cell_index, cell) in enumerate(population):
        color = "black"
        if cell == True:
            color = "white"
        # rectangle in surface coordinates representing this cell
        # coordinate transformation: start from bottom of surface
        cell_rect = pygame.Rect(
            (   cell_index * CELLSIZE_PX,
                (GENERATIONS - generation_index - 1) * CELLSIZE_PX ) ,
            (CELLSIZE_PX, CELLSIZE_PX) )

        # highlight cell being populated if animated
        if cell_drawtime_ms > 0.0:
            pygame.draw.rect(surface, "green", cell_rect, 0)
            pygame.display.update()
            sleep(cell_drawtime_ms / 1000.0)

        # draw filled rectangle
        pygame.draw.rect(
            surface,
            color,
            cell_rect
        )

        # draw cell outline (effectively creates gridlines)
        pygame.draw.rect(surface, "teal", cell_rect, 1)
        if cell_drawtime_ms > 0.0:
            pygame.display.update()

# generate a new population froma  previous population
#   population: list of 
def rule110(population: list[bool]) -> list[bool]:
    next_population = [False] * POPULATIONSIZE
    for cell_index in range(len(population)):
        x =  (cell_index - 1) % POPULATIONSIZE 
        left = population[ (cell_index - 1) % POPULATIONSIZE ]
        center = population[ cell_index ]
        right = population[ (cell_index + 1) % POPULATIONSIZE ]

        # 111 -> 0
        if left and center and right:
            next_population[cell_index] = False
        # 110 -> 1
        elif left and center and not right:
            next_population[cell_index] = True
        # 101 -> 1
        elif left and not center and right:
            next_population[cell_index] = True
        # 100 -> 0
        elif left and not center and not right:
            next_population[cell_index] = False
        # 011 -> 1
        elif not left and center and right:
            next_population[cell_index] = True
        # 010 -> 1
        elif not left and center and not right:
            next_population[cell_index] = True
        # 001 -> 1
        elif not left and not center and right:
            next_population[cell_index] = True
        # 000 -> 0
        elif left and not center and right:
            next_population[cell_index] = False

    return next_population

def generation_cycle(
        surface: pygame.Surface,
        generation: int,
        grid: list[list[bool]]) -> list[list[bool]]:
    # once the grid is initially filled, the next generation always goes on the top row
    grid_current_index = min(generation, GENERATIONS - 2)
    grid_next_index = min(generation + 1, GENERATIONS - 1)

    # if the grid is full, drop the oldest generation and shift all generations down one row
    population = grid[grid_current_index]
    if generation >= GENERATIONS - 1:
        grid = numpy.roll(grid, -1, axis=0)
        grid[GENERATIONS-1] = [False] * POPULATIONSIZE
        draw_grid(surface, grid)

    # calcuate next generation
    grid[grid_next_index] = rule110(population)
    draw_grid_generation(
        surface,
        grid_next_index,
        grid[grid_next_index],
        CELL_DRAWTIME_MS)

    # udpate display
    pygame.display.update()
    if GENERATION_DRAWTIME_MS > 0.0:
        sleep(GENERATION_DRAWTIME_MS / 1000.0)

    return grid

def main():
    # intial population with pattern [0, 0, 1, 0, 0, 1, ...]
    population0 = [False] * POPULATIONSIZE
    for cellindex in range(len(population0)):
        if cellindex % 3 == 2:
            population0[cellindex] = True
    grid = grid_init(population0)
 
    # initialize display
    pygame.display.set_caption("Rule 110")
    surface = surface_init()
    draw_grid(surface, grid)
    pygame.display.update()
    
    # main program loop
    gameover = False
    generation = 0
    while not gameover:
        generation_queued = AUTOPLAY

        # process events
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                generation_queued = True
            elif event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                gameover = True

        if generation_queued:
            grid = generation_cycle(surface, generation, grid)
            generation = generation + 1

        sleep(EVENT_LOOP_MS / 1000.0)
    
    print("game complete")

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()