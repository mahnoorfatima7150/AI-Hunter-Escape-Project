import pygame, sys, heapq, random, time
from collections import deque

# ================= SETTINGS =================
WIDTH, HEIGHT = 900, 650
GRID_SIZE = 600
ROWS, COLS = 10, 10
CELL = GRID_SIZE // COLS

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Project - COMPLETE")
font = pygame.font.SysFont("Arial", 18)
big_font = pygame.font.SysFont("Arial", 28, True)

# ================= COLORS =================
BG = (18,18,30)
GRID = (70,70,90)
OBS = (40,40,40)
BLUE = (0,180,255)
RED = (255,70,70)
GREEN = (100,255,150)
WHITE = (230,230,230)
PANEL = (25,25,45)

# ================= GLOBAL STATE =================
algorithm = "A*"
speed = 6
steps = 0
start_time = time.time()
game_over = False
winner_text = ""

# ================= PERFORMANCE =================
results_history = []
last_result = ""

# ================= HELPERS =================
def neighbors(n, grid):
    x,y = n
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    return [(x+dx,y+dy) for dx,dy in moves
            if 0<=x+dx<ROWS and 0<=y+dy<COLS and grid[x+dx][y+dy]==0]

def heuristic(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ================= BFS =================
def bfs(start, goal, grid):
    q = deque([start])
    came = {start: None}

    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for n in neighbors(cur, grid):
            if n not in came:
                came[n] = cur
                q.append(n)

    path = []
    cur = goal
    while cur in came:
        path.append(cur)
        cur = came[cur]
    return path[::-1]

# ================= A* =================
def astar(start, goal, grid):
    heap = [(0, start)]
    came = {start: None}
    cost = {start: 0}

    while heap:
        _, cur = heapq.heappop(heap)
        if cur == goal:
            break

        for n in neighbors(cur, grid):
            new = cost[cur] + 1
            if n not in cost or new < cost[n]:
                cost[n] = new
                heapq.heappush(heap, (new + heuristic(n, goal), n))
                came[n] = cur

    path = []
    cur = goal
    while cur in came:
        path.append(cur)
        cur = came[cur]
    return path[::-1]

# ================= GREEDY =================
def greedy(start, goal, grid):
    heap = [(heuristic(start, goal), start)]
    came = {start: None}

    while heap:
        _, cur = heapq.heappop(heap)
        if cur == goal:
            break
        for n in neighbors(cur, grid):
            if n not in came:
                heapq.heappush(heap, (heuristic(n, goal), n))
                came[n] = cur

    path = []
    cur = goal
    while cur in came:
        path.append(cur)
        cur = came[cur]
    return path[::-1]

# ================= SELECT ALGO =================
def get_path(start, goal, grid):
    if algorithm == "BFS":
        return bfs(start, goal, grid)
    elif algorithm == "Greedy":
        return greedy(start, goal, grid)
    return astar(start, goal, grid)

# ================= VALID GRID =================
def generate_valid_grid():
    while True:
        g = [[0]*COLS for _ in range(ROWS)]

        for i in range(ROWS):
            for j in range(COLS):
                if random.random() < 0.25:
                    g[i][j] = 1

        g[0][0] = 0
        g[5][5] = 0
        g[9][9] = 0

        if bfs((0,0),(5,5),g) and bfs((9,9),(0,0),g):
            return g

# ================= INIT =================
grid = generate_valid_grid()
escapee = (0,0)
hunter = (9,9)
goal = (5,5)

# ================= DRAW =================
def draw():
    screen.fill(BG)

    for i in range(ROWS):
        for j in range(COLS):
            x,y = j*CELL, i*CELL
            if grid[i][j]==1:
                pygame.draw.rect(screen, OBS, (x+2,y+2,CELL-4,CELL-4))
            pygame.draw.rect(screen, GRID, (x,y,CELL,CELL),1)

    def circle(pos,color):
        x = pos[1]*CELL + CELL//2
        y = pos[0]*CELL + CELL//2
        pygame.draw.circle(screen,color,(x,y),10)

    circle(escapee, BLUE)
    circle(hunter, RED)
    circle(goal, GREEN)

    pygame.draw.rect(screen, PANEL, (600,0,300,650))
    screen.blit(big_font.render("AI PROJECT",True,WHITE),(650,20))

    elapsed = round(time.time()-start_time,2)

    screen.blit(font.render(f"Algorithm: {algorithm}",True,WHITE),(620,80))
    screen.blit(font.render(f"Steps: {steps}",True,WHITE),(620,110))
    screen.blit(font.render(f"Time: {elapsed}s",True,WHITE),(620,140))
    screen.blit(font.render(f"Speed: {speed}",True,WHITE),(620,170))

    screen.blit(font.render("1=BFS  2=A*  3=Greedy",True,WHITE),(620,240))
    screen.blit(font.render("R=New Map",True,WHITE),(620,270))
    screen.blit(font.render("UP/DOWN=Speed",True,WHITE),(620,300))

    # show last result
    screen.blit(font.render(f"Last: {last_result}",True,WHITE),(620,340))

# ================= LOOP =================
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                algorithm = "BFS"
            if event.key == pygame.K_2:
                algorithm = "A*"
            if event.key == pygame.K_3:
                algorithm = "Greedy"
            if event.key == pygame.K_r:
                grid = generate_valid_grid()
                escapee = (0,0)
                hunter = (9,9)
                steps = 0
                start_time = time.time()
                game_over = False
            if event.key == pygame.K_UP:
                speed += 1
            if event.key == pygame.K_DOWN:
                speed = max(1, speed-1)

    if not game_over:
        escapee_path = get_path(escapee, goal, grid)
        hunter_path = get_path(hunter, escapee, grid)

        if len(escapee_path) > 1:
            escapee = escapee_path[1]

        if len(hunter_path) > 1:
            hunter = hunter_path[1]

        steps += 1

        if escapee == goal:
            winner_text = "ESCAPEE WINS"
            game_over = True

        elif hunter == escapee:
            winner_text = "HUNTER WINS"
            game_over = True

        # ================= PERFORMANCE ANALYSIS =================
        if game_over:
            elapsed = round(time.time() - start_time, 3)

            result = {
                "algorithm": algorithm,
                "steps": steps,
                "time": elapsed,
                "winner": winner_text
            }

            results_history.append(result)
            last_result = f"{algorithm} | Steps:{steps} | Time:{elapsed}s"

            print("\n===== PERFORMANCE ANALYSIS =====")
            for i, r in enumerate(results_history):
                print(f"{i+1}. Algo: {r['algorithm']} | Steps: {r['steps']} | Time: {r['time']}s | Winner: {r['winner']}")
            print("================================\n")

    draw()

    if game_over:
        text = big_font.render(winner_text, True, WHITE)
        screen.blit(text, (200,300))

    pygame.display.flip()
    clock.tick(speed)
