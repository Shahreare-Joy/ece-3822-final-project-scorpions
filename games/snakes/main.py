"""
Snake — Arcade mini-game
Args: --username --host --port
"""
import pygame, sys, random, argparse, json, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--username", default="Player")
parser.add_argument("--host",     default="localhost")
parser.add_argument("--port",     type=int, default=9000)
args = parser.parse_args()

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

CELL = 20
COLS = (W - 40) // CELL
ROWS = (H - 80) // CELL
OX, OY = 20, 60

BLACK  = (8,   8,  18)
GREEN  = (0,  220, 100)
DGREEN = (0,  140,  60)
RED    = (220,  50,  50)
YELLOW = (255, 210,   0)
GRAY   = (80,   80, 100)
CYAN   = (0,   220, 255)
WHITE  = (255, 255, 255)

font_lg = pygame.font.Font(None, 52)
font_md = pygame.font.Font(None, 30)
font_sm = pygame.font.Font(None, 22)

def new_food(body):
    while True:
        f = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if f not in body: return f

def reset():
    body = [(COLS//2, ROWS//2)]
    return {"body": body, "dir": (1,0), "next": (1,0),
            "food": new_food(body), "score": 0, "alive": True,
            "timer": 0, "speed": 8}

state = reset()
high  = 0

def post_score(score):
    try:
        data = json.dumps({"username": args.username, "game": "snake", "score": score}).encode()
        req  = urllib.request.Request(
            f"http://{args.host}:5000/score",
            data=data, headers={"Content-Type":"application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if not state["alive"] and event.key == pygame.K_r:
                if state["score"] > high: high = state["score"]
                post_score(state["score"])
                state = reset()
            dirs = {
                pygame.K_UP:(0,-1), pygame.K_w:(0,-1),
                pygame.K_DOWN:(0,1), pygame.K_s:(0,1),
                pygame.K_LEFT:(-1,0), pygame.K_a:(-1,0),
                pygame.K_RIGHT:(1,0), pygame.K_d:(1,0),
            }
            if event.key in dirs:
                nd = dirs[event.key]
                if nd[0]+state["dir"][0] != 0 or nd[1]+state["dir"][1] != 0:
                    state["next"] = nd

    # update
    if state["alive"]:
        state["timer"] += 1
        if state["timer"] >= 60 // state["speed"]:
            state["timer"] = 0
            state["dir"] = state["next"]
            hx, hy = state["body"][0]
            nx, ny = hx + state["dir"][0], hy + state["dir"][1]
            if not (0 <= nx < COLS and 0 <= ny < ROWS) or (nx,ny) in state["body"]:
                state["alive"] = False
                post_score(state["score"])
            else:
                state["body"].insert(0, (nx, ny))
                if (nx, ny) == state["food"]:
                    state["score"] += 10
                    state["food"]   = new_food(state["body"])
                    state["speed"]  = min(20, state["speed"] + 0.3)
                else:
                    state["body"].pop()

    # draw
    screen.fill(BLACK)
    # top bar
    pygame.draw.rect(screen, (20,20,40), (0,0,W,55))
    pygame.draw.line(screen, (55,55,100), (0,55), (W,55), 1)
    p = font_md.render(f"SNAKE  |  {args.username}", True, CYAN)
    screen.blit(p, (16, 16))
    sc = font_md.render(f"SCORE: {state['score']}", True, YELLOW)
    screen.blit(sc, (W - sc.get_width() - 16, 16))

    # grid border
    pygame.draw.rect(screen, (30,30,55),
                     (OX-2, OY-2, COLS*CELL+4, ROWS*CELL+4), border_radius=4)
    pygame.draw.rect(screen, (55,55,100),
                     (OX-2, OY-2, COLS*CELL+4, ROWS*CELL+4), 2, border_radius=4)

    # food
    fx = OX + state["food"][0]*CELL
    fy = OY + state["food"][1]*CELL
    pygame.draw.rect(screen, RED, (fx+2, fy+2, CELL-4, CELL-4), border_radius=4)

    # snake
    for i, (cx, cy) in enumerate(state["body"]):
        c = GREEN if i == 0 else DGREEN
        pygame.draw.rect(screen, c,
                         (OX+cx*CELL+1, OY+cy*CELL+1, CELL-2, CELL-2), border_radius=3)

    if not state["alive"]:
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov, (0,0))
        t1 = font_lg.render("GAME OVER", True, RED)
        t2 = font_md.render(f"Score: {state['score']}  |  Best: {max(high, state['score'])}", True, YELLOW)
        t3 = font_sm.render("R = restart   ESC = quit", True, CYAN)
        screen.blit(t1, (W//2-t1.get_width()//2, H//2-80))
        screen.blit(t2, (W//2-t2.get_width()//2, H//2-20))
        screen.blit(t3, (W//2-t3.get_width()//2, H//2+30))

    pygame.display.flip()

pygame.quit()
sys.exit()
