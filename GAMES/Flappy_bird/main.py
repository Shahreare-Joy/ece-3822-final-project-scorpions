"""
Flappy Bird — Arcade mini-game
Args: --username --host --port
Controls: SPACE or UP to flap
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
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

BLACK  = (8,   8,  18)
BG     = (15,  25,  55)
WHITE  = (255,255,255)
CYAN   = (0,  220,255)
YELLOW = (255,210,  0)
GREEN  = (0,  180, 80)
DGREEN = (0,  120, 50)
RED    = (220, 50,  50)
GRAY   = (55,  55, 90)
BIRD_C = (255,200,  0)

font_xl = pygame.font.Font(None, 90)
font_lg = pygame.font.Font(None, 52)
font_md = pygame.font.Font(None, 32)
font_sm = pygame.font.Font(None, 22)

PIPE_W   = 70
GAP      = 160
GRAVITY  = 0.35
FLAP_V   = -7.0
PIPE_SPD = 3.5
BIRD_R   = 16

def make_pipe(x):
    top_h = random.randint(80, H - GAP - 80)
    return {"x": float(x), "top_h": top_h, "scored": False}

def reset():
    return {
        "bird_y": float(H//2), "bird_v": 0.0,
        "pipes":  [make_pipe(W+i*280) for i in range(3)],
        "score":  0, "alive": True, "started": False,
    }

state = reset()
high  = 0

def post_score(score):
    try:
        data = json.dumps({"username": args.username, "game": "flappy", "score": score*50}).encode()
        req  = urllib.request.Request(
            f"http://{args.host}:5000/score",
            data=data, headers={"Content-Type":"application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def draw_pipe(x, top_h):
    # top pipe
    pygame.draw.rect(screen, GREEN,
                     (int(x), 55, PIPE_W, top_h - 55), border_radius=0)
    pygame.draw.rect(screen, DGREEN,
                     (int(x)-4, top_h-24, PIPE_W+8, 24), border_radius=4)
    # bottom pipe
    bot_y = top_h + GAP
    pygame.draw.rect(screen, GREEN,
                     (int(x), bot_y, PIPE_W, H-bot_y), border_radius=0)
    pygame.draw.rect(screen, DGREEN,
                     (int(x)-4, bot_y, PIPE_W+8, 24), border_radius=4)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if state["alive"]:
                    state["started"] = True
                    state["bird_v"]  = FLAP_V
                else:
                    if state["score"] > high: high = state["score"]
                    post_score(state["score"])
                    state = reset()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state["alive"]:
                state["started"] = True
                state["bird_v"]  = FLAP_V

    s = state
    if s["alive"] and s["started"]:
        s["bird_v"] += GRAVITY
        s["bird_v"]  = min(s["bird_v"], 12)
        s["bird_y"] += s["bird_v"]

        if s["bird_y"] - BIRD_R < 55 or s["bird_y"] + BIRD_R > H:
            s["alive"] = False
            post_score(s["score"])

        for p in s["pipes"]:
            p["x"] -= PIPE_SPD
            if p["x"] + PIPE_W < 0:
                p["x"]      = max(pp["x"] for pp in s["pipes"]) + 280
                p["top_h"]  = random.randint(80, H-GAP-80)
                p["scored"] = False

            bx = 80
            if (bx+BIRD_R > p["x"] and bx-BIRD_R < p["x"]+PIPE_W and
                    (s["bird_y"]-BIRD_R < p["top_h"] or
                     s["bird_y"]+BIRD_R > p["top_h"]+GAP)):
                s["alive"] = False
                post_score(s["score"])

            if not p["scored"] and p["x"] + PIPE_W < bx:
                s["score"] += 1
                p["scored"] = True

    # draw
    screen.fill(BG)
    # top bar
    pygame.draw.rect(screen, (15,15,35), (0,0,W,52))
    pygame.draw.line(screen, GRAY, (0,52),(W,52),1)
    ht = font_md.render(f"FLAPPY  |  {args.username}", True, CYAN)
    screen.blit(ht, (16,12))
    best = font_sm.render(f"BEST: {high}", True, GRAY)
    screen.blit(best, (W-best.get_width()-16, 16))

    for p in s["pipes"]:
        draw_pipe(p["x"], p["top_h"])

    # ground
    pygame.draw.rect(screen, (20,20,40), (0, H-4, W, 4))

    # bird body
    by = int(s["bird_y"])
    tilt = max(-30, min(30, int(s["bird_v"]*3)))
    bird_surf = pygame.Surface((BIRD_R*2, BIRD_R*2), pygame.SRCALPHA)
    pygame.draw.ellipse(bird_surf, BIRD_C, (0,0,BIRD_R*2,BIRD_R*2))
    pygame.draw.circle(bird_surf, WHITE, (BIRD_R+6, BIRD_R-4), 5)
    pygame.draw.circle(bird_surf, BLACK, (BIRD_R+7, BIRD_R-4), 2)
    rotated = pygame.transform.rotate(bird_surf, -tilt)
    screen.blit(rotated, (80-rotated.get_width()//2, by-rotated.get_height()//2))

    # score
    sc = font_lg.render(str(s["score"]), True, WHITE)
    screen.blit(sc, (W//2-sc.get_width()//2, 62))

    if not s["started"] and s["alive"]:
        t = font_md.render("SPACE or CLICK to start", True, YELLOW)
        screen.blit(t, (W//2-t.get_width()//2, H//2+60))

    if not s["alive"]:
        ov = pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov,(0,0))
        t1 = font_lg.render("GAME OVER", True, RED)
        t2 = font_md.render(f"Score: {s['score']}  Best: {max(high, s['score'])}", True, YELLOW)
        t3 = font_sm.render("SPACE = restart   ESC = quit", True, CYAN)
        screen.blit(t1,(W//2-t1.get_width()//2, H//2-80))
        screen.blit(t2,(W//2-t2.get_width()//2, H//2-20))
        screen.blit(t3,(W//2-t3.get_width()//2, H//2+30))

    pygame.display.flip()

pygame.quit()
sys.exit()
