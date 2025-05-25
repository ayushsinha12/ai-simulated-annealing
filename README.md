# AI-Simulated-Annealing

A Python-based simulated annealing solver that colors a grid so that no two adjacent blocks share the same color, while also minimizing the number of colors and shapes used.

## Project Overview

This project was developed for an AI course assignment focused on solving a variation of the graph coloring problem using **local search**. The goal is to build an autonomous agent that fills an `n × n` grid by placing shapes of various sizes and colors such that:

- **Adjacent cells do not share the same color** (edge-adjacent only).
- **The total number of distinct shapes and colors used is minimized.**

To achieve this, the agent uses **simulated annealing**—a stochastic optimization algorithm that allows for occasional uphill moves to escape local minima, improving the likelihood of reaching a globally valid and efficient solution.

## Environment and Constraints

The grid environment is provided via a PyGame interface with the following interaction model:

- The agent controls a **brush** that can:
  - Move around the grid (`up`, `down`, `left`, `right`)
  - Place shapes of various types and colors
  - Switch between 9 brush shapes and 4 brush colors

- The environment is **read-only** except through the provided `execute()` function.

- Any shape placement that overlaps with already-filled cells **fails silently**.

All placements must be done using the allowed commands, and direct manipulation of the environment variables is forbidden to preserve encapsulation.

## Features

- Implements **simulated annealing**, a type of local search, to iteratively improve color placement.
- Supports **random restarts** to escape local optima and ensure convergence.
- Dynamically chooses from multiple shape and color combinations.
- Penalizes solutions with excessive shape count or invalid placements.
- Uses only the `execute()` API to comply with assignment constraints.

## Broader Applications

This problem is a variant of **graph coloring**, which has wide applications in:

- **Scheduling** (e.g., exams, classrooms, or aircraft maintenance)
- **Resource allocation** (e.g., frequency assignment, register allocation)
- **Network optimization** (e.g., wireless channel assignment, sensor networks)

## File Structure
```bash
├── hw1.py         # Main file containing the AI agent implementation
├── gridgame.py    # Environment and simulation logic (provided)
├── README.md      # Project documentation
```

## How to Run the Program

1. **Make sure you have Python installed**, along with the `pygame` library.
2. **Open a terminal** in the project root directory.
3. **Install** the required package using:
   - `pip install pygame`
4. **Run** the main program file:
   - `python hw1.py`
5. **During execution**, the agent will:
   - Navigate the grid with shape and color changes
   - Place shapes using local search
   - Attempt to minimize conflicts, shape usage, and color usage

