# -*- coding: utf-8 -*-
import pygame
import heapq
import math
import time
import sys

# Grid and window settings
rows, cols = 8, 8
cell = 80  # px per cell
panel_w = 280  # right panel width
win_w = cols * cell + panel_w
win_h = rows * cell

fps = 30
step_delay = 120  # milliseconds between animation steps

# Color definitions for UI elements
white = (255, 255, 255)
black = (30, 30, 30)
gray = (180, 180, 180)
dkgray = (60, 60, 60)
start_c = (50, 200, 80)  # green for start node
goal_c = (220, 50, 50)  # red for goal node
wall_c = (40, 40, 40)  # dark gray for walls
front_c = (255, 220, 0)  # yellow for frontier nodes
visit_c = (100, 149, 237)  # blue for visited nodes
path_c = (50, 220, 130)  # green for final path
panel_c = (25, 25, 40)  # dark blue for side panel
btn_c = (60, 80, 140)  # normal button color
btn_h = (90, 120, 200)  # hover button color
btn_act = (40, 180, 100)  # active button color
text_c = (230, 230, 230)  # light gray for text
title_c = (180, 210, 255)  # light blue for titles

# Cell type identifiers used in grid array
empty, wall, start, goal = 0, 1, 2, 3

def mk_grid():
    """
    Creates initial grid with walls and start/goal positions
    Returns 2D list representing game board
    """
    try:
        # Initialize empty grid
        g = [[empty] * cols for _ in range(rows)]
        
        # Add vertical walls at specific positions
        for i in range(2, 6):
            g[i][3] = wall
            g[i][5] = wall
        
        # Add horizontal walls to create maze
        for j in range(1, 4):
            g[4][j] = wall
        for j in range(4, 7):
            g[6][j] = wall
        
        # Set start and goal positions
        g[1][1] = start
        g[6][6] = goal
        return g
    except Exception as e:
        print(f"error creating grid: {e}")
        sys.exit(1)

# Starting position coordinates
start_pos = (1, 1)
# Goal position coordinates
goal_pos = (6, 6)

# Movement directions: up, down, left, right
moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def nbrs(pos, g):
    """
    Finds valid neighbor cells for given position
    pos: current position tuple (row, col)
    g: grid array
    Returns list of valid neighbor positions
    """
    try:
        r, c = pos
        res = []
        # Check all 4 directions
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            # Verify position is within bounds and not a wall
            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != wall:
                res.append((nr, nc))
        return res
    except Exception as e:
        print(f"error finding neighbors: {e}")
        return []

def h_man(a, b):
    """
    Manhattan distance heuristic function
    a: first position tuple
    b: second position tuple
    Returns Manhattan distance between two points
    """
    try:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    except Exception as e:
        print(f"error calculating manhattan: {e}")
        return 0

def h_euc(a, b):
    """
    Euclidean distance heuristic function
    a: first position tuple
    b: second position tuple
    Returns straight line distance between two points
    """
    try:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    except Exception as e:
        print(f"error calculating euclidean: {e}")
        return 0

def gbfs(g, st, gl, h):
    """
    Greedy Best First Search algorithm
    g: grid array
    st: start position
    gl: goal position
    h: heuristic function
    Generator yielding search progress at each step
    """
    try:
        # Priority queue with heuristic value and position
        open_set = [(h(st, gl), 0, st)]
        cnt = 1  # Counter for tie breaking in heap
        came = {st: None}  # Parent tracking for path reconstruction
        vis = set()  # Set of visited nodes
        num_vis = 0  # Count of nodes visited
        t0 = time.time()  # Start time for performance tracking

        while open_set:
            try:
                # Get node with lowest heuristic value
                _, _, cur = heapq.heappop(open_set)
                
                # Skip if already visited
                if cur in vis:
                    continue
                
                vis.add(cur)
                num_vis += 1
                
                # Yield current state for visualization
                yield ('visit', cur, vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)

                # Check if goal reached
                if cur == gl:
                    # Reconstruct path from goal to start
                    pth = []
                    node = gl
                    while node is not None:
                        pth.append(node)
                        node = came[node]
                    pth.reverse()
                    
                    cst = len(pth) - 1  # Path cost is num of steps
                    elapsed = (time.time() - t0) * 1000  # Convert to ms
                    yield ('done', None, vis, set(), pth, num_vis, cst, elapsed)
                    return

                # Explore neighbors
                for nb in nbrs(cur, g):
                    if nb not in vis and nb not in came:
                        came[nb] = cur
                        heapq.heappush(open_set, (h(nb, gl), cnt, nb))
                        cnt += 1
                
                # Yield frontier state
                yield ('frontier', cur, vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)
            
            except Exception as e:
                print(f"error in gbfs loop: {e}")
                break

        # No path found
        yield ('done', None, vis, set(), None, num_vis, 0, (time.time() - t0) * 1000)
    
    except Exception as e:
        print(f"error in gbfs: {e}")
        yield ('done', None, set(), set(), None, 0, 0, 0)

def astar(g, st, gl, h):
    """
    A star search algorithm
    g: grid array
    st: start position
    gl: goal position
    h: heuristic function
    Generator yielding search progress at each step
    """
    try:
        # Priority queue with f-score and position
        open_set = [(h(st, gl), 0, st)]
        cnt = 1  # Counter for tie breaking
        came = {st: None}  # Parent tracking
        g_score = {st: 0}  # Cost from start to each node
        vis = set()  # Visited nodes
        num_vis = 0  # Count of visited nodes
        t0 = time.time()  # Start time

        while open_set:
            try:
                # Get node with lowest f-score
                _, _, cur = heapq.heappop(open_set)
                
                # Skip if already visited
                if cur in vis:
                    continue
                
                vis.add(cur)
                num_vis += 1
                
                # Yield current state
                yield ('visit', cur, vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)

                # Check if goal reached
                if cur == gl:
                    # Reconstruct path
                    pth = []
                    node = gl
                    while node is not None:
                        pth.append(node)
                        node = came[node]
                    pth.reverse()
                    
                    cst = g_score[gl]  # Actual cost to goal
                    elapsed = (time.time() - t0) * 1000
                    yield ('done', None, vis, set(), pth, num_vis, round(cst, 2), elapsed)
                    return

                # Explore neighbors with g+h scoring
                for nb in nbrs(cur, g):
                    temp_g = g_score[cur] + 1
                    
                    # Update if better path found
                    if nb not in g_score or temp_g < g_score[nb]:
                        g_score[nb] = temp_g
                        f = temp_g + h(nb, gl)
                        came[nb] = cur
                        heapq.heappush(open_set, (f, cnt, nb))
                        cnt += 1
                
                # Yield frontier state
                yield ('frontier', cur, vis.copy(), set(n for _, _, n in open_set), None, num_vis, 0, 0)
            
            except Exception as e:
                print(f"error in astar loop: {e}")
                break

        # No path found
        yield ('done', None, vis, set(), None, num_vis, 0, (time.time() - t0) * 1000)
    
    except Exception as e:
        print(f"error in astar: {e}")
        yield ('done', None, set(), set(), None, 0, 0, 0)

def btn(surf, rect, txt, fnt, act=False, hvr=False):
    """
    Draws button on surface
    surf: pygame surface to draw on
    rect: button rectangle
    txt: button text label
    fnt: font object for text
    act: whether button is active
    hvr: whether mouse is hovering
    """
    try:
        # Choose color based on state
        clr = btn_act if act else (btn_h if hvr else btn_c)
        
        # Draw button background with rounded corners
        pygame.draw.rect(surf, clr, rect, border_radius=8)
        pygame.draw.rect(surf, gray, rect, 1, border_radius=8)
        
        # Render and center text
        lbl = fnt.render(txt, True, white)
        surf.blit(lbl, lbl.get_rect(center=rect.center))
    except Exception as e:
        print(f"error drawing button: {e}")

def draw_g(surf, g, vis, fron, pth):
    """
    Draws game grid with cells colored by state
    surf: pygame surface
    g: grid array
    vis: set of visited positions
    fron: set of frontier positions
    pth: set of path positions
    """
    try:
        # Draw each cell
        for r in range(rows):
            for c in range(cols):
                x, y = c * cell, r * cell
                cell_type = g[r][c]

                # Determine cell color based on state
                if cell_type == wall:
                    clr = wall_c
                elif cell_type == start:
                    clr = start_c
                elif cell_type == goal:
                    clr = goal_c
                elif pth and (r, c) in pth:
                    clr = path_c
                elif (r, c) in vis:
                    clr = visit_c
                elif (r, c) in fron:
                    clr = front_c
                else:
                    clr = white

                # Draw cell with small padding
                pygame.draw.rect(surf, clr, (x + 1, y + 1, cell - 2, cell - 2), border_radius=4)

        # Draw grid lines
        for r in range(rows + 1):
            pygame.draw.line(surf, gray, (0, r * cell), (cols * cell, r * cell))
        for c in range(cols + 1):
            pygame.draw.line(surf, gray, (c * cell, 0), (c * cell, rows * cell))
    except Exception as e:
        print(f"error drawing grid: {e}")

def draw_p(surf, fb, fm, fs, algo, heur, num, cst, elapsed, rects, hov, a_idx, h_idx, st):
    """
    Draws side panel with controls and info
    surf: pygame surface
    fb: big font
    fm: medium font
    fs: small font
    algo: algorithm index
    heur: heuristic index
    num: nodes visited count
    cst: path cost
    elapsed: time elapsed
    rects: button rectangles dict
    hov: hover state
    a_idx: active algorithm index
    h_idx: active heuristic index
    st: current state
    """
    try:
        px = cols * cell
        
        # Draw panel background
        pygame.draw.rect(surf, panel_c, (px, 0, panel_w, win_h))
        pygame.draw.line(surf, gray, (px, 0), (px, win_h), 2)

        # Draw title
        t = fb.render("search visualizer", True, title_c)
        surf.blit(t, (px + 10, 10))

        # Algorithm section
        y = 50
        surf.blit(fm.render("algorithm", True, gray), (px + 10, y))
        y += 24
        for i, (lbl, r) in enumerate(zip(["gbfs", "astar"], rects['algo'])):
            btn(surf, r, lbl, fm, act=(i == a_idx), hvr=(hov == ('algo', i)))
        y = rects['algo'][0].bottom + 10

        # Heuristic section
        surf.blit(fm.render("heuristic", True, gray), (px + 10, y))
        y += 24
        for i, (lbl, r) in enumerate(zip(["manhattan", "euclidean"], rects['heur'])):
            btn(surf, r, lbl, fm, act=(i == h_idx), hvr=(hov == ('heur', i)))
        y = rects['heur'][0].bottom + 14

        # Control buttons
        btn(surf, rects['run'], "run", fm, hvr=(hov == ('ctrl', 'run')))
        btn(surf, rects['reset'], "reset", fm, hvr=(hov == ('ctrl', 'reset')))
        y = rects['run'].bottom + 20

        # Metrics section
        surf.blit(fm.render("metrics", True, gray), (px + 10, y))
        y += 26
        metrics = [
            ("nodes visited", str(num)),
            ("path cost", str(cst) if cst else "-"),
            ("time ms", f"{elapsed:.1f}" if elapsed else "-"),
        ]
        for lbl, val in metrics:
            surf.blit(fs.render(lbl, True, gray), (px + 14, y))
            surf.blit(fs.render(val, True, text_c), (px + 170, y))
            y += 22

        y += 10
        
        # Legend section
        surf.blit(fm.render("legend", True, gray), (px + 10, y))
        y += 26
        legend = [
            (start_c, "start"),
            (goal_c, "goal"),
            (wall_c, "wall"),
            (front_c, "frontier"),
            (visit_c, "visited"),
            (path_c, "final path"),
        ]
        for clr, lbl in legend:
            pygame.draw.rect(surf, clr, (px + 14, y + 3, 16, 16), border_radius=3)
            surf.blit(fs.render(lbl, True, text_c), (px + 36, y))
            y += 22

        y += 10
        
        # Status display
        st_map = {
            'idle': 'idle',
            'running': 'running',
            'done': 'done',
            'no_path': 'no path found'
        }
        s = st_map.get(st, st)
        surf.blit(fm.render(f"status: {s}", True, title_c), (px + 10, y))
    
    except Exception as e:
        print(f"error drawing panel: {e}")

def run():
    """
    Main application loop
    Initializes pygame and handles all user input and rendering
    """
    print("=== RUNNING UPDATED VERSION - Grid should NOT reset on Run ===")
    try:
        # Initialize pygame
        pygame.init()
        surf = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("gbfs astar search visualizerr")
        clk = pygame.time.Clock()

        # Load fonts
        fb = pygame.font.SysFont("segoeui", 18, bold=True)
        fm = pygame.font.SysFont("segoeui", 15, bold=True)
        fs = pygame.font.SysFont("segoeui", 14)

        px = cols * cell
        
        # Button dimensions
        bw, bh = 110, 32
        bx = px + 14
        
        # Define button rectangles
        rects = {
            'algo': [
                pygame.Rect(bx, 74, bw, bh),
                pygame.Rect(bx + bw + 8, 74, bw, bh),
            ],
            'heur': [
                pygame.Rect(bx, 148, bw, bh),
                pygame.Rect(bx + bw + 8, 148, bw, bh),
            ],
            'run': pygame.Rect(bx, 192, bw, bh),
            'reset': pygame.Rect(bx + bw + 8, 192, bw, bh),
        }

        # Initialize state variables
        g = mk_grid()  # Game grid
        a_idx = 0  # Algorithm index (0=gbfs, 1=astar)
        h_idx = 0  # Heuristic index (0=manhattan, 1=euclidean)
        vis = set()  # Visited nodes
        fron = set()  # Frontier nodes
        pth = []  # Final path
        num_vis = 0  # Count of visited nodes
        path_cst = 0  # Path cost value
        elapsed = 0.0  # Elapsed time in ms
        st = 'idle'  # Current state
        gen = None  # Generator for search algorithm
        last = 0  # Last step timestamp
        hov = None  # Hover state

        running = True
        while running:
            try:
                now = pygame.time.get_ticks()
                mx, my = pygame.mouse.get_pos()

                # Detect button hover
                hov = None
                for i, r in enumerate(rects['algo']):
                    if r.collidepoint(mx, my):
                        hov = ('algo', i)
                for i, r in enumerate(rects['heur']):
                    if r.collidepoint(mx, my):
                        hov = ('heur', i)
                if rects['run'].collidepoint(mx, my):
                    hov = ('ctrl', 'run')
                if rects['reset'].collidepoint(mx, my):
                    hov = ('ctrl', 'reset')

                # Process events
                for evt in pygame.event.get():
                    try:
                        if evt.type == pygame.QUIT:
                            running = False

                        if evt.type == pygame.KEYDOWN:
                            if evt.key == pygame.K_ESCAPE:
                                running = False

                        if evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
                            # Algorithm button clicks - DON'T reset grid
                            for i, r in enumerate(rects['algo']):
                                if r.collidepoint(mx, my):
                                    a_idx = i
                                    st = 'idle'
                                    gen = None
                                    vis = set()
                                    fron = set()
                                    pth = []
                                    num_vis = path_cst = 0
                                    elapsed = 0.0
                                    # REMOVED: g = mk_grid()

                            # Heuristic button clicks - DON'T reset grid
                            for i, r in enumerate(rects['heur']):
                                if r.collidepoint(mx, my):
                                    h_idx = i
                                    st = 'idle'
                                    gen = None
                                    vis = set()
                                    fron = set()
                                    pth = []
                                    num_vis = path_cst = 0
                                    elapsed = 0.0
                                    # REMOVED: g = mk_grid()

                            # Run button click - DON'T reset grid
                            if rects['run'].collidepoint(mx, my) and st in ('idle', 'done', 'no_path'):
                                # REMOVED: g = mk_grid()
                                vis = set()
                                fron = set()
                                pth = []
                                num_vis = path_cst = 0
                                elapsed = 0.0
                                
                                # Select heuristic function
                                h_fn = h_man if h_idx == 0 else h_euc
                                
                                # Start search algorithm
                                if a_idx == 0:
                                    gen = gbfs(g, start_pos, goal_pos, h_fn)
                                else:
                                    gen = astar(g, start_pos, goal_pos, h_fn)
                                st = 'running'

                            # Reset button click - ONLY place to reset grid
                            if rects['reset'].collidepoint(mx, my):
                                g = mk_grid()
                                vis = set()
                                fron = set()
                                pth = []
                                num_vis = path_cst = 0
                                elapsed = 0.0
                                st = 'idle'
                                gen = None

                            # Grid cell click to toggle walls
                            if mx < cols * cell and st == 'idle':
                                r = my // cell
                                c = mx // cell
                                if g[r][c] == empty:
                                    g[r][c] = wall
                                elif g[r][c] == wall:
                                    g[r][c] = empty
                    
                    except Exception as e:
                        print(f"error processing event: {e}")

                # Advance search animation
                if st == 'running' and gen and (now - last) >= step_delay:
                    last = now
                    try:
                        step = next(gen)
                        kind, _, v, f, p, nv, pc, el = step
                        vis = v
                        fron = f
                        num_vis = nv
                        
                        if kind == 'done':
                            elapsed = el
                            if p:
                                pth = p
                                path_cst = pc
                                st = 'done'
                            else:
                                st = 'no_path'
                            gen = None
                    
                    except StopIteration:
                        st = 'done'
                        gen = None
                    except Exception as e:
                        print(f"error advancing search: {e}")
                        st = 'done'
                        gen = None

                # Render everything
                surf.fill(black)
                pth_set = set(pth) if pth else set()
                draw_g(surf, g, vis, fron, pth_set)
                draw_p(surf, fb, fm, fs, a_idx, h_idx, num_vis, path_cst, elapsed, rects, hov, a_idx, h_idx, st)

                pygame.display.flip()
                clk.tick(fps)
            
            except Exception as e:
                print(f"error in main loop: {e}")
                running = False

        # Cleanup
        pygame.quit()
        sys.exit()
    
    except Exception as e:
        print(f"fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()