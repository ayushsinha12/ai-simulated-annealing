import time
import random
import math
import numpy as np
from typing import Tuple
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# You can turn the GUI feature to false if you would quickly like to see it work in the terminal

##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.5, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

#shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

#Initial State in terminal
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# code for filling the grid is below
##########################################

# finds the energy for a certain state of the game
def compute_energy(grid, place_shapes):
    grid_size = grid.shape[0]
    conflicts = 0
    energy = 0

    # finds all conflicts below and dosn't double count by checking only down and to the right
    for i in range(grid_size):
        for j in range(grid_size):
            color = grid[i, j]
            if color == -1:
                continue
            if i + 1 < grid_size and grid[i + 1, j] == color:
                conflicts += 1
            if j + 1 < grid_size and grid[i, j + 1] == color:
                conflicts += 1
    # 5000 point penalty if there is any conflicts
    if conflicts > 0:
        energy += 5000
    
    # 1 point penalty for each of the unfilled cells
    filled_cells = np.count_nonzero(grid >= 0)
    empties_penalty = (grid_size ** 2 - filled_cells)
    energy += empties_penalty

    # 10 point penalty for the amount of shapes placed
    shape_penalty = len(place_shapes)
    energy += 10*shape_penalty

    # 5 point penalty for every color used
    distinct_colors = {color for (_, _, color) in place_shapes}
    color_penalty = 5 * len(distinct_colors)
    energy += color_penalty

    return energy

# Helper method that moves the brush
def move_brush(game, tx, ty):
    # Reads the brush’s current (x,y), then issues up/down/left/right
    (x, y), _, _, _, _, _ = game.execute("export")
    while x < tx:
        game.execute("right"); x += 1
    while x > tx:
        game.execute("left");  x -= 1
    while y < ty:
        game.execute("down");  y += 1
    while y > ty:
        game.execute("up");    y -= 1

# Helper method that sets the shape for me
def set_shape(game, target):
    # Cycles through shapes until you hit the target index
    for _ in range(len(game.shapes)):
        _, shape_idx, _, _, _, _ = game.execute("export")
        if shape_idx == target:
            return
        game.execute("switchshape")

# Helper method that sets the color for me
def set_color(game, target):
    # Cycles colors until you hit the target index
    for _ in range(len(game.colors)):
        _, _, color_idx, _, _, _ = game.execute("export")
        if color_idx == target:
            return
        game.execute("switchcolor")

# Checks if a placed shape and color causes a color conflict
def no_color_conflict(grid: np.ndarray,
                      shape: np.ndarray,
                      pos: Tuple[int,int],
                      color_idx: int) -> bool:
    """
    Return True if stamping `shape` at column/row pos=(c,r)
    with color `color_idx` would not put two same‐colored
    cells edge‐adjacent to one another.
    """
    n = grid.shape[0]
    c0, r0 = pos

    # for every block in the shape
    for i in range(shape.shape[0]):
        for j in range(shape.shape[1]):
            if shape[i, j]:
                r, c = r0 + i, c0 + j

                # check each of the four neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < n and 0 <= cc < n:
                        if grid[rr, cc] == color_idx:
                            return False
    return True

# finds a neighbor
def generate_neighbor(game, max_tries: int = 50):
     # gets current state of the grid
    _, _, _, grid, placed, _ = game.execute("export")
    n = grid.shape[0]

    # gets all the empty cells on the grid
    empties = [(r, c) for r in range(n) for c in range(n) if grid[r, c] < 0]
    if not empties:
        return None

    
    # i is an unused variable
    for i in range(max_tries):
        # pick random empty
        r, c = random.choice(empties)
        # pick random shape and color
        shape_idx = random.randrange(len(game.shapes))
        color_idx = random.randrange(len(game.colors))
        shape = game.shapes[shape_idx]

        # move brush & set shape/color
        move_brush(game, c, r)
        set_shape(game, shape_idx)
        set_color(game, color_idx)

        # checks and places shape if it is possible
        if (game.canPlace(grid, game.shapes[shape_idx], (c, r))
            and no_color_conflict(grid, shape, (c, r), color_idx)):
            game.execute("place")
            return (shape_idx, (r, c), color_idx)

    # returns nothing if no valid neighbor is found
    return None

       
# the main local seatch functiom
def simulated_annealing(game, temp = 500.0, cooling_rate = 0.995, max_steps = 5000):
    _, _, _, grid, placed, _ = game.execute("export")
    curr_energy = compute_energy(grid, placed)
    best_energy = curr_energy
    best_record = placed.copy()
    T_min = 5.0

    for i in range(max_steps):

        _, _, _, _, _, done = game.execute("export")
        if done:
            print(f"Converged by validity at step {i}")
            break
        if temp < T_min:
            print(f"Converged by T_min={T_min} at step {i}")
            break

        neighbor = generate_neighbor(game)
        
        if neighbor is None:
            continue

        # updating after the move of the neighbor
        _, _, _, grid_n, placed_n, done_n = game.execute("export")

        neighbor_energy = compute_energy(grid_n, placed_n)
        delta = curr_energy - neighbor_energy
        if delta >= 0 or random.random() < math.exp(delta / temp):

            curr_energy = neighbor_energy
            if done_n and neighbor_energy < best_energy:
                best_energy = neighbor_energy
                best_record = placed_n.copy()
        else:
            game.execute("undo")
        
        #cooling
        #print(temp)
        temp *= cooling_rate

    """
    while True:
        _, _, _, _, placed_now, _ = game.execute("export")
        if not placed_now:
            break
        game.execute("undo")
    # Place best_record
    for shape_idx, (r, c), color_idx in best_record:
        move_brush(game, c, r)
        set_shape(game, shape_idx)
        set_color(game, color_idx)
        game.execute("place")
    """

#simulated_annealing(game)
#shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

#Prints result in terminal
print("▶ Starting Annealing")
simulated_annealing(game)
print("▶ Annealing complete, final export:")
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = \
game.execute("export")
print("Done?", done, "Shapes:", placedShapes)

########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
