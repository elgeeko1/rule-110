import pygame

import math
import numpy

from time import sleep

pygame.init()

# number of cells per generation
CELLS_PER_ROW = 80
# number of rows to display
DISPLAY_ROWS = 80

# segment size of a square cell, in px
CELL_SIZE_PX = 15
# time to highlight newly drawn cells, in ms
CELL_DRAWTIME_MS = 0.0
# delay between drawing rows, in ms
ROW_DRAWTIME_MS = 25.0

# event processing loop delay, in ms
# prevents program from starving CPU
# and results in faster response to user inputs
EVENT_LOOP_MS = 10.0

AUTOPLAY = True

# return a new, blank canvas
def surface_init() -> pygame.Surface:
    # cavas dimensions in pixels (H, W)
    dimensions = (
        CELL_SIZE_PX * CELLS_PER_ROW,
        CELL_SIZE_PX * DISPLAY_ROWS)
    surface = pygame.display.set_mode(dimensions)
    return surface

# return the grid index for a generation
def generation_to_row(generation: int) -> int:
    return max(min(generation, DISPLAY_ROWS - 1), 0)

# return a new game grid containing an initial population
def grid_init(cells0: list[bool]) -> list[list[bool]]:
    if len(cells0) != CELLS_PER_ROW:
        raise ValueError("ERROR: initial population size is " + len(cells0) + " but should be " + CELLS_PER_ROW)
    # 2D array, each row is a generation, row 0 is the intial popuation
    grid = [ [False] * CELLS_PER_ROW ] * DISPLAY_ROWS
    grid[0] = cells0
    return grid

# draw a grid onto the canvas
def grid_draw(surface: pygame.Surface, grid: list[list[bool]]):
    # clear the canvas
    surface.fill("black")
    # draw each row
    for (row_index, cells) in enumerate(grid):
        grid_draw_row(surface, row_index, cells)

# draw a single generation in the grid
def grid_draw_row(
        surface: pygame.Surface,
        row_index: int,
        population: list[bool],
        cell_drawtime_ms: float = 0.0 ):
    for (cell_index, cell) in enumerate(population):
        color = "black"
        if cell == True:
            color = "white"
        # rectangle in surface coordinates representing this cell
        # coordinate transformation: start from bottom of surface
        cell_rect = pygame.Rect(
            (   cell_index * CELL_SIZE_PX,
                (DISPLAY_ROWS - row_index - 1) * CELL_SIZE_PX ) ,
            (CELL_SIZE_PX, CELL_SIZE_PX) )

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

# generate a new population from a previous population
#   cells: row of cells
def rule110(cells: list[bool]) -> list[bool]:
    cells_next = [False] * CELLS_PER_ROW
    for cell_index in range(len(cells)):
        x =  (cell_index - 1) % CELLS_PER_ROW 
        left = cells[ (cell_index - 1) % CELLS_PER_ROW ]
        center = cells[ cell_index ]
        right = cells[ (cell_index + 1) % CELLS_PER_ROW ]

        # 111 -> 0
        if left and center and right:
            cells_next[cell_index] = False
        # 110 -> 1
        elif left and center and not right:
            cells_next[cell_index] = True
        # 101 -> 1
        elif left and not center and right:
            cells_next[cell_index] = True
        # 100 -> 0
        elif left and not center and not right:
            cells_next[cell_index] = False
        # 011 -> 1
        elif not left and center and right:
            cells_next[cell_index] = True
        # 010 -> 1
        elif not left and center and not right:
            cells_next[cell_index] = True
        # 001 -> 1
        elif not left and not center and right:
            cells_next[cell_index] = True
        # 000 -> 0
        elif left and not center and right:
            cells_next[cell_index] = False

    return cells_next

def cycle(
        surface: pygame.Surface,
        grid: list[list[bool]],
        generation: int) -> list[list[bool]]:
    # determine current and next generation indexes in the grid
    row_current_index = generation_to_row(generation)
    row_next_index = generation_to_row(generation + 1)

    # if the grid is full, drop the oldest generation and shift all rows down one
    cells = grid[row_current_index]
    if (generation + 1) >= DISPLAY_ROWS:
        grid = numpy.roll(grid, -1, axis=0)
        grid[row_next_index] = [False] * CELLS_PER_ROW
        grid_draw(surface, grid)

    # calcuate next generation
    grid[row_next_index] = rule110(cells)
    grid_draw_row(
        surface,
        row_next_index,
        grid[row_next_index],
        CELL_DRAWTIME_MS)

    # udpate display
    pygame.display.update()

    return grid


def main():
    # intial population with pattern [0, 0, 1, 0, 0, 1, ...]
    cells0 = [False] * CELLS_PER_ROW
    for cellindex in range(len(cells0)):
        if cellindex % 3 == 2:
            cells0[cellindex] = True
    grid = grid_init(cells0)
 
    # initialize display
    pygame.display.set_caption("Rule 110")
    surface = surface_init()
    grid_draw(surface, grid)
    pygame.display.update()
    
    # main program loop
    gameover = False
    generation = 0
    while not gameover:
        next_generation = AUTOPLAY

        # process events
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                next_generation = True
            elif event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                gameover = True

        if next_generation:
            grid = cycle(surface, grid, generation)
            generation = generation + 1
            if ROW_DRAWTIME_MS > 0.0:
                sleep(ROW_DRAWTIME_MS / 1000.0)

        sleep(EVENT_LOOP_MS / 1000.0)
    
    print("game complete")

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()