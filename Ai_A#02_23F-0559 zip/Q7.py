import pygame
import heapq
import math
import time
import sys
import random

# ============================================
# GRID AND WINDOW CONFIGURATION
# ============================================
# These get updated based on user input at startup
rows, cols = 8, 8          # default grid dimensions
cell = 60                   # pixel size of each grid cell
panel_w = 280               # width of the control panel on the right side
win_w = cols * cell + panel_w   # total window width
win_h = rows * cell             # total window height
fps = 30                    # frames per second for smooth animation
step_delay = 80             # milliseconds between each search step (controls animation speed)

# ============================================
# COLOR DEFINITIONS (RGB tuples)
# ============================================
# I picked these colors to make the visualization easy to read
white = (255, 255, 255)
black = (30, 30, 30)
gray = (180, 180, 180)
start_c = (50, 200, 80)     # green - marks where the agent starts
goal_c = (220, 50, 50)      # red - marks the destination
wall_c = (40, 40, 40)       # dark gray - obstacles that block movement
front_c = (255, 220, 0)     # yellow - cells waiting to be explored (frontier)
visit_c = (100, 149, 237)   # blue - cells that have been visited already
path_c = (50, 220, 130)     # bright green - the final path from start to goal
panel_c = (25, 25, 40)      # dark blue - background for the side panel
btn_c = (60, 80, 140)       # normal button color
btn_h = (90, 120, 200)      # button color when mouse hovers over it
btn_act = (40, 180, 100)    # button color when it's active/selected
text_c = (230, 230, 230)    # light gray for regular text
title_c = (180, 210, 255)   # light blue for titles and headers
agent_c = (255, 100, 0)     # orange - shows current agent position during dynamic mode
error_c = (255, 80, 80)     # red for error messages

# ============================================
# CELL TYPE CONSTANTS
# ============================================
# These numbers represent what each cell in the grid contains
empty, wall, start, goal = 0, 1, 2, 3

# Global variables to track start and goal positions
# They get updated when we create a new grid
start_pos = (1, 1)
goal_pos = (6, 6)

# Movement directions - up, down, left, right
# Each tuple is (row_change, column_change)
moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def get_user_config():
    """
    Shows a setup screen where the user can configure:
    - Grid size (rows and columns)
    - Obstacle density (what percentage of cells become walls)
    
    Returns the validated values as a tuple (rows, cols, density)
    The user can't proceed until they enter valid numbers.
    """
    pygame.init()
    screen = pygame.display.set_mode((400, 320))
    pygame.display.set_caption("Pathfinding Setup")
    font = pygame.font.SysFont("segoeui", 20)
    sfont = pygame.font.SysFont("segoeui", 14)
    
    # Dictionary holding info about each input field
    # Each field has: current value, rectangle for drawing, and label text
    inputs = {
        'rows': {'value': '10', 'rect': pygame.Rect(180, 60, 160, 35), 'label': 'Rows (5-30):'},
        'cols': {'value': '10', 'rect': pygame.Rect(180, 110, 160, 35), 'label': 'Columns (5-30):'},
        'density': {'value': '0.25', 'rect': pygame.Rect(180, 160, 160, 35), 'label': 'Density (0-0.5):'}
    }
    
    active = None  # which input field is currently selected (if any)
    start_btn = pygame.Rect(100, 250, 200, 45)
    error_msg = ""  # shows validation errors to the user
    
    # Main loop for the config screen
    while True:
        screen.fill((30, 30, 45))
        title = font.render("Dynamic Pathfinding Setup", True, title_c)
        screen.blit(title, (70, 15))
        
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if user clicked on any input field
                active = None
                for key, inp in inputs.items():
                    if inp['rect'].collidepoint(event.pos):
                        active = key
                
                # Handle START button click - validate all inputs
                if start_btn.collidepoint(event.pos):
                    error_msg = ""
                    try:
                        r = int(inputs['rows']['value'])
                        c = int(inputs['cols']['value'])
                        d = float(inputs['density']['value'])
                        
                        # Check if values are within acceptable ranges
                        if r < 5 or r > 30:
                            error_msg = "Rows must be 5-30!"
                        elif c < 5 or c > 30:
                            error_msg = "Columns must be 5-30!"
                        elif d < 0.0 or d > 0.5:
                            error_msg = "Density must be 0-0.5!"
                        else:
                            # All good! Close this screen and return values
                            pygame.quit()
                            return r, c, d
                    except ValueError:
                        error_msg = "Invalid number!"
            
            # Handle keyboard input for the active text field
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_BACKSPACE:
                    # Delete last character
                    inputs[active]['value'] = inputs[active]['value'][:-1]
                elif event.key == pygame.K_RETURN:
                    # Deselect the field
                    active = None
                elif len(inputs[active]['value']) < 6:
                    # Only allow digits and decimal point
                    ch = event.unicode
                    if ch.isdigit() or ch == '.':
                        inputs[active]['value'] += ch
        
        # Draw all the input fields
        for key, inp in inputs.items():
            lbl = sfont.render(inp['label'], True, gray)
            screen.blit(lbl, (30, inp['rect'].y + 8))
            # Highlight the active field
            color = btn_act if active == key else btn_c
            pygame.draw.rect(screen, color, inp['rect'], border_radius=5)
            pygame.draw.rect(screen, gray, inp['rect'], 2, border_radius=5)
            txt = sfont.render(inp['value'], True, white)
            screen.blit(txt, (inp['rect'].x + 10, inp['rect'].y + 8))
        
        # Show error message if there is one
        if error_msg:
            err = sfont.render(error_msg, True, error_c)
            screen.blit(err, (120, 210))
        
        # Draw the START button with hover effect
        btn_color = btn_h if start_btn.collidepoint(mx, my) else btn_c
        pygame.draw.rect(screen, btn_color, start_btn, border_radius=8)
        pygame.draw.rect(screen, gray, start_btn, 2, border_radius=8)
        btn_txt = font.render("START", True, white)
        screen.blit(btn_txt, btn_txt.get_rect(center=start_btn.center))
        
        pygame.display.flip()


def mk_grid(r, c, density, randomize=True):
    """
    Creates a new grid with the given dimensions.
    
    Parameters:
    - r: number of rows
    - c: number of columns  
    - density: probability (0-1) that each empty cell becomes a wall
    - randomize: if True, add random walls; if False, create empty grid
    
    The start position is always at (1,1) and goal is near the bottom-right.
    We leave some space around start and goal so they're not blocked by walls.
    """
    global start_pos, goal_pos
    
    # Create empty grid filled with zeros
    g = [[empty] * c for _ in range(r)]
    
    # Place start and goal
    start_pos = (1, 1)
    goal_pos = (r - 2, c - 2)
    g[start_pos[0]][start_pos[1]] = start
    g[goal_pos[0]][goal_pos[1]] = goal
    
    # Add random obstacles if requested
    if randomize:
        for row in range(r):
            for col in range(c):
                if g[row][col] == empty:
                    # Don't put walls right next to start or goal
                    # This ensures there's always a way to begin moving
                    if abs(row - start_pos[0]) <= 1 and abs(col - start_pos[1]) <= 1:
                        continue
                    if abs(row - goal_pos[0]) <= 1 and abs(col - goal_pos[1]) <= 1:
                        continue
                    # Random chance to become a wall
                    if random.random() < density:
                        g[row][col] = wall
    return g


def nbrs(pos, g, r, c):
    """
    Get all valid neighboring cells that the agent can move to.
    
    A neighbor is valid if:
    - It's within grid bounds
    - It's not a wall
    
    Returns a list of (row, col) tuples for valid neighbors.
    """
    row, col = pos
    res = []
    for dr, dc in moves:
        nr, nc = row + dr, col + dc
        if 0 <= nr < r and 0 <= nc < c and g[nr][nc] != wall:
            res.append((nr, nc))
    return res


def h_man(a, b):
    """
    Manhattan distance heuristic.
    This is the "taxicab" distance - how many steps if you can only
    move horizontally or vertically (no diagonals).
    Good for grid-based pathfinding where diagonal movement isn't allowed.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h_euc(a, b):
    """
    Euclidean distance heuristic.
    This is the straight-line distance between two points.
    More accurate but slightly slower to compute than Manhattan.
    """
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def search(g, st, gl, h, r, c, use_astar):
    """
    Unified search function that can do either GBFS or A* search.
    This is a generator that yields the search state at each step,
    allowing us to visualize the algorithm as it runs.
    
    Parameters:
    - g: the grid (2D list)
    - st: start position tuple
    - gl: goal position tuple
    - h: heuristic function to use
    - r, c: grid dimensions
    - use_astar: if True, use A* (considers path cost); if False, use GBFS
    
    Yields tuples containing:
    - status: 'visit', 'frontier', or 'done'
    - visited set
    - frontier set (nodes waiting to be explored)
    - path (only when done)
    - nodes visited count
    - path cost
    - elapsed time in ms
    """
    # Priority queue: (priority, tiebreaker, position)
    # The tiebreaker ensures consistent ordering when priorities are equal
    open_set = [(h(st, gl), 0, st)]
    cnt = 1  # counter for tiebreaking
    
    came = {st: None}  # tracks parent of each node for path reconstruction
    g_score = {st: 0}  # cost to reach each node from start (used by A*)
    vis = set()        # nodes we've already fully explored
    num_vis = 0        # counter for visited nodes
    t0 = time.time()   # start timing

    while open_set:
        # Get the node with lowest priority (best according to heuristic)
        _, _, cur = heapq.heappop(open_set)
        
        # Skip if we already processed this node
        if cur in vis:
            continue
            
        vis.add(cur)
        num_vis += 1
        
        # Let the visualization show this step
        yield ('visit', vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)

        # Check if we reached the goal
        if cur == gl:
            # Reconstruct path by following parent pointers backwards
            pth = []
            node = gl
            while node:
                pth.append(node)
                node = came[node]
            pth.reverse()  # flip it so it goes start -> goal
            
            # Cost calculation differs between algorithms
            cst = g_score[gl] if use_astar else len(pth) - 1
            yield ('done', vis, set(), pth, num_vis, cst, (time.time() - t0) * 1000)
            return

        # Explore all valid neighbors
        for nb in nbrs(cur, g, r, c):
            if use_astar:
                # A* considers actual cost to reach neighbor
                temp_g = g_score[cur] + 1
                if nb not in g_score or temp_g < g_score[nb]:
                    g_score[nb] = temp_g
                    came[nb] = cur
                    # Priority = actual cost + estimated remaining cost
                    heapq.heappush(open_set, (temp_g + h(nb, gl), cnt, nb))
                    cnt += 1
            else:
                # GBFS only looks at heuristic, ignores path cost
                if nb not in vis and nb not in came:
                    came[nb] = cur
                    heapq.heappush(open_set, (h(nb, gl), cnt, nb))
                    cnt += 1
        
        # Show the current frontier state
        yield ('frontier', vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)

    # If we get here, there's no path to the goal
    yield ('done', vis, set(), None, num_vis, 0, (time.time() - t0) * 1000)


def spawn_obstacle(g, pth_set, agent_pos, r, c):
    """
    Randomly spawns a new obstacle during dynamic mode.
    This simulates real-world scenarios where the environment changes
    while the agent is moving.
    
    Returns True if the new obstacle blocks the current path,
    which means we need to replan.
    
    The 8% spawn chance and 15 attempts are tuned to create
    interesting scenarios without making it impossible to reach the goal.
    """
    # Only spawn with 8% probability each call
    if random.random() >= 0.08:
        return False
    
    # Try up to 15 times to find a valid spot for the obstacle
    for _ in range(15):
        rr, cc = random.randint(0, r - 1), random.randint(0, c - 1)
        # Don't block start, goal, or current agent position
        if g[rr][cc] == empty and (rr, cc) != start_pos and (rr, cc) != goal_pos and (rr, cc) != agent_pos:
            g[rr][cc] = wall
            # Return True if this obstacle is on the planned path
            return (rr, cc) in pth_set
    return False


def btn(surf, rect, txt, fnt, act=False, hvr=False):
    """
    Helper function to draw a button with text.
    Handles different visual states:
    - act=True: button is currently active/selected (green)
    - hvr=True: mouse is hovering over button (lighter blue)
    - default: normal button color
    """
    clr = btn_act if act else (btn_h if hvr else btn_c)
    pygame.draw.rect(surf, clr, rect, border_radius=6)
    pygame.draw.rect(surf, gray, rect, 1, border_radius=6)
    lbl = fnt.render(txt, True, white)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


def draw_grid(surf, g, vis, fron, pth, agent_pos, r, c, csz):
    """
    Draws the main grid area showing:
    - Walls, start, goal positions
    - Visited cells (blue)
    - Frontier cells (yellow) 
    - Final path (green)
    - Current agent position in dynamic mode (orange)
    
    The order of if/elif matters here - we want agent to show on top of path,
    path on top of visited, etc.
    """
    for row in range(r):
        for col in range(c):
            x, y = col * csz, row * csz
            ct = g[row][col]
            
            # Determine what color this cell should be
            # Priority: agent > wall > start > goal > path > visited > frontier > empty
            if (row, col) == agent_pos and agent_pos != start_pos:
                clr = agent_c
            elif ct == wall:
                clr = wall_c
            elif ct == start:
                clr = start_c
            elif ct == goal:
                clr = goal_c
            elif pth and (row, col) in pth:
                clr = path_c
            elif (row, col) in vis:
                clr = visit_c
            elif (row, col) in fron:
                clr = front_c
            else:
                clr = white
            
            # Draw cell with small gap for grid lines
            pygame.draw.rect(surf, clr, (x + 1, y + 1, csz - 2, csz - 2), border_radius=3)
    
    # Draw the grid lines
    for row in range(r + 1):
        pygame.draw.line(surf, gray, (0, row * csz), (c * csz, row * csz))
    for col in range(c + 1):
        pygame.draw.line(surf, gray, (col * csz, 0), (col * csz, r * csz))


def draw_panel(surf, fm, fs, rects, hov, a_idx, h_idx, st, num_vis, path_cst, elapsed, dyn_mode, r, c, density):
    """
    Draws the control panel on the right side of the window.
    Contains:
    - Algorithm selection buttons (GBFS / A*)
    - Heuristic selection buttons (Manhattan / Euclidean)
    - Run and Reset buttons
    - Dynamic mode toggle
    - Generate Map button
    - Metrics display (visited nodes, path cost, time)
    - Color legend
    - Current status
    """
    px = c * cell  # x position where panel starts
    
    # Panel background
    pygame.draw.rect(surf, panel_c, (px, 0, panel_w, win_h))
    pygame.draw.line(surf, gray, (px, 0), (px, win_h), 2)

    # Title and grid info
    surf.blit(fm.render("Dynamic Pathfinding", True, title_c), (px + 8, 8))
    surf.blit(fs.render("Grid: %dx%d  Density: %.0f%%" % (r, c, density * 100), True, gray), (px + 8, 32))

    # Algorithm selection section
    y = 55
    surf.blit(fs.render("Algorithm", True, gray), (px + 8, y))
    for i, (lbl, rect) in enumerate(zip(["GBFS", "A*"], rects['algo'])):
        btn(surf, rect, lbl, fs, act=(i == a_idx), hvr=(hov == ('algo', i)))

    # Heuristic selection section
    y = rects['algo'][0].bottom + 6
    surf.blit(fs.render("Heuristic", True, gray), (px + 8, y))
    for i, (lbl, rect) in enumerate(zip(["Manhat", "Euclid"], rects['heur'])):
        btn(surf, rect, lbl, fs, act=(i == h_idx), hvr=(hov == ('heur', i)))

    # Control buttons
    btn(surf, rects['run'], "Run", fs, hvr=(hov == ('ctrl', 'run')))
    btn(surf, rects['reset'], "Reset", fs, hvr=(hov == ('ctrl', 'reset')))
    
    # Dynamic mode shows ON/OFF state
    dyn_txt = "Dynamic: ON" if dyn_mode else "Dynamic: OFF"
    btn(surf, rects['dynamic'], dyn_txt, fs, act=dyn_mode, hvr=(hov == ('ctrl', 'dynamic')))
    btn(surf, rects['generate'], "Generate Map", fs, hvr=(hov == ('ctrl', 'generate')))

    # Metrics section - shows algorithm performance
    y = rects['generate'].bottom + 12
    surf.blit(fs.render("Metrics", True, gray), (px + 8, y))
    y += 18
    surf.blit(fs.render("Visited: %d" % num_vis, True, text_c), (px + 10, y))
    y += 16
    surf.blit(fs.render("Cost: %s" % (str(path_cst) if path_cst else "-"), True, text_c), (px + 10, y))
    y += 16
    surf.blit(fs.render("Time: %s ms" % ("%.2f" % elapsed if elapsed else "-"), True, text_c), (px + 10, y))

    # Legend section - explains what each color means
    y += 22
    surf.blit(fs.render("Legend", True, gray), (px + 8, y))
    y += 18
    for clr, lbl in [(start_c, "Start"), (goal_c, "Goal"), (wall_c, "Wall"), (front_c, "Frontier"), (visit_c, "Visited"), (path_c, "Path"), (agent_c, "Agent")]:
        pygame.draw.rect(surf, clr, (px + 10, y + 1, 12, 12), border_radius=2)
        surf.blit(fs.render(lbl, True, text_c), (px + 26, y - 1))
        y += 15

    # Current status display
    y += 8
    st_map = {'idle': 'Idle', 'running': 'Running', 'done': 'Done', 'no_path': 'No Path', 'replanning': 'Replanning'}
    surf.blit(fs.render("Status: %s" % st_map.get(st, st), True, title_c), (px + 8, y))


def run():
    """
    Main application function - sets everything up and runs the game loop.
    
    This handles:
    1. Getting user configuration
    2. Setting up pygame window and fonts
    3. Creating button rectangles
    4. Running the main loop that:
       - Handles all user input (clicks, keys)
       - Updates search visualization
       - Handles dynamic obstacle spawning
       - Renders everything each frame
    """
    global rows, cols, cell, win_w, win_h
    
    # Get grid size and density from user
    rows, cols, density = get_user_config()
    
    # Calculate cell size to fit nicely on screen
    # Smaller cells for larger grids so it doesn't get too big
    cell = min(50, 600 // max(rows, cols))
    win_w = cols * cell + panel_w
    win_h = max(rows * cell, 480)  # minimum height so panel fits
    
    pygame.init()
    surf = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Dynamic Pathfinding Agent")
    clk = pygame.time.Clock()

    # Fonts for different text sizes
    fm = pygame.font.SysFont("segoeui", 14, bold=True)  # medium, for buttons
    fs = pygame.font.SysFont("segoeui", 12)              # small, for labels

    # Calculate button positions based on panel location
    px = cols * cell
    bw, bh = 120, 24  # button width and height
    bx = px + 8       # x position for buttons
    
    # Define all the clickable button rectangles
    rects = {
        'algo': [pygame.Rect(bx, 72, bw // 2 - 2, bh), pygame.Rect(bx + bw // 2 + 2, 72, bw // 2 - 2, bh)],
        'heur': [pygame.Rect(bx, 118, bw // 2 - 2, bh), pygame.Rect(bx + bw // 2 + 2, 118, bw // 2 - 2, bh)],
        'run': pygame.Rect(bx, 152, bw // 2 - 2, bh),
        'reset': pygame.Rect(bx + bw // 2 + 2, 152, bw // 2 - 2, bh),
        'dynamic': pygame.Rect(bx, 182, bw, bh),
        'generate': pygame.Rect(bx, 212, bw, bh),
    }

    # Create initial grid with random obstacles
    g = mk_grid(rows, cols, density)
    
    # State variables
    a_idx, h_idx = 0, 0  # selected algorithm (0=GBFS, 1=A*) and heuristic (0=Manhattan, 1=Euclidean)
    vis, fron, pth, pth_set = set(), set(), [], set()  # visualization state
    num_vis, path_cst, elapsed = 0, 0, 0.0  # metrics
    st, gen, last, hov = 'idle', None, 0, None  # status, generator, last update time, hover state
    dyn_mode = False  # whether dynamic obstacles are enabled
    agent_pos, path_idx = start_pos, 0  # agent position for dynamic mode

    # Main game loop
    running = True
    while running:
        now = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()

        # Figure out what button (if any) the mouse is hovering over
        hov = None
        for i, r in enumerate(rects['algo']):
            if r.collidepoint(mx, my): hov = ('algo', i)
        for i, r in enumerate(rects['heur']):
            if r.collidepoint(mx, my): hov = ('heur', i)
        if rects['run'].collidepoint(mx, my): hov = ('ctrl', 'run')
        if rects['reset'].collidepoint(mx, my): hov = ('ctrl', 'reset')
        if rects['dynamic'].collidepoint(mx, my): hov = ('ctrl', 'dynamic')
        if rects['generate'].collidepoint(mx, my): hov = ('ctrl', 'generate')

        # Process all pending events
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            if evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
                running = False

            if evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
                # Check algorithm button clicks
                for i, r in enumerate(rects['algo']):
                    if r.collidepoint(mx, my):
                        a_idx = i
                        # Reset visualization state when changing algorithm
                        st, gen = 'idle', None
                        vis, fron, pth, pth_set = set(), set(), [], set()
                        num_vis, path_cst, elapsed = 0, 0, 0.0
                        agent_pos, path_idx = start_pos, 0

                # Check heuristic button clicks
                for i, r in enumerate(rects['heur']):
                    if r.collidepoint(mx, my):
                        h_idx = i
                        st, gen = 'idle', None
                        vis, fron, pth, pth_set = set(), set(), [], set()
                        num_vis, path_cst, elapsed = 0, 0, 0.0
                        agent_pos, path_idx = start_pos, 0

                # Run button - start the search
                if rects['run'].collidepoint(mx, my) and st in ('idle', 'done', 'no_path'):
                    vis, fron, pth, pth_set = set(), set(), [], set()
                    num_vis, path_cst, elapsed = 0, 0, 0.0
                    agent_pos, path_idx = start_pos, 0
                    h_fn = h_man if h_idx == 0 else h_euc
                    gen = search(g, start_pos, goal_pos, h_fn, rows, cols, a_idx == 1)
                    st = 'running'

                # Reset button - clear the grid (keeps walls user placed)
                if rects['reset'].collidepoint(mx, my):
                    g = mk_grid(rows, cols, density, False)  # empty grid, no random walls
                    vis, fron, pth, pth_set = set(), set(), [], set()
                    num_vis, path_cst, elapsed = 0, 0, 0.0
                    st, gen = 'idle', None
                    agent_pos, path_idx = start_pos, 0

                # Toggle dynamic mode
                if rects['dynamic'].collidepoint(mx, my):
                    dyn_mode = not dyn_mode

                # Generate new random map
                if rects['generate'].collidepoint(mx, my):
                    g = mk_grid(rows, cols, density)
                    vis, fron, pth, pth_set = set(), set(), [], set()
                    num_vis, path_cst, elapsed = 0, 0, 0.0
                    st, gen = 'idle', None
                    agent_pos, path_idx = start_pos, 0

                # Click on grid to toggle walls (only when idle)
                if mx < cols * cell and st == 'idle':
                    cr, cc = my // cell, mx // cell
                    if 0 <= cr < rows and 0 <= cc < cols:
                        if g[cr][cc] == empty:
                            g[cr][cc] = wall
                        elif g[cr][cc] == wall:
                            g[cr][cc] = empty

        # Dynamic mode: move agent along path and spawn obstacles
        if st == 'done' and dyn_mode and pth and path_idx < len(pth) - 1:
            if (now - last) >= 150:  # move every 150ms
                last = now
                path_idx += 1
                if path_idx < len(pth):
                    agent_pos = pth[path_idx]
                # Try to spawn obstacle, replan if it blocks our path
                if spawn_obstacle(g, pth_set, agent_pos, rows, cols):
                    st = 'replanning'
                    h_fn = h_man if h_idx == 0 else h_euc
                    gen = search(g, agent_pos, goal_pos, h_fn, rows, cols, a_idx == 1)
                    pth, pth_set, fron = [], set(), set()

        # Advance the search visualization one step at a time
        if st in ('running', 'replanning') and gen and (now - last) >= step_delay:
            last = now
            try:
                step = next(gen)
                kind, v, f, p, nv, pc, el = step
                vis, fron, num_vis = v, f, nv
                if kind == 'done':
                    elapsed = el
                    if p:
                        pth, pth_set, path_cst = p, set(p), pc
                        st, path_idx = 'done', 0
                        agent_pos = pth[0] if pth else start_pos
                    else:
                        st = 'no_path'
                    gen = None
            except StopIteration:
                st = 'done' if pth else 'no_path'
                gen = None

        # Draw everything
        surf.fill(black)
        draw_grid(surf, g, vis, fron, pth_set, agent_pos, rows, cols, cell)
        draw_panel(surf, fm, fs, rects, hov, a_idx, h_idx, st, num_vis, path_cst, elapsed, dyn_mode, rows, cols, density)
        pygame.display.flip()
        clk.tick(fps)

    pygame.quit()
    sys.exit()


# Entry point - only runs if this file is executed directly
if __name__ == "__main__":
    run()