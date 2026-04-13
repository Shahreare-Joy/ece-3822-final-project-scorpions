"""
Rock Paper Scissors — Arcade mini-game
Args: --username --host --port
"""
import pygame, sys, random, argparse, json, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--username", default="Player")
parser.add_argument("--host",     default="localhost")
parser.add_argument("--port",     type=int, default=9000)
args = parser.parse_args()

pygame.init()
W, H = 800, 550
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Rock Paper Scissors")
clock = pygame.time.Clock()

BLACK  = (8,   8,  18)
WHITE  = (255,255,255)
CYAN   = (0,  220,255)
YELLOW = (255,210,  0)
GREEN  = (0,  220,100)
RED    = (220, 50, 50)
GRAY   = (80,  80,100)
PANEL  = (20,  20, 45)
CARD   = (28,  28, 58)

font_xl = pygame.font.Font(None, 90)
font_lg = pygame.font.Font(None, 52)
font_md = pygame.font.Font(None, 32)
font_sm = pygame.font.Font(None, 22)

CHOICES = ["ROCK", "PAPER", "SCISSORS"]
EMOJI   = ["✊",   "✋",    "✌️"]
BEATS   = {"ROCK":"SCISSORS", "PAPER":"ROCK", "SCISSORS":"PAPER"}

state = {
    "wins": 0, "losses": 0, "ties": 0,
    "player_choice": None, "cpu_choice": None,
    "result": "", "phase": "choose",  # choose | reveal
    "anim": 0,
}

def evaluate(p, c):
    if p == c: return "TIE"
    if BEATS[p] == c: return "WIN"
    return "LOSE"

def post_score(wins):
    try:
        data = json.dumps({"username": args.username, "game": "rps", "score": wins*100}).encode()
        req  = urllib.request.Request(
            f"http://{args.host}:5000/score",
            data=data, headers={"Content-Type":"application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

btn_rects = [pygame.Rect(80 + i*220, 300, 180, 120) for i in range(3)]
play_again = pygame.Rect(W//2-100, H-70, 200, 44)

running = True
while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state["phase"] == "choose":
                for i, r in enumerate(btn_rects):
                    if r.collidepoint(mx, my):
                        state["player_choice"] = CHOICES[i]
                        state["cpu_choice"]    = random.choice(CHOICES)
                        state["result"]        = evaluate(CHOICES[i], state["cpu_choice"])
                        if state["result"] == "WIN":   state["wins"]   += 1
                        elif state["result"] == "LOSE": state["losses"] += 1
                        else:                           state["ties"]   += 1
                        state["phase"] = "reveal"
                        state["anim"]  = 0
                        post_score(state["wins"])
            elif state["phase"] == "reveal":
                if play_again.collidepoint(mx, my):
                    state["player_choice"] = None
                    state["cpu_choice"]    = None
                    state["result"]        = ""
                    state["phase"]         = "choose"

    if state["phase"] == "reveal":
        state["anim"] = min(60, state["anim"] + 2)

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill(BLACK)
    pygame.draw.rect(screen, PANEL, (0,0,W,55))
    pygame.draw.line(screen, (55,55,100), (0,55),(W,55),1)
    p = font_md.render(f"RPS  |  {args.username}", True, CYAN)
    screen.blit(p, (16,16))
    sc = font_md.render(f"W:{state['wins']}  L:{state['losses']}  T:{state['ties']}", True, YELLOW)
    screen.blit(sc, (W-sc.get_width()-16, 16))

    if state["phase"] == "choose":
        t = font_lg.render("CHOOSE YOUR MOVE", True, WHITE)
        screen.blit(t, (W//2 - t.get_width()//2, 90))
        t2 = font_sm.render("Click to pick", True, GRAY)
        screen.blit(t2, (W//2 - t2.get_width()//2, 148))

        for i, (r, label, em) in enumerate(zip(btn_rects, CHOICES, EMOJI)):
            hover = r.collidepoint(mx, my)
            bg    = (35,35,72) if hover else CARD
            bc    = CYAN if hover else (55,55,100)
            pygame.draw.rect(screen, bg, r, border_radius=8)
            pygame.draw.rect(screen, bc, r, 2, border_radius=8)
            ef = pygame.font.SysFont("segoe ui emoji", 42).render(em, True, WHITE)
            screen.blit(ef, (r.centerx - ef.get_width()//2, r.y + 12))
            lf = font_sm.render(label, True, CYAN if hover else GRAY)
            screen.blit(lf, (r.centerx - lf.get_width()//2, r.bottom - 28))

    else:  # reveal
        a = state["anim"] / 60.0
        pc = state["player_choice"]
        cc = state["cpu_choice"]
        res= state["result"]

        res_color = GREEN if res=="WIN" else (RED if res=="LOSE" else YELLOW)
        res_text  = {"WIN":"YOU WIN!","LOSE":"YOU LOSE","TIE":"TIE!"}[res]

        # left card — player
        lcard = pygame.Rect(80, 90, 240, 200)
        pygame.draw.rect(screen, CARD, lcard, border_radius=10)
        pygame.draw.rect(screen, CYAN, lcard, 2, border_radius=10)
        lbl = font_sm.render(args.username.upper(), True, CYAN)
        screen.blit(lbl, (lcard.centerx - lbl.get_width()//2, lcard.y+10))
        pem = pygame.font.SysFont("segoe ui emoji", 72).render(
            EMOJI[CHOICES.index(pc)], True, WHITE)
        screen.blit(pem, (lcard.centerx - pem.get_width()//2, lcard.y+40))
        pt  = font_md.render(pc, True, WHITE)
        screen.blit(pt,  (lcard.centerx - pt.get_width()//2, lcard.bottom-36))

        # VS
        vs = font_lg.render("VS", True, GRAY)
        screen.blit(vs, (W//2 - vs.get_width()//2, 160))

        # right card — CPU
        rcard = pygame.Rect(W-320, 90, 240, 200)
        pygame.draw.rect(screen, CARD, rcard, border_radius=10)
        pygame.draw.rect(screen, PINK if res=="LOSE" else (55,55,100),
                         rcard, 2, border_radius=10)
        rlbl = font_sm.render("CPU", True, GRAY)
        screen.blit(rlbl, (rcard.centerx - rlbl.get_width()//2, rcard.y+10))
        cem  = pygame.font.SysFont("segoe ui emoji", 72).render(
            EMOJI[CHOICES.index(cc)], True, WHITE)
        screen.blit(cem,  (rcard.centerx - cem.get_width()//2, rcard.y+40))
        ct   = font_md.render(cc, True, WHITE)
        screen.blit(ct,   (rcard.centerx - ct.get_width()//2, rcard.bottom-36))

        # result
        if a > 0.3:
            rf = font_xl.render(res_text, True, res_color)
            screen.blit(rf, (W//2-rf.get_width()//2, 310))

        # play again btn
        hover_pa = play_again.collidepoint(mx,my)
        pygame.draw.rect(screen, (35,35,72) if hover_pa else CARD,
                         play_again, border_radius=6)
        pygame.draw.rect(screen, CYAN, play_again, 2, border_radius=6)
        pa_t = font_sm.render("PLAY AGAIN", True, CYAN)
        screen.blit(pa_t, (play_again.centerx-pa_t.get_width()//2,
                            play_again.centery-pa_t.get_height()//2))

    pygame.display.flip()

PINK = (255,80,160)
pygame.quit()
sys.exit()
