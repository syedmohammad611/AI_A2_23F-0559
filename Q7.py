import pygame
import heapq
import math
import time
import sys

ROWS, COLS = 8, 8
CELL = 80
SIDE_W = 280
WIDTH = COLS * CELL + SIDE_W
HEIGHT = ROWS * CELL

FPS = 30
DELAY = 120

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (180, 180, 180)
DARK = (60, 60, 60)
CLR_START = (50, 200, 80)
CLR_GOAL = (220, 50, 50)
CLR_WALL = (40, 40, 40)
CLR_OPEN = (255, 220, 0)
CLR_SEEN = (100, 149, 237)
CLR_PATH = (50, 220, 130)
CLR_PANEL = (25, 25, 40)
CLR_BTN = (60, 80, 140)
CLR_BTN_H = (90, 120, 200)
CLR_BTN_A = (40, 180, 100)
CLR_TEXT = (230, 230, 230)
CLR_TITLE = (180, 210, 255)

EMPTY, BLOCK, ORIGIN, TARGET = 0, 1, 2, 3

def generate_board():
    board = [[EMPTY] * COLS for _ in range(ROWS)]
    for i in range(2, 6):
        board[i][3] = BLOCK
        board[i][5] = BLOCK
    for j in range(1, 4):
        board[4][j] = BLOCK
    for j in range(4, 7):
        board[6][j] = BLOCK
    board[1][1] = ORIGIN
    board[6][6] = TARGET
    return board

START_NODE = (1, 1)
GOAL_NODE = (6, 6)

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

def adjacent(node, board):
    r, c = node
    res = []
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] != BLOCK:
            res.append((nr, nc))
    return res

def h_manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def h_euclid(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def greedy_search(board, start, goal, heuristic):
    heap = [(heuristic(start, goal), 0, start)]
    order = 1
    parent = {start: None}
    seen = set()
    count = 0
    t0 = time.time()

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in seen:
            continue
        seen.add(current)
        count += 1
        yield ('step', current, seen.copy(), set(n for _,_,n in heap), None, count, 0, 0)

        if current == goal:
            route = []
            node = goal
            while node is not None:
                route.append(node)
                node = parent[node]
            route.reverse()
            cost = len(route) - 1
            elapsed = (time.time() - t0) * 1000
            yield ('finish', None, seen, set(), route, count, cost, elapsed)
            return

        for nxt in adjacent(current, board):
            if nxt not in seen and nxt not in parent:
                parent[nxt] = current
                heapq.heappush(heap, (heuristic(nxt, goal), order, nxt))
                order += 1

        yield ('expand', current, seen.copy(), set(n for _,_,n in heap), None, count, 0, 0)

    yield ('finish', None, seen, set(), None, count, 0, (time.time()-t0)*1000)

def a_star(board, start, goal, heuristic):
    heap = [(heuristic(start, goal), 0, start)]
    order = 1
    parent = {start: None}
    g = {start: 0}
    seen = set()
    count = 0
    t0 = time.time()

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in seen:
            continue
        seen.add(current)
        count += 1
        yield ('step', current, seen.copy(), set(n for _,_,n in heap), None, count, 0, 0)

        if current == goal:
            route = []
            node = goal
            while node is not None:
                route.append(node)
                node = parent[node]
            route.reverse()
            cost = g[goal]
            elapsed = (time.time() - t0) * 1000
            yield ('finish', None, seen, set(), route, count, cost, elapsed)
            return

        for nxt in adjacent(current, board):
            temp = g[current] + 1
            if nxt not in g or temp < g[nxt]:
                g[nxt] = temp
                f = temp + heuristic(nxt, goal)
                parent[nxt] = current
                heapq.heappush(heap, (f, order, nxt))
                order += 1

        yield ('expand', current, seen.copy(), set(n for _,_,n in heap), None, count, 0, 0)

    yield ('finish', None, seen, set(), None, count, 0, (time.time()-t0)*1000)

def button(surface, rect, label, font, active=False, hover=False):
    color = CLR_BTN_A if active else (CLR_BTN_H if hover else CLR_BTN)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, GRAY, rect, 1, border_radius=8)
    txt = font.render(label, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))

def draw_board(surface, board, seen, open_set, route):
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c*CELL, r*CELL
            cell = board[r][c]

            if cell == BLOCK:
                color = CLR_WALL
            elif cell == ORIGIN:
                color = CLR_START
            elif cell == TARGET:
                color = CLR_GOAL
            elif route and (r,c) in route:
                color = CLR_PATH
            elif (r,c) in seen:
                color = CLR_SEEN
            elif (r,c) in open_set:
                color = CLR_OPEN
            else:
                color = WHITE

            pygame.draw.rect(surface, color, (x+1,y+1,CELL-2,CELL-2), border_radius=4)

    for r in range(ROWS+1):
        pygame.draw.line(surface, GRAY, (0,r*CELL),(COLS*CELL,r*CELL))
    for c in range(COLS+1):
        pygame.draw.line(surface, GRAY, (c*CELL,0),(c*CELL,ROWS*CELL))

def side_panel(surface, f_big, f_med, f_sm,
               algo_i, heur_i, visited_ct, cost, elapsed,
               rects, hover, state):

    px = COLS * CELL
    pygame.draw.rect(surface, CLR_PANEL, (px,0,SIDE_W,HEIGHT))
    pygame.draw.line(surface, GRAY, (px,0),(px,HEIGHT),2)

    title = f_big.render("Pathfinding Visualizer", True, CLR_TITLE)
    surface.blit(title,(px+10,10))

    y = 50
    surface.blit(f_med.render("Algorithm",True,GRAY),(px+10,y)); y+=24
    for i,(lbl,r) in enumerate(zip(["Greedy","A*"],rects['algo'])):
        button(surface,r,lbl,f_med,active=(i==algo_i),hover=(hover==('algo',i)))

    y = rects['algo'][0].bottom + 10
    surface.blit(f_med.render("Heuristic",True,GRAY),(px+10,y)); y+=24
    for i,(lbl,r) in enumerate(zip(["Manhattan","Euclidean"],rects['heur'])):
        button(surface,r,lbl,f_med,active=(i==heur_i),hover=(hover==('heur',i)))

    button(surface,rects['run'],"Run",f_med,hover=(hover==('ctrl','run')))
    button(surface,rects['reset'],"Reset",f_med,hover=(hover==('ctrl','reset')))

    y = rects['run'].bottom + 20
    surface.blit(f_med.render("Metrics",True,GRAY),(px+10,y)); y+=26

    data = [
        ("Visited", str(visited_ct)),
        ("Cost", str(cost) if cost else "—"),
        ("Time(ms)", f"{elapsed:.1f}" if elapsed else "—")
    ]
    for label,val in data:
        surface.blit(f_sm.render(label+":",True,GRAY),(px+14,y))
        surface.blit(f_sm.render(val,True,CLR_TEXT),(px+170,y))
        y+=22

    status_map={'idle':'Idle','running':'Running','done':'Done','fail':'No Path'}
    surface.blit(f_med.render("Status: "+status_map.get(state,state),
                              True,CLR_TITLE),(px+10,y+20))

def run_app():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Search Demo")
    clock = pygame.time.Clock()

    f_big = pygame.font.SysFont("segoeui",18,True)
    f_med = pygame.font.SysFont("segoeui",15,True)
    f_sm = pygame.font.SysFont("segoeui",14)

    px = COLS*CELL
    bw,bh = 110,32
    bx = px+14

    rects={
        'algo':[pygame.Rect(bx,74,bw,bh),
                pygame.Rect(bx+bw+8,74,bw,bh)],
        'heur':[pygame.Rect(bx,148,bw,bh),
                pygame.Rect(bx+bw+8,148,bw,bh)],
        'run':pygame.Rect(bx,192,bw,bh),
        'reset':pygame.Rect(bx+bw+8,192,bw,bh)
    }

    board=generate_board()
    algo_i=0
    heur_i=0
    seen=set()
    open_set=set()
    route=[]
    visited_ct=0
    cost=0
    elapsed=0.0
    state='idle'
    gen=None
    last=0
    hover=None

    running=True
    while running:
        now=pygame.time.get_ticks()
        mx,my=pygame.mouse.get_pos()

        hover=None
        for i,r in enumerate(rects['algo']):
            if r.collidepoint(mx,my): hover=('algo',i)
        for i,r in enumerate(rects['heur']):
            if r.collidepoint(mx,my): hover=('heur',i)
        if rects['run'].collidepoint(mx,my): hover=('ctrl','run')
        if rects['reset'].collidepoint(mx,my): hover=('ctrl','reset')

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                running=False

            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                for i,r in enumerate(rects['algo']):
                    if r.collidepoint(mx,my):
                        algo_i=i; state='idle'; gen=None
                        seen=set(); open_set=set(); route=[]
                        visited_ct=cost=0; elapsed=0.0
                        board=generate_board()

                for i,r in enumerate(rects['heur']):
                    if r.collidepoint(mx,my):
                        heur_i=i; state='idle'; gen=None
                        seen=set(); open_set=set(); route=[]
                        visited_ct=cost=0; elapsed=0.0
                        board=generate_board()

                if rects['run'].collidepoint(mx,my) and state in ('idle','done','fail'):
                    board=generate_board()
                    seen=set(); open_set=set(); route=[]
                    visited_ct=cost=0; elapsed=0.0
                    h = h_manhattan if heur_i==0 else h_euclid
                    gen = greedy_search(board,START_NODE,GOAL_NODE,h) if algo_i==0 \
                          else a_star(board,START_NODE,GOAL_NODE,h)
                    state='running'

                if rects['reset'].collidepoint(mx,my):
                    board=generate_board()
                    seen=set(); open_set=set(); route=[]
                    visited_ct=cost=0; elapsed=0.0
                    state='idle'; gen=None

                if mx < COLS*CELL and state=='idle':
                    r=my//CELL; c=mx//CELL
                    if board[r][c]==EMPTY: board[r][c]=BLOCK
                    elif board[r][c]==BLOCK: board[r][c]=EMPTY

        if state=='running' and gen and (now-last)>=DELAY:
            last=now
            try:
                kind,_,s,o,p,v_ct,cst,el=next(gen)
                seen=s; open_set=o; visited_ct=v_ct
                if kind=='finish':
                    elapsed=el
                    if p:
                        route=p; cost=cst; state='done'
                    else:
                        state='fail'
                    gen=None
            except StopIteration:
                state='done'; gen=None

        screen.fill(BLACK)
        draw_board(screen,board,seen,open_set,set(route))
        side_panel(screen,f_big,f_med,f_sm,
                   algo_i,heur_i,visited_ct,cost,elapsed,
                   rects,hover,state)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    run_app()