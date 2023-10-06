import pygame

import math
import numpy

from time import sleep

pygame.init()

# number of cells per generation
CELLS_PER_ROW = 79
# segment size of a square cell, in px
CELL_SIZE_PX = 15
# number of rows to display
DISPLAY_ROWS = CELLS_PER_ROW
# width of the canvas, in px
DISPLAY_WIDTH = CELL_SIZE_PX * CELLS_PER_ROW
# height of the canvas, in px
DISPLAY_HEIGHT = CELL_SIZE_PX * DISPLAY_ROWS
# time to highlight newly drawn cells, in ms
CELL_DRAWTIME_MS = 0.0
# delay between drawing rows, in ms
ROW_DRAWTIME_MS = 25.0

# event processing loop delay, in ms
# prevents program from starving CPU
# and results in faster response to user inputs
EVENT_LOOP_MS = 10.0

# automatically cycle generations?
AUTOPLAY = True

###################
# game logic
###################

# return a new, blank canvas sized to game grid
#   returns: new canvas
def canvas_init() -> pygame.Surface:
    # cavas dimensions in pixels (H, W)
    dimensions = ( DISPLAY_WIDTH, DISPLAY_HEIGHT )
    canvas = pygame.display.set_mode(dimensions)
    return canvas

# grid row index for a generation
#   returns: row index for the given generation
def generation_to_row(generation: int) -> int:
    return max(min(generation, DISPLAY_ROWS - 1), 0)

# initialize a new game grid containing an initial population
#   seed_cells: seed population, list of booleans
#   returns: 2D grid containing DISPLAY_ROWS, with seed population in first row
def grid_init(seed_cells: list[bool]) -> list[list[bool]]:
    if len(seed_cells) != CELLS_PER_ROW:
        raise ValueError("ERROR: initial population size is "
                         + len(seed_cells)
                         + " but should be "
                         + CELLS_PER_ROW)
    # 2D array, each row is a generation, row 0 is the intial popuation
    grid = [ [False] * CELLS_PER_ROW ] * DISPLAY_ROWS
    grid[0] = seed_cells
    return grid

# draw a grid onto the canvas
#   canvas: canvas on which to draw
#   grid: 2D grid to draw
def grid_draw(canvas: pygame.Surface, grid: list[list[bool]]):
    # clear the canvas
    canvas.fill("black")
    # draw each row
    for (row_index, cells) in enumerate(grid):
        grid_draw_row(canvas, row_index, cells)

# draw a row of cells in the grid
#   canvas: canvas on which to draw
#   row_index: index of the row in the grid in which to paint the cells
#   cells: cells to draw
#   cell_drawtime_ms: time to highlight each cell before advancing to the next; defaults to zero
def grid_draw_row(canvas: pygame.Surface,
                  row_index: int,
                  cells: list[bool],
                  cell_drawtime_ms: float = 0.0 ):
    # for each cell, highlight and paint according to its state
    for (cell_index, cell) in  enumerate(cells):
        color = "black"
        if cell == True:
            color = "white"
        
        # rectangle in canvas coordinates representing this cell
        # coordinate transformation: start from bottom of canvas
        cell_rect = pygame.Rect((cell_index * CELL_SIZE_PX,
                                   (DISPLAY_ROWS - row_index - 1) * CELL_SIZE_PX ) ,
                                (CELL_SIZE_PX, CELL_SIZE_PX) )

        # highlight cell being populated if animated
        if cell_drawtime_ms > 0.0:
            pygame.draw.rect(canvas, "green", cell_rect, 0)
            pygame.display.update()
            sleep(cell_drawtime_ms / 1000.0)

        # draw filled rectangle
        pygame.draw.rect(canvas,
                         color,
                         cell_rect)

        # draw cell outline (effectively creates gridlines)
        pygame.draw.rect(canvas, "teal", cell_rect, 1)
        if cell_drawtime_ms > 0.0:
            pygame.display.update()

# generate a new cell population from a previous populatio
# according to Rule 110
#   cells: row of cells
#   returns: next generation of cells
def rule110(cells: list[bool]) -> list[bool]:
    # next generation of cells
    cells_next = [False] * CELLS_PER_ROW

    # for each cell, apply Rule 110 and store in next generation
    for cell_index in range(len(cells)):
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

# cycle the next generation of cells and draw to the canvas
#
# this method implements a circular queue in the grid. Once
# the grid is full, the oldest generation is discarded and the
# next generation is pushed to the top of the grid
#
#   canvas: canvas on which to draw
#   grid: 2D array of cells
#   generation: current generation count
#   returns: 2D array of cells containing next generation
def cycle(canvas: pygame.Surface,
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
        grid_draw(canvas, grid)

    # calcuate next generation
    grid[row_next_index] = rule110(cells)
    grid_draw_row(canvas,
                  row_next_index,
                  grid[row_next_index],
                  CELL_DRAWTIME_MS)

    # udpate display
    pygame.display.update()

    return grid

###################
# main application
###################

# main application loop
def main():
    # intial population with pattern [0, 0, 1, 0, 0, 1, ...]
    seed_cells = [False] * CELLS_PER_ROW
    for cellindex in range(len(seed_cells)):
        if cellindex % 3 == 2:
            seed_cells[cellindex] = True
    grid = grid_init(seed_cells)

    # initialize display
    pygame.display.set_caption("Rule 110")
    canvas = canvas_init()
    grid_draw(canvas, grid)
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

        # cycle the next generation
        if next_generation:
            grid = cycle(canvas, grid, generation)
            generation = generation + 1
            if ROW_DRAWTIME_MS > 0.0:
                sleep(ROW_DRAWTIME_MS / 1000.0)

        # delay to allow user input to be captured
        sleep(EVENT_LOOP_MS / 1000.0)
    
    print("game complete")

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()