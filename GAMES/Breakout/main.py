"""
Breakout — Arcade mini-game
Args: --username --host --port
Controls: LEFT/RIGHT to move, SPACE to launch
"""
import pygame, sys, random, argparse, json, urllib.request, math

parser = argparse.ArgumentParser()
parser.add_argument("--username", default="Player")
parser.add_argument("--host",     default="localhost")
parser.add_argument("--port",     type=int, default=9000)
args = parser.parse_args()

pygame.init()
W, H = 900, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()

BLACK  = (8,   8,  18)
WHITE  = (255,255,255)
CYAN   = (0,  220,255)
YELLOW = (255,210,  0)
GRAY   = (55,  55, 90)
PANEL  = (20,  20, 45)
BALL_C = (255,255,255)
PAD_C  = (0,  200,255)

BRICK_COLORS = [
    (220, 50,  50),
    (255,140,  30),
    (255,210,   0),
    (0,  200, 100),
    (0,  180, 255),
    (160, 80, 255),
]

font_lg = pygame.font.Font(None, 52)
font_md = pygame.font.Font(None, 32)
font_sm = pygame.font.Font(None, 22)

ROWS, COLS = 6, 14
BRK_W = (W-60) // COLS
BRK_H = 26
BRK_OX, BRK_OY = 30, 65

def make_bricks():
    bricks = []
    for r in range(ROWS):
        for c in range(COLS):
            bricks.append({
                "rect":  pygame.Rect(BRK_OX + c*BRK_W+2, BRK_OY + r*(BRK_H+4), BRK_W-4, BRK_H),
                "color": BRICK_COLORS[r],
                "hp":    1 if r > 3 else 2,
                "pts":   (ROWS-r)*10,
                "alive": True,
            })
    return bricks

def make_state():
    return {
        "pad":      pygame.Rect(W//2-60, H-50, 120, 14),
        "bx":       float(W//2), "by": float(H-70),
        "vx":       0.0,         "vy": 0.0,
        "launched": False,
        "score":    0, "lives": 3,
        "bricks":   make_bricks(),
        "alive":    True, "won": False,
        "particles":[],
    }

state = make_state()

def post_score(score):
    try:
        data = json.dumps({"username": args.username, "game": "breakout", "score": score}).encode()
        req  = urllib.request.Request(
            f"http://{args.host}:5000/score",
            data=data, headers={"Content-Type":"application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def spawn_particles(x, y, color):
    for _ in range(8):
        a = random.uniform(0, 2*math.pi)
        s = random.uniform(2, 5)
        state["particles"].append({
            "x": x, "y": y,
            "vx": math.cos(a)*s, "vy": math.sin(a)*s,
            "life": 30, "color": color,
        })

BALL_R = 9
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_SPACE and not state["launched"] and state["alive"] and not state["won"]:
                state["launched"] = True
                state["vx"] = random.choice([-3.5, 3.5])
                state["vy"] = -5.0
            if event.key == pygame.K_r and (not state["alive"] or state["won"]):
                post_score(state["score"])
                state = make_state()

    s = state
    if s["alive"] and not s["won"]:
        keys = pygame.key.get_pressed()
        spd  = 7
        if keys[pygame.K_LEFT]  and s["pad"].left  > 5:   s["pad"].x -= spd
        if keys[pygame.K_RIGHT] and s["pad"].right < W-5: s["pad"].x += spd

        if not s["launched"]:
            s["bx"] = float(s["pad"].centerx)
        else:
            s["bx"] += s["vx"]; s["by"] += s["vy"]

            if s["bx"] - BALL_R < 0:  s["bx"] = BALL_R;    s["vx"] =  abs(s["vx"])
            if s["bx"] + BALL_R > W:  s["bx"] = W-BALL_R;  s["vx"] = -abs(s["vx"])
            if s["by"] - BALL_R < 60: s["by"] = 60+BALL_R; s["vy"] =  abs(s["vy"])

            if s["by"] > H+20:
                s["lives"] -= 1
                if s["lives"] <= 0:
                    s["alive"] = False
                    post_score(s["score"])
                else:
                    s["bx"] = float(s["pad"].centerx)
                    s["by"] = float(s["pad"].y - BALL_R - 2)
                    s["launched"] = False

            # paddle collision
            pr = s["pad"]
            bxi, byi = int(s["bx"]), int(s["by"])
            if (pr.left < bxi < pr.right and
                    pr.top - BALL_R < byi < pr.bottom):
                s["vy"] = -abs(s["vy"])
                rel = (s["bx"] - pr.centerx) / (pr.width/2)
                s["vx"] = rel * 7
                s["vx"] = max(-12, min(12, s["vx"]))

            # brick collisions
            alive_any = False
            for br in s["bricks"]:
                if not br["alive"]: continue
                alive_any = True
                if br["rect"].collidepoint(bxi, byi):
                    br["hp"] -= 1
                    if br["hp"] <= 0:
                        br["alive"] = False
                        s["score"] += br["pts"]
                        spawn_particles(br["rect"].centerx, br["rect"].centery, br["color"])
                    if abs(s["vx"]) > abs(s["vy"]): s["vx"] *= -1
                    else:                            s["vy"] *= -1
                    break
            if not alive_any:
                s["won"] = True
                s["score"] += 500
                post_score(s["score"])

        # particles
        for p in s["particles"][:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.2
            p["life"] -= 1
            if p["life"] <= 0: s["particles"].remove(p)

    # draw
    screen.fill(BLACK)
    pygame.draw.rect(screen, PANEL, (0,0,W,58))
    pygame.draw.line(screen, GRAY, (0,58),(W,58),1)
    ht = font_md.render(f"BREAKOUT  |  {args.username}", True, CYAN)
    screen.blit(ht, (16,16))
    st = font_md.render(f"SCORE: {s['score']}", True, YELLOW)
    screen.blit(st, (W-st.get_width()-16, 16))
    for i in range(s["lives"]):
        pygame.draw.circle(screen, CYAN, (W-140+i*22, 40), 7)

    for br in s["bricks"]:
        if br["alive"]:
            c = br["color"] if br["hp"] > 1 else tuple(max(0,x-60) for x in br["color"])
            pygame.draw.rect(screen, c, br["rect"], border_radius=3)
            pygame.draw.rect(screen, BLACK, br["rect"], 1, border_radius=3)

    for p in s["particles"]:
        alpha = int(255 * p["life"] / 30)
        pygame.draw.circle(screen, p["color"], (int(p["x"]),int(p["y"])), 3)

    pygame.draw.rect(screen, PAD_C, s["pad"], border_radius=5)
    pygame.draw.circle(screen, WHITE, (int(s["bx"]),int(s["by"])), BALL_R)

    if not s["launched"] and s["alive"] and not s["won"]:
        t = font_sm.render("SPACE to launch  |  LEFT/RIGHT to move", True, GRAY)
        screen.blit(t, (W//2-t.get_width()//2, H-22))

    if not s["alive"] or s["won"]:
        ov = pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov,(0,0))
        msg = "YOU WIN!" if s["won"] else "GAME OVER"
        mc  = YELLOW if s["won"] else (220,50,50)
        t1  = font_lg.render(msg, True, mc)
        t2  = font_md.render(f"Score: {s['score']}", True, WHITE)
        t3  = font_sm.render("R = restart   ESC = quit", True, CYAN)
        screen.blit(t1, (W//2-t1.get_width()//2, H//2-80))
        screen.blit(t2, (W//2-t2.get_width()//2, H//2-20))
        screen.blit(t3, (W//2-t3.get_width()//2, H//2+30))

    pygame.display.flip()

pygame.quit()
sys.exit()
