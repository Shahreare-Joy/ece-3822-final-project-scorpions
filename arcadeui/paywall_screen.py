"""
paywall_screen.py — Fake $100 payment wall for ECE 3822 Arcade.

Looks like a real payment screen. Credit card form goes nowhere.
Secret: press Q to dismiss. No hints given.
"""

import pygame
import math
import re


def run_paywall_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """
    Shows a convincing $100 payment wall.
    Press Q (secret) to dismiss and continue.
    Returns True to continue, False to quit.
    """
    W, H = screen.get_size()

    # Colors
    BG       = (245, 246, 248)
    WHITE    = (255, 255, 255)
    BLACK    = (15,  15,  20)
    DKBLUE   = (26,  54,  93)
    BLUE     = (37,  99, 235)
    BLUE_LT  = (59, 130, 246)
    BLUE_DIM = (147,197,253)
    GREEN    = (22, 163,  74)
    GREEN_LT = (240,253,244)
    GREEN_BD = (187,247,208)
    RED      = (220,  38,  38)
    GRAY     = (107, 114, 128)
    LGRAY    = (209, 213, 219)
    XLGRAY   = (243, 244, 246)
    BORDER   = (209, 213, 219)
    TEXT     = (17,  24,  39)
    SUBTEXT  = (75,  85,  99)
    GOLD     = (217,119,  6)

    font_lg  = pygame.font.SysFont("segoe ui", 26, bold=True)
    font_md  = pygame.font.SysFont("segoe ui", 18)
    font_sm  = pygame.font.SysFont("segoe ui", 14)
    font_xs  = pygame.font.SysFont("segoe ui", 12)
    font_card= pygame.font.SysFont("courier new", 17)

    # Input fields state
    fields = {
        "card":  {"label": "Card number",       "val": "", "placeholder": "1234  5678  9012  3456", "max": 19, "x":0,"y":0,"w":0,"h":0},
        "name":  {"label": "Name on card",       "val": "", "placeholder": "HAMZA MUGHAL",            "max": 26, "x":0,"y":0,"w":0,"h":0},
        "exp":   {"label": "Expiration date",    "val": "", "placeholder": "MM / YY",                 "max": 7,  "x":0,"y":0,"w":0,"h":0},
        "cvv":   {"label": "Security code",      "val": "", "placeholder": "CVV",                     "max": 3,  "x":0,"y":0,"w":0,"h":0},
        "zip":   {"label": "ZIP / Postal code",  "val": "", "placeholder": "12345",                   "max": 5,  "x":0,"y":0,"w":0,"h":0},
    }
    active_field = None
    pay_clicked  = False
    pay_hover    = False
    error_msg    = ""
    processing   = False
    process_t    = 0
    process_dots = 0

    def fmt_card(raw):
        digits = re.sub(r"\D", "", raw)[:16]
        return "  ".join(digits[i:i+4] for i in range(0, len(digits), 4))

    def fmt_exp(raw):
        digits = re.sub(r"\D", "", raw)[:4]
        if len(digits) >= 3:
            return digits[:2] + " / " + digits[2:]
        return digits

    def draw_field(surf, fid, x, y, w, h):
        f  = fields[fid]
        f["x"]=x; f["y"]=y; f["w"]=w; f["h"]=h
        active = active_field == fid
        bd_c   = BLUE if active else (BORDER if not error_msg or f["val"] else RED)
        pygame.draw.rect(surf, WHITE, (x,y,w,h), border_radius=6)
        pygame.draw.rect(surf, bd_c,  (x,y,w,h), 2 if active else 1, border_radius=6)
        # label
        lbl = font_xs.render(f["label"], True, SUBTEXT)
        surf.blit(lbl, (x, y-18))
        # value or placeholder
        display = f["val"] if f["val"] else f["placeholder"]
        color   = TEXT if f["val"] else LGRAY
        fnt     = font_card if fid == "card" else font_sm
        val_s   = fnt.render(display, True, color)
        surf.blit(val_s, (x+12, y+h//2-val_s.get_height()//2))
        # cursor
        if active and pygame.time.get_ticks() % 900 < 450 and f["val"] is not None:
            cx_ = x + 12 + fnt.size(f["val"])[0] + 1
            pygame.draw.rect(surf, TEXT, (cx_, y+10, 1, h-20))

    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # Secret dismiss key
                if event.key == pygame.K_q:
                    return True

                if active_field and not processing:
                    f = fields[active_field]
                    if event.key == pygame.K_BACKSPACE:
                        f["val"] = f["val"][:-1]
                    elif event.key == pygame.K_TAB:
                        keys = list(fields.keys())
                        idx  = keys.index(active_field)
                        active_field = keys[(idx+1) % len(keys)]
                    elif event.key == pygame.K_RETURN:
                        pass
                    else:
                        raw = f["val"] + event.unicode
                        if active_field == "card":
                            f["val"] = fmt_card(raw)
                        elif active_field == "exp":
                            f["val"] = fmt_exp(raw)
                        elif active_field in ("cvv","zip"):
                            if event.unicode.isdigit() and len(f["val"]) < f["max"]:
                                f["val"] += event.unicode
                        else:
                            if len(f["val"]) < f["max"]:
                                f["val"] += event.unicode.upper()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                active_field = None
                for fid, f in fields.items():
                    r = pygame.Rect(f["x"], f["y"], f["w"], f["h"])
                    if r.collidepoint(mx, my):
                        active_field = fid
                        break

                # Pay button area — calculated below, approximate
                pay_r = pygame.Rect(W//2-190, 530, 380, 48)
                if pay_r.collidepoint(mx, my) and not processing:
                    # validate
                    card_digits = re.sub(r"\D","",fields["card"]["val"])
                    if len(card_digits) < 16:
                        error_msg = "Please enter a valid 16-digit card number."
                    elif not fields["name"]["val"].strip():
                        error_msg = "Please enter the name on your card."
                    elif len(re.sub(r"\D","",fields["exp"]["val"])) < 4:
                        error_msg = "Please enter a valid expiration date."
                    elif len(fields["cvv"]["val"]) < 3:
                        error_msg = "CVV must be 3 digits."
                    elif len(fields["zip"]["val"]) < 5:
                        error_msg = "Please enter your ZIP code."
                    else:
                        error_msg   = ""
                        processing  = True
                        process_t   = now

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                pay_r  = pygame.Rect(W//2-190, 530, 380, 48)
                pay_hover = pay_r.collidepoint(mx, my)

        # Processing animation → fail after 3 seconds
        if processing:
            process_dots = ((now - process_t) // 400) % 4
            if now - process_t > 3200:
                processing  = False
                error_msg   = "Your card was declined. Please try a different card."
                for f in fields.values():
                    f["val"] = ""
                active_field = "card"

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Card background
        card_w, card_h = 440, 540
        cx_ = W//2 - card_w//2
        cy_ = H//2 - card_h//2 - 20
        pygame.draw.rect(screen, WHITE, (cx_, cy_, card_w, card_h), border_radius=12)
        pygame.draw.rect(screen, BORDER,(cx_, cy_, card_w, card_h), 1, border_radius=12)

        # Header stripe
        pygame.draw.rect(screen, DKBLUE, (cx_, cy_, card_w, 62), border_radius=12)
        pygame.draw.rect(screen, DKBLUE, (cx_, cy_+46, card_w, 16))

        hdr  = font_lg.render("PIXEL ARCADE", True, WHITE)
        sub  = font_xs.render("Premium Access  •  One-time payment", True, BLUE_DIM)
        screen.blit(hdr, (cx_+20, cy_+10))
        screen.blit(sub, (cx_+20, cy_+38))

        # Lock icon (simple)
        lk_x, lk_y = cx_+card_w-48, cy_+12
        pygame.draw.rect(screen, BLUE_DIM, (lk_x, lk_y+10, 22, 16), border_radius=3)
        pygame.draw.arc(screen, BLUE_DIM,
                        pygame.Rect(lk_x+3, lk_y, 16, 16), 0, math.pi, 3)

        # Price section
        py0 = cy_ + 78
        price_lbl = font_xs.render("AMOUNT DUE", True, SUBTEXT)
        price_val = font_lg.render("$100.00", True, TEXT)
        once_lbl  = font_xs.render("One-time  •  Instant access  •  No subscription", True, GRAY)
        screen.blit(price_lbl, (cx_+20, py0))
        screen.blit(price_val, (cx_+20, py0+16))
        screen.blit(once_lbl, (cx_+20, py0+46))

        pygame.draw.line(screen, BORDER,
                         (cx_+20, py0+68), (cx_+card_w-20, py0+68), 1)

        # Form fields
        fx = cx_ + 20
        fw = card_w - 40
        fy = py0 + 86

        draw_field(screen, "card", fx,        fy,      fw,    42)
        draw_field(screen, "name", fx,        fy+80,   fw,    42)
        draw_field(screen, "exp",  fx,        fy+160,  fw//2-6, 42)
        draw_field(screen, "cvv",  fx+fw//2+6,fy+160,  (fw//2-6)//2-4, 42)
        draw_field(screen, "zip",  fx+fw//2+6+(fw//2-6)//2,fy+160, (fw//2-6)//2, 42)

        # Error message
        if error_msg:
            err_box = pygame.Rect(cx_+20, fy+218, fw, 30)
            pygame.draw.rect(screen, (254,242,242), err_box, border_radius=4)
            pygame.draw.rect(screen, (252,165,165), err_box, 1, border_radius=4)
            err_t = font_xs.render(error_msg, True, RED)
            screen.blit(err_t, (err_box.x+8, err_box.centery-err_t.get_height()//2))

        # Pay button
        btn_y = cy_ + card_h - 78
        btn_r = pygame.Rect(cx_+20, btn_y, fw, 46)
        btn_c = (21,128,61) if pay_hover and not processing else GREEN
        pygame.draw.rect(screen, btn_c, btn_r, border_radius=8)

        if processing:
            dots  = "." * process_dots
            btn_t = font_md.render(f"Processing{dots}", True, WHITE)
        else:
            btn_t = font_md.render("Pay $100.00", True, WHITE)
        screen.blit(btn_t, (btn_r.centerx-btn_t.get_width()//2,
                             btn_r.centery-btn_t.get_height()//2))

        # Fine print
        fine1 = font_xs.render("Secured by 256-bit SSL encryption", True, GRAY)
        fine2 = font_xs.render("By continuing you agree to our Terms of Service and Privacy Policy", True, LGRAY)
        screen.blit(fine1, (W//2-fine1.get_width()//2, cy_+card_h+10))
        screen.blit(fine2, (W//2-fine2.get_width()//2, cy_+card_h+26))

        # Card brand logos (drawn as colored pills)
        brands = [("VISA","\u2022",(26,54,93)), ("MC","●",(235,87,35)), ("AMEX","●",(0,112,185))]
        bx = cx_+card_w-20
        for name, sym, col in reversed(brands):
            pill = pygame.Rect(bx-38, cy_+card_h-30, 36, 16)
            pygame.draw.rect(screen, col, pill, border_radius=3)
            bt = font_xs.render(name, True, WHITE)
            screen.blit(bt, (pill.centerx-bt.get_width()//2, pill.centery-bt.get_height()//2))
            bx -= 42

        pygame.display.flip()
        clock.tick(60)

    return True
