# Assignment 2: Pathfinding Visualization informed search algorithms (GBFS and A*) with dynamic obstacle handling and real-time replanning.

A visual pathfinding application that demonstrates informed search algorithms (GBFS and A*) with dynamic obstacle handling and real-time replanning.

## Requirements

- Python 3.7 or higher
- Pygame library

## Installation

1. Make sure Python is installed on your system
2. Install the required dependency:

## How to Run

Navigate to the project directory and run:

## Usage Instructions

### Setup Screen
When you launch the application, you'll see a configuration screen where you can set:
- **Grid Rows**: Number of rows (5-30)
- **Grid Columns**: Number of columns (5-30)
- **Obstacle Density**: Percentage of cells that become walls (0-0.5)

Click **START** to begin.

### Main Interface

#### Algorithm Selection
- **GBFS** (Greedy Best-First Search): Uses only heuristic to guide search. Faster but may not find optimal path.
- **A***: Uses both path cost and heuristic. Guarantees optimal path if heuristic is admissible.

#### Heuristic Selection
- **Manhattan**: Sum of horizontal and vertical distances. Better for grid-based movement.
- **Euclidean**: Straight-line distance. More accurate but slightly slower.

#### Controls
- **Run**: Start the pathfinding visualization
- **Reset**: Clear the grid (removes all walls)
- **Generate Map**: Create a new random maze
- **Dynamic: ON/OFF**: Toggle dynamic obstacle spawning

#### Interactive Features
- Click on empty cells to add walls
- Click on walls to remove them
- Watch the algorithm explore in real-time

### Dynamic Mode
When enabled, obstacles randomly appear while the agent moves along the path. If an obstacle blocks the current path, the agent automatically replans from its current position.

## Algorithms Explained

### Greedy Best-First Search (GBFS)
- **Evaluation Function**: f(n) = h(n)
- Only considers the heuristic (estimated distance to goal)
- Fast but doesn't guarantee the shortest path
- May get stuck in dead ends

### A* Search
- **Evaluation Function**: f(n) = g(n) + h(n)
- g(n) = actual cost from start to current node
- h(n) = estimated cost from current node to goal
- Guarantees optimal path when heuristic is admissible
- More nodes explored but always finds shortest path

### Heuristic Functions

**Manhattan Distance**:
Best for grids where only 4-directional movement is allowed.

h(n) = |x1 - x2| + |y1 - y2|

**Euclidean Distance**:
Straight-line distance, useful when diagonal movement is considered.

h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)

## Visual Legend

| Color | Meaning |
|-------|---------|
| Green | Start position |
| Red | Goal position |
| Dark Gray | Wall/Obstacle |
| Yellow | Frontier (nodes to explore) |
| Blue | Visited nodes |
| Light Green | Final path |
| Orange | Agent position (dynamic mode) |

## Metrics Displayed

- **Visited**: Total number of nodes expanded during search
- **Cost**: Length of the final path
- **Time**: Execution time in milliseconds

## Troubleshooting

**"No module named pygame"**: Run `pip install pygame`

**Window too small**: Reduce grid size in the setup screen

**No path found**: The goal might be completely blocked by walls. Click Reset or Generate Map.

## Author

Student ID: 23F-0559