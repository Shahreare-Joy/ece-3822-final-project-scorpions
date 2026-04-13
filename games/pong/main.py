"""
Pong — Arcade mini-game (2 players, same keyboard)
Args: --username --host --port
P1: W/S    P2: UP/DOWN
"""
import pygame, sys, random, argparse, json, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--username", default="Player")
parser.add_argument("--host",     default="localhost")
parser.add_argument("--port",     type=int, default=9000)
args = parser.parse_args()

pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

BLACK  = (8,   8,  18)
WHITE  = (255,255,255)
CYAN   = (0,  220,255)
PINK   = (255, 80,160)
YELLOW = (255,210,  0)
GRAY   = (55,  55, 90)

font_xl = pygame.font.Font(None, 80)
font_md = pygame.font.Font(None, 30)
font_sm = pygame.font.Font(None, 22)

PAD_W, PAD_H = 14, 100
BALL_R = 9
MAX_SCORE = 7

def reset_ball(direction=1):
    return {
        "x": float(W//2), "y": float(H//2),
        "vx": 4.5 * direction, "vy": random.uniform(-3, 3)
    }

state = {
    "p1y": float(H//2 - PAD_H//2),
    "p2y": float(H//2 - PAD_H//2),
    "ball": reset_ball(),
    "s1": 0, "s2": 0,
    "winner": 0,
    "p1_name": args.username,
    "p2_name": "Player 2",
}

def post_score(winner_name, score):
    try:
        data = json.dumps({"username": winner_name, "game": "pong", "score": score*100}).encode()
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
            if state["winner"] and event.key == pygame.K_r:
                state.update({"p1y": float(H//2-PAD_H//2),
                               "p2y": float(H//2-PAD_H//2),
                               "ball": reset_ball(),
                               "s1": 0, "s2": 0, "winner": 0})

    if not state["winner"]:
        keys = pygame.key.get_pressed()
        spd  = 6
        if keys[pygame.K_w]    and state["p1y"] > 55:       state["p1y"] -= spd
        if keys[pygame.K_s]    and state["p1y"] < H-PAD_H-5: state["p1y"] += spd
        if keys[pygame.K_UP]   and state["p2y"] > 55:       state["p2y"] -= spd
        if keys[pygame.K_DOWN] and state["p2y"] < H-PAD_H-5: state["p2y"] += spd

        b = state["ball"]
        b["x"] += b["vx"]; b["y"] += b["bvy"] if "bvy" in b else b["vy"]
        b["vy"] = b.get("vy", b.get("bvy", 0))

        if b["y"] - BALL_R < 55:  b["y"] = 55+BALL_R;    b["vy"] =  abs(b["vy"])
        if b["y"] + BALL_R > H-5: b["y"] = H-5-BALL_R;   b["vy"] = -abs(b["vy"])

        # P1 paddle
        if (36 < b["x"] - BALL_R < 52 and
                state["p1y"] < b["y"] < state["p1y"]+PAD_H):
            b["vx"] = abs(b["vx"]) + 0.3
            rel = (b["y"] - state["p1y"] - PAD_H//2) / (PAD_H//2)
            b["vy"] = rel * 6
            b["vx"] = min(b["vx"], 14)

        # P2 paddle
        if (W-52 < b["x"] + BALL_R < W-36 and
                state["p2y"] < b["y"] < state["p2y"]+PAD_H):
            b["vx"] = -(abs(b["vx"]) + 0.3)
            rel = (b["y"] - state["p2y"] - PAD_H//2) / (PAD_H//2)
            b["vy"] = rel * 6
            b["vx"] = max(b["vx"], -14)

        if b["x"] < 0:
            state["s2"] += 1
            state["ball"] = reset_ball(1)
        if b["x"] > W:
            state["s1"] += 1
            state["ball"] = reset_ball(-1)

        if state["s1"] >= MAX_SCORE:
            state["winner"] = 1
            post_score(state["p1_name"], state["s1"])
        if state["s2"] >= MAX_SCORE:
            state["winner"] = 2
            post_score(state["p2_name"], state["s2"])

    # draw
    screen.fill(BLACK)
    pygame.draw.rect(screen, (20,20,40), (0,0,W,52))
    pygame.draw.line(screen, GRAY, (0,52),(W,52),1)
    # dashed center
    for y in range(52, H, 18):
        pygame.draw.rect(screen, GRAY, (W//2-2, y, 4, 10))

    # scores
    s1f = font_xl.render(str(state["s1"]), True, CYAN)
    s2f = font_xl.render(str(state["s2"]), True, PINK)
    screen.blit(s1f, (W//4 - s1f.get_width()//2, 5))
    screen.blit(s2f, (3*W//4 - s2f.get_width()//2, 5))

    n1 = font_sm.render(state["p1_name"] + "  (W/S)", True, CYAN)
    n2 = font_sm.render("(UP/DN)  " + state["p2_name"], True, PINK)
    screen.blit(n1, (16, 32))
    screen.blit(n2, (W - n2.get_width() - 16, 32))

    # paddles
    pygame.draw.rect(screen, CYAN,
                     (36, int(state["p1y"]), PAD_W, PAD_H), border_radius=5)
    pygame.draw.rect(screen, PINK,
                     (W-50, int(state["p2y"]), PAD_W, PAD_H), border_radius=5)

    # ball
    b = state["ball"]
    pygame.draw.circle(screen, WHITE, (int(b["x"]), int(b["y"])), BALL_R)

    if state["winner"]:
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov,(0,0))
        wn = state["p1_name"] if state["winner"]==1 else state["p2_name"]
        wc = CYAN if state["winner"]==1 else PINK
        t1 = font_xl.render(f"{wn} WINS!", True, wc)
        t2 = font_sm.render("R = rematch   ESC = quit", True, WHITE)
        screen.blit(t1, (W//2-t1.get_width()//2, H//2-60))
        screen.blit(t2, (W//2-t2.get_width()//2, H//2+20))

    pygame.display.flip()

pygame.quit()
sys.exit()
