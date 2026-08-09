#!/usr/bin/env python3
"""Generate 520 unique dino coloring pages — 39 REAL species, each with its
own recognizable anatomy (T-Rex tiny arms, Stegosaurus plates, Spinosaurus
sail, Ankylosaurus club tail, Parasaurolophus crest, raptor sickle claw...).

Each page = list of regions. Region kinds:
  fill  -> tappable, user colors it (white default, black outline)
  fixed -> decoration (pupils, smile lines), not tappable
Path data uses ONLY absolute M, L, C, Q, Z commands (Flutter parser contract).
Canvas: 1024 x 1024.
"""
import json
import math
import os
import random

W = H = 1024
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "pages")
SVG_OUT = os.path.join(os.path.dirname(__file__), "..", "preview_svgs")

K = 0.5522847498  # circle bezier constant


def ci_hash(s):
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) % 100003
    return h


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def ellipse(cx, cy, rx, ry, rot=0.0):
    cos, sin = math.cos(rot), math.sin(rot)

    def tp(x, y):
        x, y = x - cx, y - cy
        return (cx + x * cos - y * sin, cy + x * sin + y * cos)

    p0 = tp(cx + rx, cy)
    arcs = [
        ((cx + rx, cy + ry * K), (cx + rx * K, cy + ry), (cx, cy + ry)),
        ((cx - rx * K, cy + ry), (cx - rx, cy + ry * K), (cx - rx, cy)),
        ((cx - rx, cy - ry * K), (cx - rx * K, cy - ry), (cx, cy - ry)),
        ((cx + rx * K, cy - ry), (cx + rx, cy - ry * K), (cx + rx, cy)),
    ]
    d = f"M {f(p0[0])} {f(p0[1])}"
    for a, b, e in arcs:
        a, b, e = tp(*a), tp(*b), tp(*e)
        d += f" C {f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} {f(e[0])} {f(e[1])}"
    return d + " Z"


def poly(pts, close=True):
    d = f"M {f(pts[0][0])} {f(pts[0][1])}"
    for p in pts[1:]:
        d += f" L {f(p[0])} {f(p[1])}"
    return d + (" Z" if close else "")


def open_quad(pts):
    d = f"M {f(pts[0][0])} {f(pts[0][1])}"
    for i in range(1, len(pts) - 1, 2):
        d += f" Q {f(pts[i][0])} {f(pts[i][1])} {f(pts[i+1][0])} {f(pts[i+1][1])}"
    return d


class Page:
    def __init__(self, pid, title, category):
        self.id = pid
        self.title = title
        self.category = category
        self.regions = []
        self._n = 0
        self._gc = None

    def use(self, color):
        """Set the guide color for the fill() regions that follow."""
        self._gc = color

    def fill(self, d, gc=None):
        self._n += 1
        r = {"id": f"r{self._n}", "d": d, "kind": "fill"}
        color = gc or self._gc
        if color:
            r["gc"] = color
        self.regions.append(r)

    def fixed(self, d, color="#222222", stroke=False, sw=7):
        self._n += 1
        r = {"id": f"r{self._n}", "d": d, "kind": "fixed", "color": color}
        if stroke:
            r["stroke"] = True
            r["sw"] = sw
        self.regions.append(r)


# ---------- shared scenery ----------

def sky(pg):
    pg.fill(f"M 0 0 L {W} 0 L {W} {H} L 0 {H} Z", gc="#BFE7F5")


def ground(pg, rng, y=780):
    bumps = rng.randint(2, 4)
    pts = [(0, H), (0, y + rng.randint(-30, 30))]
    step = W / bumps
    for i in range(bumps):
        pts.append((step * i + step / 2, y - rng.randint(30, 90)))
        pts.append((step * (i + 1), y + rng.randint(-20, 30)))
    pts.append((W, H))
    d = f"M 0 {H} L {f(pts[1][0])} {f(pts[1][1])}"
    for i in range(2, len(pts) - 1, 2):
        d += f" Q {f(pts[i][0])} {f(pts[i][1])} {f(pts[i+1][0])} {f(pts[i+1][1])}"
    d += f" L {W} {H} Z"
    pg.fill(d, gc="#A5D6A7")


def sun(pg, rng, cx=None, cy=170):
    cx = cx if cx is not None else rng.choice([160, 864])
    r = rng.randint(60, 85)
    pg.fill(ellipse(cx, cy, r, r), gc="#FFD54F")
    n = rng.choice([8, 10, 12])
    for i in range(n):
        a = 2 * math.pi * i / n
        x1, y1 = cx + math.cos(a) * (r + 18), cy + math.sin(a) * (r + 18)
        x2, y2 = cx + math.cos(a) * (r + 55), cy + math.sin(a) * (r + 55)
        pg.fixed(f"M {f(x1)} {f(y1)} L {f(x2)} {f(y2)}", stroke=True, sw=9)


def cloud(pg, rng, cx, cy):
    s = rng.uniform(0.8, 1.3)
    d = (
        f"M {f(cx-100*s)} {f(cy+30*s)}"
        f" C {f(cx-140*s)} {f(cy+30*s)} {f(cx-140*s)} {f(cy-25*s)} {f(cx-95*s)} {f(cy-25*s)}"
        f" C {f(cx-90*s)} {f(cy-70*s)} {f(cx-20*s)} {f(cy-75*s)} {f(cx-5*s)} {f(cy-40*s)}"
        f" C {f(cx+35*s)} {f(cy-70*s)} {f(cx+90*s)} {f(cy-45*s)} {f(cx+85*s)} {f(cy-8*s)}"
        f" C {f(cx+130*s)} {f(cy-5*s)} {f(cx+125*s)} {f(cy+30*s)} {f(cx+85*s)} {f(cy+30*s)} Z"
    )
    pg.fill(d, gc="#FFFFFF")


def volcano(pg, rng, cx=800, base=800):
    w, h = rng.randint(170, 210), rng.randint(220, 300)
    pg.fill(
        f"M {f(cx-w)} {f(base)} Q {f(cx-w*0.35)} {f(base-h*0.75)} {f(cx-w*0.28)} {f(base-h)}"
        f" L {f(cx+w*0.28)} {f(base-h)} Q {f(cx+w*0.35)} {f(base-h*0.75)} {f(cx+w)} {f(base)} Z",
        gc="#A1887F",
    )
    pg.fill(ellipse(cx, base - h - 55, 70, 42), gc="#E0E0E0")


def tree(pg, rng, cx, base):
    th = rng.randint(120, 190)
    tw = rng.randint(22, 32)
    pg.fill(f"M {f(cx-tw)} {f(base)} L {f(cx-tw*0.6)} {f(base-th)} L {f(cx+tw*0.6)} {f(base-th)} L {f(cx+tw)} {f(base)} Z", gc="#8D6E63")
    pg.fill(ellipse(cx, base - th - 60, 85 + rng.randint(-10, 20), 70), gc="#66BB6A")


def flower(pg, rng, cx, cy):
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        pg.fill(ellipse(cx + math.cos(a) * 24, cy + math.sin(a) * 24, 17, 17), gc="#F48FB1")
    pg.fill(ellipse(cx, cy, 13, 13), gc="#FFEE58")
    pg.fixed(f"M {f(cx)} {f(cy+38)} L {f(cx)} {f(cy+85)}", stroke=True, sw=8)


def butterfly(pg, rng, cx, cy):
    pg.fill(ellipse(cx - 26, cy - 12, 26, 20, -0.4), gc="#CE93D8")
    pg.fill(ellipse(cx + 26, cy - 12, 26, 20, 0.4), gc="#CE93D8")
    pg.fill(ellipse(cx - 20, cy + 16, 18, 14, -0.3), gc="#FFCC80")
    pg.fill(ellipse(cx + 20, cy + 16, 18, 14, 0.3), gc="#FFCC80")
    pg.fixed(ellipse(cx, cy, 7, 24), "#222222")


def balloon(pg, rng, cx, cy):
    pg.fill(ellipse(cx, cy, 55, 68), gc="#EF5350")
    pg.fixed(f"M {f(cx)} {f(cy+68)} Q {f(cx-18)} {f(cy+140)} {f(cx+8)} {f(cy+205)}", stroke=True, sw=6)


def party_hat(pg, rng, cx, cy, s=1.0):
    pg.fill(f"M {f(cx-52*s)} {f(cy)} L {f(cx)} {f(cy-115*s)} L {f(cx+52*s)} {f(cy)} Z", gc="#AB47BC")
    pg.fill(ellipse(cx, cy - 115 * s, 20 * s, 20 * s), gc="#FFEE58")


def egg(pg, rng, cx, cy, s=1.0, cracked=False):
    pg.fill(
        f"M {f(cx)} {f(cy-95*s)}"
        f" C {f(cx+58*s)} {f(cy-95*s)} {f(cx+72*s)} {f(cy-10*s)} {f(cx+70*s)} {f(cy+20*s)}"
        f" C {f(cx+66*s)} {f(cy+75*s)} {f(cx-66*s)} {f(cy+75*s)} {f(cx-70*s)} {f(cy+20*s)}"
        f" C {f(cx-72*s)} {f(cy-10*s)} {f(cx-58*s)} {f(cy-95*s)} {f(cx)} {f(cy-95*s)} Z",
        gc="#FFF3E0",
    )
    if cracked:
        zz = f"M {f(cx-58*s)} {f(cy)} L {f(cx-30*s)} {f(cy-22*s)} L {f(cx-6*s)} {f(cy+4*s)} L {f(cx+22*s)} {f(cy-20*s)} L {f(cx+46*s)} {f(cy+2*s)} L {f(cx+60*s)} {f(cy-12*s)}"
        pg.fixed(zz, stroke=True, sw=7)


def star(pg, rng, cx, cy, s=1.0):
    pts = []
    for i in range(10):
        r = 34 * s if i % 2 == 0 else 14 * s
        a = math.pi * i / 5 - math.pi / 2
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pg.fill(poly(pts), gc="#FFF176")


def rainbow(pg, rng, cx=512, cy=340, r0=260):
    for i in range(3):
        r_out, r_in = r0 - i * 46, r0 - i * 46 - 40
        d = (
            f"M {f(cx-r_out)} {f(cy)}"
            f" C {f(cx-r_out)} {f(cy-r_out*1.32)} {f(cx+r_out)} {f(cy-r_out*1.32)} {f(cx+r_out)} {f(cy)}"
            f" L {f(cx+r_in)} {f(cy)}"
            f" C {f(cx+r_in)} {f(cy-r_in*1.32)} {f(cx-r_in)} {f(cy-r_in*1.32)} {f(cx-r_in)} {f(cy)} Z"
        )
        pg.fill(d, gc=["#EF5350", "#FFB74D", "#FFF176"][i])


def eye(pg, cx, cy, r=26, look=0.0):
    pg.fill(ellipse(cx, cy, r, r), gc="#FFFFFF")
    pg.fixed(ellipse(cx + look * r * 0.3, cy, r * 0.42, r * 0.42), "#222222")


def smile(pg, cx, cy, w=60, up=28):
    pg.fixed(f"M {f(cx-w)} {f(cy)} Q {f(cx)} {f(cy+up)} {f(cx+w)} {f(cy)}", stroke=True, sw=9)


def face(pg, hx, hy, rx, ry, flip=1):
    """Eye + smile sized for the head; call AFTER all head shapes."""
    er = max(10.0, ry * 0.3)
    if er > ry * 0.45:
        er = ry * 0.45
    eye(pg, hx + flip * rx * 0.35, hy - ry * 0.22, er, flip * 0.4)
    smile(pg, hx + flip * rx * 0.5, hy + ry * 0.32, max(8.0, rx * 0.28), ry * 0.13)


def legs(pg, rng, cx, cy, spread=120, lw=46, lh=130, n=2):
    xs = [cx - spread, cx + spread] if n == 2 else [cx - spread, cx - spread * 0.33, cx + spread * 0.33, cx + spread]
    for x in xs:
        d = (
            f"M {f(x-lw)} {f(cy)} L {f(x-lw)} {f(cy+lh-24)}"
            f" Q {f(x-lw)} {f(cy+lh)} {f(x-lw+24)} {f(cy+lh)}"
            f" L {f(x+lw-24)} {f(cy+lh)} Q {f(x+lw)} {f(cy+lh)} {f(x+lw)} {f(cy+lh-24)}"
            f" L {f(x+lw)} {f(cy)} Z"
        )
        pg.fill(d)


def belly(pg, cx, cy, rx, ry):
    pg.fill(ellipse(cx, cy, rx, ry), gc="#FFF8E1")


def tail(pg, rng, x0, y0, flip=1, length=None, up=None):
    ln = length or rng.randint(230, 320)
    u = up or rng.randint(90, 170)
    d = (
        f"M {f(x0)} {f(y0-70)}"
        f" Q {f(x0+flip*ln*0.7)} {f(y0-u)} {f(x0+flip*ln)} {f(y0-u-30)}"
        f" Q {f(x0+flip*(ln*0.75))} {f(y0-20)} {f(x0)} {f(y0+55)} Z"
    )
    pg.fill(d)


def tail_strip(pg, x0, y0, flip, ln, thick):
    """Thin stiff tail (raptors)."""
    pg.fill(
        f"M {f(x0)} {f(y0-thick)} Q {f(x0+flip*ln*0.6)} {f(y0-thick*1.6)} {f(x0+flip*ln)} {f(y0-12)}"
        f" L {f(x0+flip*ln)} {f(y0+12)} Q {f(x0+flip*ln*0.6)} {f(y0+thick*1.6)} {f(x0)} {f(y0+thick)} Z"
    )


def tri(pg, p1, p2, p3, gc=None):
    pg.fill(f"M {f(p1[0])} {f(p1[1])} L {f(p2[0])} {f(p2[1])} L {f(p3[0])} {f(p3[1])} Z", gc=gc)


def teeth(pg, x, y, flip, n=3, s=22):
    pts = [(x, y)]
    for i in range(n):
        pts.append((x + flip * (s * i + s * 0.5), y + 18))
        pts.append((x + flip * (s * (i + 1)), y))
    d = f"M {f(pts[0][0])} {f(pts[0][1])}"
    for p in pts[1:]:
        d += f" L {f(p[0])} {f(p[1])}"
    pg.fixed(d, stroke=True, sw=7)


# ---------- shared body bases ----------

def predator_base(pg, rng, flip=1, cx=470, cy=560, arm=(55, 22), head_r=(120, 100)):
    """Big two-legged meat-eater body. Returns head pos."""
    rx, ry = rng.randint(170, 195), rng.randint(140, 160)
    tail(pg, rng, cx - flip * rx * 0.8, cy, -flip)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.5, lw=52, lh=150)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx + flip * 20, cy + 35, rx * 0.55, ry * 0.55)
    aw, ah = arm
    pg.fill(ellipse(cx + flip * (rx * 0.55), cy - 20, aw, ah, 0.5 * flip))
    pg.fill(ellipse(cx + flip * (rx * 0.62), cy + 40, aw * 0.9, ah * 0.9, 0.2 * flip))
    hx, hy = cx + flip * (rx * 0.75), cy - ry - rng.randint(55, 85)
    pg.fill(ellipse(hx, hy, head_r[0], head_r[1]))
    return hx, hy, rx, ry, cx, cy


def sauropod(pg, rng, flip=1, cx=470, cy=620, body_s=1.0, neck_top=380, neck_dx=70,
             tail_len=280, tail_up=80, whip=False):
    """Long-neck giant. neck_top = how high above cy the head sits."""
    rx, ry = int(200 * body_s), int(148 * body_s)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=tail_len, up=tail_up)
    if whip:
        tipx = cx - flip * rx * 0.85 - flip * tail_len
        tipy = cy - tail_up - 30
        tail_strip(pg, tipx, tipy, -flip, 60, 8)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=50, lh=140, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    nx = cx + flip * rx * 0.7
    top = cy - neck_top
    pg.fill(
        f"M {f(nx-60)} {f(cy-40)}"
        f" Q {f(nx+flip*neck_dx*0.55)} {f(top+120)} {f(nx+flip*neck_dx)} {f(top)}"
        f" L {f(nx+flip*(neck_dx+90))} {f(top+30)}"
        f" Q {f(nx+flip*(neck_dx*0.6+60))} {f(top+220)} {f(nx+80)} {f(cy)} Z"
    )
    hx, hy = nx + flip * (neck_dx + 45), top - 10
    pg.fill(ellipse(hx, hy, 85, 62))
    face(pg, hx, hy, 85, 62, flip)
    return hx, hy


def trike_base(pg, rng, flip=1, cx=520, cy=590, brow_horns=True, nose_horn=True,
               frill_spikes=False, nose_boss=False, s=1.0):
    rx, ry = int(200 * s), int(142 * s)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=200, up=50)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=46, lh=130, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    hx, hy = cx + flip * (rx * 0.9), cy - ry * 0.55
    pg.fill(ellipse(hx - flip * 30, hy - 30, 105, 120))  # frill
    if frill_spikes:
        prev = pg._gc
        pg.use("#FF8A65")
        for i in range(5):
            a = math.radians(150 - i * 30)  # spread over frill top
            sx = hx - flip * 30 - math.cos(a) * 0 - flip * 0
            sx = hx - flip * 30 + math.cos(a) * 108 * -flip
            sy = hy - 30 - math.sin(a) * 122
            tri(pg, (sx - 14, sy + 22), (sx, sy - 34), (sx + 14, sy + 22))
        pg.use(prev)
    pg.fill(ellipse(hx + flip * 30, hy, 95, 75))  # head
    pg.fill(f"M {f(hx+flip*105)} {f(hy-10)} Q {f(hx+flip*165)} {f(hy+5)} {f(hx+flip*112)} {f(hy+42)} Z")  # beak
    prev = pg._gc
    pg.use("#D7CCC8")
    if brow_horns:
        tri(pg, (hx + flip * 10, hy - 62), (hx + flip * 28, hy - 150), (hx + flip * 52, hy - 58))
        tri(pg, (hx - flip * 36, hy - 66), (hx - flip * 20, hy - 148), (hx + flip * 2, hy - 60))
    if nose_horn:
        tri(pg, (hx + flip * 74, hy + 28), (hx + flip * 118, hy + 14), (hx + flip * 82, hy + 52))
    if nose_boss:
        pg.fill(ellipse(hx + flip * 88, hy + 18, 30, 24))
    pg.use(prev)
    face(pg, hx + flip * 30, hy, 95, 75, flip)
    return hx, hy


def raptor_base(pg, rng, flip=1, cx=480, cy=540, s=1.0, tuft=False):
    rx, ry = 120 * s, 75 * s
    tail_strip(pg, cx - flip * rx * 0.85, cy - 10, -flip, 220 * s, 22 * s)
    legs(pg, rng, cx, cy + ry * 0.6, spread=rx * 0.4, lw=32 * s, lh=150 * s)
    pg.fill(ellipse(cx, cy, rx, ry))
    hx, hy = cx + flip * (rx * 0.95), cy - ry - 40 * s
    pg.fill(ellipse(hx, hy, 62 * s, 48 * s))
    pg.fill(ellipse(hx + flip * 55 * s, hy + 8 * s, 45 * s, 22 * s))  # narrow snout
    pg.fill(ellipse(cx + flip * (rx * 0.6), cy + 10 * s, 40 * s, 16 * s, 0.4 * flip))  # arm
    # sickle claw on the back foot
    fx = cx + flip * (rx * 0.4) + 30 * s
    fy = cy + ry * 0.6 + 148 * s
    tri(pg, (fx - 20 * s, fy), (fx + 18 * s, fy), (fx + 4 * s, fy - 30 * s))
    if tuft:
        for k in (-1, 0, 1):
            px = hx + k * 22 * s
            pg.fill(f"M {f(px-12*s)} {f(hy-42*s)} Q {f(px)} {f(hy-80*s)} {f(px+12*s)} {f(hy-42*s)} Z")
    face(pg, hx, hy, 62 * s, 48 * s, flip)
    return hx, hy


def hadrosaur(pg, rng, flip=1, cx=480, cy=560):
    """Duckbill body. Returns head pos (crest drawn by species)."""
    rx, ry = 165, 125
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=260, up=60)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.45, lw=48, lh=140)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 30, rx * 0.55, ry * 0.5)
    pg.fill(ellipse(cx + flip * (rx * 0.5), cy + 10, 42, 18, 0.4 * flip))
    hx, hy = cx + flip * (rx * 0.8), cy - ry - 40
    pg.fill(ellipse(hx, hy, 88, 70))
    pg.fill(ellipse(hx + flip * 78, hy + 16, 55, 26))  # flat duckbill
    return hx, hy


# ---------- CATEGORY: Big Predators ----------

def trex(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(52, 20), head_r=(120, 100))
    pg.fill(ellipse(hx + flip * 95, hy + 25, 70, 48))  # big snout
    teeth(pg, hx + flip * 60, hy + 60, flip, 3)
    face(pg, hx, hy, 120, 100, flip)
    return hx, hy


def allosaurus(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(78, 26), head_r=(112, 90))
    pg.fill(ellipse(hx + flip * 88, hy + 22, 66, 42))
    # brow ridges above the eye
    tri(pg, (hx + flip * 10, hy - 70), (hx + flip * 30, hy - 108), (hx + flip * 50, hy - 66))
    tri(pg, (hx + flip * 42, hy - 62), (hx + flip * 62, hy - 98), (hx + flip * 82, hy - 56))
    face(pg, hx, hy, 112, 90, flip)
    return hx, hy


def carnotaurus(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(34, 15), head_r=(104, 88))
    pg.fill(ellipse(hx + flip * 80, hy + 22, 62, 44))
    # two devil horns above the eyes
    tri(pg, (hx + flip * 2, hy - 66), (hx + flip * 8, hy - 128), (hx + flip * 34, hy - 72))
    tri(pg, (hx + flip * 46, hy - 62), (hx + flip * 58, hy - 122), (hx + flip * 80, hy - 62))
    face(pg, hx, hy, 104, 88, flip)
    return hx, hy


def ceratosaurus(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(60, 22), head_r=(110, 92))
    pg.fill(ellipse(hx + flip * 86, hy + 24, 64, 44))
    # nose horn on the snout
    tri(pg, (hx + flip * 86, hy - 22), (hx + flip * 104, hy - 84), (hx + flip * 122, hy - 18))
    # brow ridges
    tri(pg, (hx + flip * 14, hy - 66), (hx + flip * 30, hy - 100), (hx + flip * 48, hy - 62))
    face(pg, hx, hy, 110, 92, flip)
    return hx, hy


def baryonyx(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(88, 28), head_r=(98, 78))
    # long crocodile snout
    pg.fill(ellipse(hx + flip * 120, hy + 16, 105, 24))
    # big thumb claw on the arm
    ax = cx + flip * (rx * 0.62) + flip * 70
    tri(pg, (ax, cy + 30), (ax + flip * 55, cy + 78), (ax + flip * 10, cy + 88))
    # small head crest bump
    pg.fill(ellipse(hx - flip * 10, hy - 72, 22, 14))
    face(pg, hx, hy, 98, 78, flip)
    return hx, hy


def spinosaurus(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(70, 24), head_r=(100, 82))
    pg.fill(ellipse(hx + flip * 105, hy + 18, 95, 26))  # long croc snout
    # THE SAIL: membrane arc + tall spines along the back
    prev = pg._gc
    pg.use("#FFAB91")
    top_y = cy - ry + 10
    pg.fill(f"M {f(cx-rx*0.75)} {f(top_y)} Q {f(cx)} {f(top_y-195)} {f(cx+rx*0.75)} {f(top_y)} Z")
    n = 6
    for i in range(n):
        t = i / (n - 1)
        px = cx - rx * 0.62 + t * rx * 1.24
        h = 120 + 70 * math.sin(math.pi * t)
        tri(pg, (px - 13, top_y + 4), (px, top_y - h), (px + 13, top_y + 4))
    pg.use(prev)
    face(pg, hx, hy, 100, 82, flip)
    return hx, hy


# ---------- CATEGORY: Raptors & Speedsters ----------

def velociraptor(pg, rng, flip=1):
    return raptor_base(pg, rng, flip, s=1.0, tuft=True)


def deinonychus(pg, rng, flip=1):
    return raptor_base(pg, rng, flip, s=1.18, tuft=True)


def compsognathus(pg, rng, flip=1):
    return raptor_base(pg, rng, flip, s=0.58, tuft=False)


def oviraptor(pg, rng, flip=1):
    hx, hy = raptor_base(pg, rng, flip, s=0.92, tuft=False)
    # head crest
    tri(pg, (hx - 18, hy - 40), (hx + flip * 8, hy - 95), (hx + 26, hy - 40))
    # tail feather fan (3 ellipses at tail tip)
    tx = 480 - flip * (120 * 0.92 * 0.85) - flip * 200
    ty = 540 - 10
    for i, dy in enumerate((-28, 0, 28)):
        pg.fill(ellipse(tx, ty + dy, 42, 16, flip * 0.3 * (i - 1)))
    return hx, hy


def gallimimus(pg, rng, flip=1, slim=False):
    cx, cy = 470, 520
    rx, ry = (100, 72) if slim else (115, 82)
    tail(pg, rng, cx - flip * rx * 0.8, cy, -flip, length=185, up=40)
    legs(pg, rng, cx, cy + ry * 0.5, spread=rx * 0.4, lw=22, lh=235)
    pg.fill(ellipse(cx, cy, rx, ry))
    nx = cx + flip * rx * 0.7
    pg.fill(
        f"M {f(nx-16)} {f(cy-30)} Q {f(nx+flip*20)} {f(cy-160)} {f(nx+flip*38)} {f(cy-220)}"
        f" L {f(nx+flip*66)} {f(cy-210)} Q {f(nx+flip*45)} {f(cy-140)} {f(nx+22)} {f(cy)} Z"
    )
    hx, hy = nx + flip * 52, cy - 232
    pg.fill(ellipse(hx, hy, 38, 28))
    pg.fill(ellipse(hx + flip * 34, hy + 4, 26, 12))  # beak
    face(pg, hx, hy, 38, 28, flip)
    return hx, hy


def ornithomimus(pg, rng, flip=1):
    return gallimimus(pg, rng, flip, slim=True)


# ---------- CATEGORY: Horned & Frilled ----------

def triceratops(pg, rng, flip=1):
    return trike_base(pg, rng, flip, brow_horns=True, nose_horn=True)


def styracosaurus(pg, rng, flip=1):
    return trike_base(pg, rng, flip, brow_horns=False, nose_horn=True, frill_spikes=True)


def pachyrhinosaurus(pg, rng, flip=1):
    return trike_base(pg, rng, flip, brow_horns=False, nose_horn=False, nose_boss=True)


def protoceratops(pg, rng, flip=1):
    return trike_base(pg, rng, flip, brow_horns=False, nose_horn=False, s=0.72)


# ---------- CATEGORY: Long Neck Giants ----------

def brachiosaurus(pg, rng, flip=1):
    return sauropod(pg, rng, flip, neck_top=380, neck_dx=70)


def diplodocus(pg, rng, flip=1):
    return sauropod(pg, rng, flip, neck_top=250, neck_dx=200, tail_len=230, tail_up=30, whip=True)


def brontosaurus(pg, rng, flip=1):
    return sauropod(pg, rng, flip, body_s=1.06, neck_top=340, neck_dx=110, tail_len=280)


def apatosaurus(pg, rng, flip=1):
    return sauropod(pg, rng, flip, neck_top=290, neck_dx=150, tail_len=290)


def mamenchisaurus(pg, rng, flip=1):
    return sauropod(pg, rng, flip, body_s=0.9, neck_top=430, neck_dx=50, tail_len=250)


# ---------- CATEGORY: Armored & Plated ----------

def stegosaurus(pg, rng, flip=1):
    cx, cy = 500, 590
    rx, ry = rng.randint(200, 225), rng.randint(130, 150)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=rng.randint(200, 250), up=60)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=44, lh=135, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    prev = pg._gc
    pg.use("#FF8A65")
    n = rng.choice([5, 6])
    for i in range(n):
        t = i / (n - 1)
        px = cx - rx * 0.8 + t * rx * 1.6
        py = cy - ry * math.sqrt(max(0.05, 1 - ((px - cx) / rx) ** 2)) + 6
        s = 55 + 28 * math.sin(math.pi * t)
        pg.fill(f"M {f(px-s*0.7)} {f(py)} Q {f(px)} {f(py-s*1.7)} {f(px+s*0.7)} {f(py)} Z")
    pg.use(prev)
    hx, hy = cx + flip * (rx * 0.95), cy - 55
    pg.fill(ellipse(hx, hy, 88, 66))
    face(pg, hx, hy, 88, 66, flip)
    sx = cx - flip * (rx + 110)
    for k in range(2):  # tail spikes (thagomizer)
        tri(pg, (sx + k * 36 * flip, cy - 130), (sx + k * 36 * flip + 14, cy - 195),
            (sx + k * 36 * flip + 28, cy - 130), gc="#D7CCC8")
    return hx, hy


def kentrosaurus(pg, rng, flip=1):
    cx, cy = 500, 590
    rx, ry = 195, 135
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=210, up=60)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=44, lh=135, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    # pairs of thin SPIKES along the back (not plates)
    n = 6
    for i in range(n):
        t = i / (n - 1)
        px = cx - rx * 0.75 + t * rx * 1.5
        py = cy - ry * math.sqrt(max(0.05, 1 - ((px - cx) / rx) ** 2)) + 8
        h = 95 + 45 * math.sin(math.pi * t)
        tri(pg, (px - 12, py), (px - 2, py - h), (px + 10, py), gc="#FF8A65")
    # shoulder spike
    tri(pg, (cx + flip * rx * 0.72, cy - 60), (cx + flip * (rx * 0.72 + 55), cy - 130),
        (cx + flip * (rx * 0.72 + 30), cy - 45), gc="#FF8A65")
    hx, hy = cx + flip * (rx * 0.95), cy - 55
    pg.fill(ellipse(hx, hy, 80, 60))
    face(pg, hx, hy, 80, 60, flip)
    return hx, hy


def anky_base(pg, rng, flip=1, club=True, head_bumps=False):
    cx, cy = 500, 640
    rx, ry = 210, 100
    legs(pg, rng, cx, cy + ry * 0.5, spread=rx * 0.55, lw=46, lh=95, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    # armor bumps in two rows
    for row in range(2):
        oy = -45 + row * 38
        for i in range(6):
            bx = cx - rx * 0.65 + i * (rx * 1.3 / 5)
            by = cy + oy - ry * 0.55 * math.sqrt(max(0.05, 1 - ((bx - cx) / rx) ** 2)) + row * 20
            pg.fill(ellipse(bx, by, 20, 15), gc="#A1887F")
    # tail + club
    tx = cx - flip * rx * 0.9
    pg.fill(
        f"M {f(tx)} {f(cy-20)} Q {f(tx-flip*130)} {f(cy-30)} {f(tx-flip*190)} {f(cy+5)}"
        f" L {f(tx-flip*190)} {f(cy+45)} Q {f(tx-flip*130)} {f(cy+30)} {f(tx)} {f(cy+30)} Z"
    )
    if club:
        pg.fill(ellipse(tx - flip * 195, cy + 25, 55, 48), gc="#6D4C41")
    hx, hy = cx + flip * (rx * 0.92), cy - 55
    pg.fill(ellipse(hx, hy, 72, 54))
    pg.fill(ellipse(hx + flip * 55, hy + 12, 40, 26))  # beak
    tri(pg, (hx - flip * 60, hy - 20), (hx - flip * 95, hy - 55), (hx - flip * 45, hy - 45), gc="#D7CCC8")  # rear horn
    if head_bumps:
        pg.fill(ellipse(hx, hy - 50, 18, 13), gc="#A1887F")
        pg.fill(ellipse(hx + flip * 40, hy - 42, 15, 11), gc="#A1887F")
    face(pg, hx, hy, 72, 54, flip)
    return hx, hy


def ankylosaurus(pg, rng, flip=1):
    return anky_base(pg, rng, flip, club=True, head_bumps=False)


def euoplocephalus(pg, rng, flip=1):
    return anky_base(pg, rng, flip, club=True, head_bumps=True)


# ---------- CATEGORY: Sky Flyers ----------

def ptero_variant(pg, rng, flip=1, cx=512, cy=430, ww=None, head_r=(78, 64),
                  crest=1.0, beak="long", tail_len=0, tail_vane=False):
    ww = ww or rng.randint(300, 350)
    pg.fill(f"M {f(cx)} {f(cy)} Q {f(cx-ww*0.6)} {f(cy-190)} {f(cx-ww)} {f(cy-60)} Q {f(cx-ww*0.5)} {f(cy+40)} {f(cx-60)} {f(cy+60)} Z")
    pg.fill(f"M {f(cx)} {f(cy)} Q {f(cx+ww*0.6)} {f(cy-190)} {f(cx+ww)} {f(cy-60)} Q {f(cx+ww*0.5)} {f(cy+40)} {f(cx+60)} {f(cy+60)} Z")
    pg.fill(ellipse(cx, cy + 40, 95, 120))
    belly(pg, cx, cy + 70, 55, 70)
    if tail_len:
        tail_strip(pg, cx - flip * 60, cy + 120, -flip, tail_len, 11)
        if tail_vane:
            tx = cx - flip * (60 + tail_len)
            ty = cy + 120
            pg.fill(poly([(tx, ty - 30), (tx - flip * 32, ty), (tx, ty + 30), (tx + flip * 32, ty)]), gc="#FFCC80")
    hx, hy = cx, cy - 110
    pg.fill(ellipse(hx, hy, head_r[0], head_r[1]))
    if crest:
        pg.fill(f"M {f(hx-flip*20)} {f(hy-head_r[1]*0.8)} Q {f(hx-flip*130*crest)} {f(hy-110)} {f(hx-flip*60)} {f(hy-20)} Z", gc="#FFD54F")
    if beak == "long":
        pg.fill(f"M {f(hx+flip*60)} {f(hy-14)} L {f(hx+flip*175)} {f(hy+16)} L {f(hx+flip*62)} {f(hy+34)} Z")
    else:
        tri(pg, (hx + flip * head_r[0] * 0.7, hy - 10),
            (hx + flip * (head_r[0] * 0.7 + 70), hy + 18),
            (hx + flip * head_r[0] * 0.7, hy + 36))
    face(pg, hx, hy, head_r[0], head_r[1], flip)
    return hx, hy


def pteranodon(pg, rng, flip=1):
    return ptero_variant(pg, rng, flip, crest=1.0, beak="long")


def rhamphorhynchus(pg, rng, flip=1):
    return ptero_variant(pg, rng, flip, ww=270, head_r=(66, 54), crest=0.0,
                         beak="short", tail_len=170, tail_vane=True)


def dimorphodon(pg, rng, flip=1):
    return ptero_variant(pg, rng, flip, ww=250, head_r=(92, 76), crest=0.0,
                         beak="short", tail_len=90)


def quetzalcoatlus(pg, rng, flip=1):
    """Giant pterosaur standing tall."""
    cx, cy = 500, 560
    legs(pg, rng, cx, cy + 70, spread=45, lw=26, lh=170)
    pg.fill(ellipse(cx, cy, 95, 85))
    # folded wings
    pg.fill(f"M {f(cx-60)} {f(cy-30)} Q {f(cx-200)} {f(cy+20)} {f(cx-150)} {f(cy+140)} Q {f(cx-80)} {f(cy+90)} {f(cx-45)} {f(cy+40)} Z")
    pg.fill(f"M {f(cx+60)} {f(cy-30)} Q {f(cx+200)} {f(cy+20)} {f(cx+150)} {f(cy+140)} Q {f(cx+80)} {f(cy+90)} {f(cx+45)} {f(cy+40)} Z")
    # very long neck
    pg.fill(
        f"M {f(cx-34)} {f(cy-50)} Q {f(cx-30)} {f(cy-260)} {f(cx+flip*15)} {f(cy-330)}"
        f" L {f(cx+flip*55)} {f(cy-318)} Q {f(cx+30)} {f(cy-230)} {f(cx+34)} {f(cy-40)} Z"
    )
    hx, hy = cx + flip * 35, cy - 340
    pg.fill(ellipse(hx, hy, 55, 42))
    # long pointed beak
    tri(pg, (hx + flip * 45, hy - 8), (hx + flip * 185, hy + 14), (hx + flip * 45, hy + 26))
    # small back crest
    tri(pg, (hx - flip * 10, hy - 38), (hx - flip * 70, hy - 70), (hx - flip * 35, hy - 10))
    face(pg, hx, hy, 55, 42, flip)
    return hx, hy


def archaeopteryx(pg, rng, flip=1):
    """Feathered bird-dino standing."""
    cx, cy = 480, 560
    legs(pg, rng, cx, cy + 50, spread=35, lw=22, lh=170)
    pg.fill(ellipse(cx, cy, 105, 72))  # slim body
    # long tail with feather fan
    tail_strip(pg, cx - flip * 90, cy + 10, -flip, 170, 14)
    tx = cx - flip * 260
    for i, dy in enumerate((-26, 0, 26)):
        pg.fill(ellipse(tx, cy + 10 + dy, 46, 15, flip * 0.25 * (i - 1)))
    # feathered wings (layered ellipses)
    pg.fill(ellipse(cx + flip * 10, cy - 20, 115, 55, 0.25 * flip))
    pg.fill(ellipse(cx + flip * 25, cy + 10, 90, 40, 0.15 * flip))
    # small head + beak
    hx, hy = cx + flip * 110, cy - 85
    pg.fill(ellipse(hx, hy, 50, 40))
    tri(pg, (hx + flip * 42, hy - 4), (hx + flip * 88, hy + 12), (hx + flip * 42, hy + 22))
    face(pg, hx, hy, 50, 40, flip)
    return hx, hy


# ---------- CATEGORY: Sea Monsters ----------

def plesio_base(pg, rng, flip=1, cx=500, cy=560, neck_top=330, head_r=(75, 55)):
    rx, ry = 180, 105
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 25, rx * 0.6, ry * 0.5)
    pg.fill(ellipse(cx - 60, cy + ry - 8, 75, 30, 0.5))
    pg.fill(ellipse(cx + 80, cy + ry - 8, 75, 30, -0.4))
    nx = cx + flip * rx * 0.75
    top = cy - neck_top
    pg.fill(
        f"M {f(nx-50)} {f(cy-30)} Q {f(nx+flip*30)} {f(top+100)} {f(nx+flip*55)} {f(top)}"
        f" L {f(nx+flip*135)} {f(top+35)} Q {f(nx+flip*75)} {f(top+200)} {f(nx+70)} {f(cy+10)} Z"
    )
    hx, hy = nx + flip * 95, top - 5
    pg.fill(ellipse(hx, hy, head_r[0], head_r[1]))
    face(pg, hx, hy, head_r[0], head_r[1], flip)
    # tail fin
    pg.fill(f"M {f(cx-flip*rx)} {f(cy-20)} Q {f(cx-flip*(rx+130))} {f(cy-90)} {f(cx-flip*(rx+90))} {f(cy+10)} Q {f(cx-flip*(rx+130))} {f(cy+80)} {f(cx-flip*rx)} {f(cy+30)} Z")
    return hx, hy


def plesiosaurus(pg, rng, flip=1):
    return plesio_base(pg, rng, flip, neck_top=330, head_r=(75, 55))


def elasmosaurus(pg, rng, flip=1):
    return plesio_base(pg, rng, flip, neck_top=455, head_r=(56, 42))


def mosasaurus(pg, rng, flip=1):
    cx, cy = 500, 560
    rx, ry = 240, 75
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 18, rx * 0.62, ry * 0.5)
    # tail fluke
    tx = cx - flip * rx
    pg.fill(f"M {f(tx)} {f(cy-15)} Q {f(tx-flip*110)} {f(cy-110)} {f(tx-flip*90)} {f(cy-10)} Q {f(tx-flip*120)} {f(cy+80)} {f(tx)} {f(cy+20)} Z")
    # four small flippers
    for i, dx in enumerate((-90, -30, 60, 130)):
        pg.fill(ellipse(cx + dx, cy + ry - 6, 42, 16, 0.35 if dx < 0 else -0.3))
    # head + two-part jaw
    hx, hy = cx + flip * (rx * 0.95), cy - 10
    pg.fill(ellipse(hx, hy, 80, 52))
    tri(pg, (hx + flip * 60, hy - 16), (hx + flip * 170, hy + 2), (hx + flip * 62, hy + 22))
    tri(pg, (hx + flip * 58, hy + 26), (hx + flip * 150, hy + 18), (hx + flip * 60, hy + 40))
    teeth(pg, hx + flip * 80, hy + 14, flip, 3, 16)
    face(pg, hx, hy, 80, 52, flip)
    return hx, hy


def ichthyosaurus(pg, rng, flip=1):
    cx, cy = 500, 560
    rx, ry = 200, 85
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 20, rx * 0.6, ry * 0.5)
    # dorsal fin
    pg.fill(f"M {f(cx-30)} {f(cy-ry+8)} Q {f(cx+5)} {f(cy-ry-90)} {f(cx+45)} {f(cy-ry+6)} Z")
    # vertical tail fluke
    tx = cx - flip * rx
    pg.fill(f"M {f(tx)} {f(cy)} Q {f(tx-flip*80)} {f(cy-90)} {f(tx-flip*60)} {f(cy-10)} Q {f(tx-flip*90)} {f(cy+70)} {f(tx)} {f(cy+10)} Z")
    # pectoral fin
    pg.fill(ellipse(cx + flip * 60, cy + ry - 4, 50, 18, 0.4 * flip))
    # long dolphin snout
    hx, hy = cx + flip * (rx * 0.85), cy - 20
    pg.fill(ellipse(hx, hy, 85, 58))
    tri(pg, (hx + flip * 70, hy - 8), (hx + flip * 200, hy + 6), (hx + flip * 72, hy + 22))
    face(pg, hx, hy, 85, 58, flip)
    return hx, hy


# ---------- CATEGORY: Crests & Duckbills ----------

def parasaurolophus(pg, rng, flip=1):
    hx, hy = hadrosaur(pg, rng, flip)
    # long backward tube crest
    pg.fill(
        f"M {f(hx-flip*20)} {f(hy-55)} Q {f(hx-flip*200)} {f(hy-120)} {f(hx-flip*260)} {f(hy-40)}"
        f" L {f(hx-flip*235)} {f(hy-6)} Q {f(hx-flip*150)} {f(hy-58)} {f(hx-flip*8)} {f(hy-16)} Z",
        gc="#FF8F00",
    )
    face(pg, hx, hy, 88, 70, flip)
    return hx, hy


def corythosaurus(pg, rng, flip=1):
    hx, hy = hadrosaur(pg, rng, flip)
    pg.fill(ellipse(hx - flip * 10, hy - 58, 60, 46), gc="#AED581")  # helmet crest
    face(pg, hx, hy, 88, 70, flip)
    return hx, hy


def edmontosaurus(pg, rng, flip=1):
    hx, hy = hadrosaur(pg, rng, flip)
    pg.fill(ellipse(hx, hy - 64, 26, 16), gc="#EF9A9A")  # small fleshy comb
    face(pg, hx, hy, 88, 70, flip)
    return hx, hy


def pachycephalosaurus(pg, rng, flip=1):
    hx, hy = raptor_base(pg, rng, flip, s=1.25, tuft=False)
    # big dome on the head + bumps around it
    pg.fill(ellipse(hx, hy - 60, 48, 40), gc="#B39DDB")
    for a in (-0.5, 0.0, 0.5):
        pg.fill(ellipse(hx + flip * 40 * math.sin(a + 0.5), hy - 60 - 30 * math.cos(a), 10, 8), gc="#B39DDB")
    return hx, hy


def dilophosaurus(pg, rng, flip=1):
    hx, hy, rx, ry, cx, cy = predator_base(pg, rng, flip, arm=(62, 20), head_r=(95, 80))
    pg.fill(ellipse(hx + flip * 75, hy + 20, 58, 36))
    # TWO thin parallel crests on the head
    pg.fill(f"M {f(hx-flip*30)} {f(hy-62)} Q {f(hx+flip*10)} {f(hy-125)} {f(hx+flip*55)} {f(hy-118)} Q {f(hx+flip*12)} {f(hy-100)} {f(hx-flip*5)} {f(hy-56)} Z", gc="#FF7043")
    pg.fill(f"M {f(hx-flip*8)} {f(hy-58)} Q {f(hx+flip*30)} {f(hy-108)} {f(hx+flip*70)} {f(hy-100)} Q {f(hx+flip*32)} {f(hy-88)} {f(hx+flip*14)} {f(hy-50)} Z", gc="#FF7043")
    face(pg, hx, hy, 95, 80, flip)
    return hx, hy


# ---------- CATEGORY: Baby Dinos ----------

def baby(pg, rng, flip=1, feature="spikes"):
    cx, cy, s = 512, 560, 1.0
    rx, ry = 150 * s, 140 * s
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 30 * s, rx * 0.6, ry * 0.55)
    legs(pg, rng, cx, cy + ry * 0.6, spread=rx * 0.45, lw=38 * s, lh=85 * s)
    hx, hy = cx, cy - ry - 60 * s
    pg.fill(ellipse(hx, hy, 125 * s, 110 * s))
    eye(pg, hx - 45 * s, hy - 10, 30 * s, 0.3)
    eye(pg, hx + 45 * s, hy - 10, 30 * s, 0.3)
    smile(pg, hx, hy + 52 * s, 42 * s, 22 * s)
    if feature == "spikes":  # baby t-rex
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=170, up=60)
        for k in (-1, 0, 1):
            px = hx + k * 46 * s
            pg.fill(f"M {f(px-20*s)} {f(hy-100*s)} Q {f(px)} {f(hy-160*s)} {f(px+20*s)} {f(hy-100*s)} Z", gc="#FF8A65")
    elif feature == "frill":  # baby triceratops
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=150, up=50)
        pg.fill(ellipse(hx, hy - 20, 150 * s, 130 * s), gc="#D7CCC8")  # frill behind head
        tri(pg, (hx - 40, hy - 120), (hx - 28, hy - 175), (hx - 12, hy - 118), gc="#BCAAA4")
        tri(pg, (hx + 40, hy - 120), (hx + 28, hy - 175), (hx + 12, hy - 118), gc="#BCAAA4")
        tri(pg, (hx - 10, hy + 30), (hx, hy + 62), (hx + 10, hy + 30), gc="#BCAAA4")
    elif feature == "plates":  # baby stegosaurus
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=150, up=45)
        for i in range(4):
            t = i / 3
            px = cx - rx * 0.7 + t * rx * 1.4
            py = cy - ry * math.sqrt(max(0.05, 1 - ((px - cx) / rx) ** 2)) + 6
            sz = 34 + 14 * math.sin(math.pi * t)
            pg.fill(f"M {f(px-sz*0.7)} {f(py)} Q {f(px)} {f(py-sz*1.7)} {f(px+sz*0.7)} {f(py)} Z", gc="#FF8A65")
    elif feature == "longneck":  # baby long neck
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=150, up=50)
        # neck ring decoration
        pg.fixed(open_quad([(hx - 70, hy + 70), (hx, hy + 95), (hx + 70, hy + 70)]), stroke=True, sw=8)
    elif feature == "crest":  # baby parasaurolophus
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=150, up=50)
        pg.fill(
            f"M {f(hx-flip*15)} {f(hy-95)} Q {f(hx-flip*120)} {f(hy-150)} {f(hx-flip*165)} {f(hy-95)}"
            f" L {f(hx-flip*140)} {f(hy-60)} Q {f(hx-flip*85)} {f(hy-95)} {f(hx+flip*10)} {f(hy-60)} Z",
            gc="#FF8F00",
        )
    elif feature == "club":  # baby ankylosaurus
        tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=140, up=30)
        tx = cx - flip * rx * 0.8 - flip * 145
        pg.fill(ellipse(tx, cy - 25, 42, 36), gc="#8D6E63")  # tail club
        for i in range(3):
            px = cx - rx * 0.5 + i * rx * 0.5
            py = cy - ry * 0.9
            pg.fill(ellipse(px, py, 15, 11), gc="#A1887F")
    return hx, hy


def baby_trex(pg, rng, flip=1):
    return baby(pg, rng, flip, "spikes")


def baby_trike(pg, rng, flip=1):
    return baby(pg, rng, flip, "frill")


def baby_stego(pg, rng, flip=1):
    return baby(pg, rng, flip, "plates")


def baby_brachio(pg, rng, flip=1):
    return baby(pg, rng, flip, "longneck")


def baby_para(pg, rng, flip=1):
    return baby(pg, rng, flip, "crest")


def baby_anky(pg, rng, flip=1):
    return baby(pg, rng, flip, "club")


SPECIES = {
    "trex": trex, "allosaurus": allosaurus, "carnotaurus": carnotaurus,
    "ceratosaurus": ceratosaurus, "baryonyx": baryonyx, "spinosaurus": spinosaurus,
    "velociraptor": velociraptor, "deinonychus": deinonychus,
    "gallimimus": gallimimus, "compsognathus": compsognathus,
    "oviraptor": oviraptor, "ornithomimus": ornithomimus,
    "triceratops": triceratops, "styracosaurus": styracosaurus,
    "pachyrhinosaurus": pachyrhinosaurus, "protoceratops": protoceratops,
    "brachiosaurus": brachiosaurus, "diplodocus": diplodocus,
    "brontosaurus": brontosaurus, "apatosaurus": apatosaurus,
    "mamenchisaurus": mamenchisaurus,
    "stegosaurus": stegosaurus, "kentrosaurus": kentrosaurus,
    "ankylosaurus": ankylosaurus, "euoplocephalus": euoplocephalus,
    "pteranodon": pteranodon, "quetzalcoatlus": quetzalcoatlus,
    "rhamphorhynchus": rhamphorhynchus, "archaeopteryx": archaeopteryx,
    "dimorphodon": dimorphodon,
    "plesiosaurus": plesiosaurus, "mosasaurus": mosasaurus,
    "ichthyosaurus": ichthyosaurus, "elasmosaurus": elasmosaurus,
    "parasaurolophus": parasaurolophus, "corythosaurus": corythosaurus,
    "edmontosaurus": edmontosaurus, "pachycephalosaurus": pachycephalosaurus,
    "dilophosaurus": dilophosaurus,
    "baby_trex": baby_trex, "baby_trike": baby_trike, "baby_stego": baby_stego,
    "baby_brachio": baby_brachio, "baby_para": baby_para, "baby_anky": baby_anky,
}

SPECIES_NAME = {
    "trex": "T-Rex", "allosaurus": "Allosaurus", "carnotaurus": "Carnotaurus",
    "ceratosaurus": "Ceratosaurus", "baryonyx": "Baryonyx",
    "spinosaurus": "Spinosaurus", "velociraptor": "Velociraptor",
    "deinonychus": "Deinonychus", "gallimimus": "Gallimimus",
    "compsognathus": "Compsognathus", "oviraptor": "Oviraptor",
    "ornithomimus": "Ornithomimus", "triceratops": "Triceratops",
    "styracosaurus": "Styracosaurus", "pachyrhinosaurus": "Pachyrhinosaurus",
    "protoceratops": "Protoceratops", "brachiosaurus": "Brachiosaurus",
    "diplodocus": "Diplodocus", "brontosaurus": "Brontosaurus",
    "apatosaurus": "Apatosaurus", "mamenchisaurus": "Mamenchisaurus",
    "stegosaurus": "Stegosaurus", "kentrosaurus": "Kentrosaurus",
    "ankylosaurus": "Ankylosaurus", "euoplocephalus": "Euoplocephalus",
    "pteranodon": "Pteranodon", "quetzalcoatlus": "Quetzalcoatlus",
    "rhamphorhynchus": "Rhamphorhynchus", "archaeopteryx": "Archaeopteryx",
    "dimorphodon": "Dimorphodon", "plesiosaurus": "Plesiosaurus",
    "mosasaurus": "Mosasaurus", "ichthyosaurus": "Ichthyosaurus",
    "elasmosaurus": "Elasmosaurus", "parasaurolophus": "Parasaurolophus",
    "corythosaurus": "Corythosaurus", "edmontosaurus": "Edmontosaurus",
    "pachycephalosaurus": "Pachycephalosaurus", "dilophosaurus": "Dilophosaurus",
    "baby_trex": "Baby T-Rex", "baby_trike": "Baby Triceratops",
    "baby_stego": "Baby Stegosaurus", "baby_brachio": "Baby Long Neck",
    "baby_para": "Baby Parasaurolophus", "baby_anky": "Baby Ankylosaurus",
}

# Guide body color per species (for the colored sample kids copy).
SPECIES_COLOR = {
    "trex": "#66BB6A", "allosaurus": "#9575CD", "carnotaurus": "#EF5350",
    "ceratosaurus": "#FF8A65", "baryonyx": "#4DB6AC", "spinosaurus": "#42A5F5",
    "velociraptor": "#FFA726", "deinonychus": "#EC407A", "gallimimus": "#FFEE58",
    "compsognathus": "#AED581", "oviraptor": "#AB47BC", "ornithomimus": "#80DEEA",
    "triceratops": "#8D6E63", "styracosaurus": "#FF7043",
    "pachyrhinosaurus": "#90A4AE", "protoceratops": "#DCE775",
    "brachiosaurus": "#26A69A", "diplodocus": "#9CCC65",
    "brontosaurus": "#7986CB", "apatosaurus": "#81C784",
    "mamenchisaurus": "#4FC3F7", "stegosaurus": "#FF9800",
    "kentrosaurus": "#7CB342", "ankylosaurus": "#8D6E63",
    "euoplocephalus": "#A1887F", "pteranodon": "#F06292",
    "quetzalcoatlus": "#9575CD", "rhamphorhynchus": "#4DD0E1",
    "archaeopteryx": "#FF8A65", "dimorphodon": "#7986CB",
    "plesiosaurus": "#4FC3F7", "mosasaurus": "#78909C",
    "ichthyosaurus": "#29B6F6", "elasmosaurus": "#26C6DA",
    "parasaurolophus": "#FFB300", "corythosaurus": "#66BB6A",
    "edmontosaurus": "#8D6E63", "pachycephalosaurus": "#7E57C2",
    "dilophosaurus": "#26A69A",
    "baby_trex": "#81C784", "baby_trike": "#A1887F", "baby_stego": "#FFB74D",
    "baby_brachio": "#4DB6AC", "baby_para": "#FFD54F", "baby_anky": "#BCAAA4",
}

WATER_SPECIES = {"plesiosaurus", "mosasaurus", "ichthyosaurus", "elasmosaurus"}
FLY_SPECIES = {"pteranodon", "quetzalcoatlus", "rhamphorhynchus", "dimorphodon"}

CATEGORIES = [
    ("predators", "Big Predators",
     ["trex", "allosaurus", "carnotaurus", "ceratosaurus", "baryonyx", "spinosaurus"]),
    ("raptors", "Raptors & Speedsters",
     ["velociraptor", "deinonychus", "gallimimus", "compsognathus", "oviraptor", "ornithomimus"]),
    ("horned", "Horned & Frilled",
     ["triceratops", "styracosaurus", "pachyrhinosaurus", "protoceratops"]),
    ("longnecks", "Long Neck Giants",
     ["brachiosaurus", "diplodocus", "brontosaurus", "apatosaurus", "mamenchisaurus"]),
    ("armored", "Armored & Plated",
     ["stegosaurus", "kentrosaurus", "ankylosaurus", "euoplocephalus"]),
    ("flyers", "Sky Flyers",
     ["pteranodon", "quetzalcoatlus", "rhamphorhynchus", "archaeopteryx", "dimorphodon"]),
    ("sea", "Sea Monsters",
     ["plesiosaurus", "mosasaurus", "ichthyosaurus", "elasmosaurus"]),
    ("crested", "Crests & Duckbills",
     ["parasaurolophus", "corythosaurus", "edmontosaurus", "pachycephalosaurus", "dilophosaurus"]),
    ("babies", "Baby Dinos",
     ["baby_trex", "baby_trike", "baby_stego", "baby_brachio", "baby_para", "baby_anky"]),
    ("party", "Dino Party", None),
]

PARTY_POOL = ["trex", "triceratops", "stegosaurus", "brachiosaurus",
              "parasaurolophus", "pteranodon", "spinosaurus", "velociraptor",
              "ankylosaurus", "baby_trex"]


def water_scene(pg, rng):
    sky(pg)
    sun(pg, rng)
    if rng.random() < 0.8:
        cloud(pg, rng, rng.randint(250, 750), rng.randint(120, 220))
    pg.fill(f"M 0 {H} L 0 700 Q 256 660 512 700 Q 768 740 {W} 700 L {W} {H} Z", gc="#64B5F6")
    for wy in (790, 880):
        pg.fixed(open_quad([(80, wy), (180, wy - 30), (280, wy), (380, wy + 25), (480, wy)]), stroke=True, sw=7)
        pg.fixed(open_quad([(560, wy + 20), (660, wy - 12), (760, wy + 20), (860, wy + 45), (940, wy + 20)]), stroke=True, sw=7)


def fly_scene(pg, rng):
    sky(pg)
    sun(pg, rng)
    cloud(pg, rng, rng.randint(150, 400), rng.randint(500, 700))
    cloud(pg, rng, rng.randint(620, 880), rng.randint(550, 750))
    ground(pg, rng, y=900)


def land_scene(pg, rng, extras=True):
    sky(pg)
    if rng.random() < 0.75:
        sun(pg, rng)
    nclouds = rng.randint(0, 2)
    for i in range(nclouds):
        cloud(pg, rng, 220 + i * 470 + rng.randint(-60, 60), rng.randint(110, 240))
    ground(pg, rng)
    if extras:
        pick = rng.random()
        if pick < 0.3:
            volcano(pg, rng, rng.choice([230, 780]), 810)
        elif pick < 0.6:
            tree(pg, rng, rng.choice([150, 870]), 830)


def accessory(pg, rng, hx, hy, kind):
    if kind == "hat":
        # clamp: hat top (cy - 115) must stay inside the canvas even on
        # very long-necked species whose head sits near the top edge
        party_hat(pg, rng, hx, max(hy - 85, 140))
    elif kind == "balloon":
        balloon(pg, rng, min(900, max(120, hx + 230)), max(160, hy - 160))
    elif kind == "flower":
        flower(pg, rng, rng.choice([130, 900]), 830)
    elif kind == "butterfly":
        butterfly(pg, rng, min(920, max(100, hx + rng.choice([-260, 260]))), max(140, hy - 120))
    elif kind == "stars":
        for sx, sy in [(150, 150), (860, 190), (520, 100)]:
            star(pg, rng, sx + rng.randint(-30, 30), sy + rng.randint(-20, 20))
    elif kind == "rainbow":
        rainbow(pg, rng)
    elif kind == "egg":
        egg(pg, rng, rng.choice([170, 870]), 840, 0.9, cracked=rng.random() < 0.5)


ACC_NAME = {"hat": "with Party Hat", "balloon": "with Balloon", "flower": "with Flower",
            "butterfly": "and Butterfly", "stars": "under the Stars",
            "rainbow": "under a Rainbow", "egg": "and the Egg", "none": ""}


def build_page(idx, cat_key, species_list, rng):
    acc_kinds = ["none", "hat", "balloon", "flower", "butterfly", "stars", "rainbow", "egg"]
    if cat_key == "party":
        species = PARTY_POOL[idx % len(PARTY_POOL)]
        acc = ["hat", "balloon", "stars", "rainbow"][idx % 4]
    else:
        species = species_list[idx % len(species_list)]
        acc = acc_kinds[idx % len(acc_kinds)]
    name = SPECIES_NAME[species]
    title = f"{name} {ACC_NAME[acc]}".strip() + f" #{idx + 1}"
    pg = Page(f"{cat_key}_{idx+1:02d}", title, cat_key)
    flip = 1 if rng.random() < 0.6 else -1
    if species in WATER_SPECIES:
        water_scene(pg, rng)
    elif species in FLY_SPECIES:
        fly_scene(pg, rng)
    else:
        land_scene(pg, rng)
    if acc == "rainbow":
        rainbow(pg, rng)
    pg.use(SPECIES_COLOR.get(species, "#66BB6A"))
    hx, hy = SPECIES[species](pg, rng, flip)
    if acc not in ("none", "rainbow"):
        accessory(pg, rng, hx, hy, acc)
    if cat_key == "party" and rng.random() < 0.6:
        egg(pg, rng, rng.choice([150, 890]), 845, 0.8, cracked=True)
    return pg


def page_to_svg(pg, colored=False):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    for r in pg.regions:
        if r["kind"] == "fill":
            color = r.get("gc", "#FFFFFF") if colored else "#FFFFFF"
            parts.append(f'<path d="{r["d"]}" fill="{color}" stroke="#222222" stroke-width="6"/>')
        elif r.get("stroke"):
            parts.append(f'<path d="{r["d"]}" fill="none" stroke="{r.get("color", "#222222")}" stroke-width="{r.get("sw", 7)}" stroke-linecap="round"/>')
        else:
            parts.append(f'<path d="{r["d"]}" fill="{r.get("color", "#222222")}"/>')
    parts.append("</svg>")
    return "".join(parts)


PAGES_PER_CAT = 52   # 10 categories x 52 = 520 pages
FREE_PER_CAT = 11    # 10 x 11 = 110 free pages


def validate_bounds(catalog):
    """Ensure no path geometry is clipped by the 1024x1024 canvas border.
    Endpoints must stay inside the canvas; bezier control points get slack."""
    bad = []
    for p in catalog["pages"]:
        for r in p["regions"]:
            toks = r["d"].split()
            pairs = []
            i = 0
            while i < len(toks):
                t = toks[i]
                if t in ("M", "L"):
                    pairs.append((float(toks[i+1]), float(toks[i+2]), False))
                    i += 3
                elif t == "Q":
                    pairs.append((float(toks[i+1]), float(toks[i+2]), True))
                    pairs.append((float(toks[i+3]), float(toks[i+4]), False))
                    i += 5
                elif t == "C":
                    pairs.append((float(toks[i+1]), float(toks[i+2]), True))
                    pairs.append((float(toks[i+3]), float(toks[i+4]), True))
                    pairs.append((float(toks[i+5]), float(toks[i+6]), False))
                    i += 7
                else:
                    i += 1
            for x, y, ctrl in pairs:
                lim = 45 if ctrl else 3
                if x < -lim or x > W + lim or y < -lim or y > H + lim:
                    bad.append((p["id"], r["id"], round(x), round(y), "ctrl" if ctrl else "end"))
    return bad


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SVG_OUT, exist_ok=True)
    catalog = {"categories": [], "pages": []}
    total_free = 0
    species_seen = set()
    for ci, (cat_key, cat_title, species_list) in enumerate(CATEGORIES):
        catalog["categories"].append({"id": cat_key, "title": cat_title})
        for idx in range(PAGES_PER_CAT):
            rng = random.Random(ci * 100000 + idx * 7919 + 42)
            pg = build_page(idx, cat_key, species_list, rng)
            species_seen.add(pg.title.split(" #")[0].split(" with")[0].split(" and")[0].split(" under")[0])
            free = idx < FREE_PER_CAT
            if free:
                total_free += 1
            catalog["pages"].append({
                "id": pg.id,
                "title": pg.title,
                "category": cat_key,
                "free": free,
                "regions": pg.regions,
            })
            if idx < len(species_list or PARTY_POOL) + 1:
                with open(os.path.join(SVG_OUT, pg.id + ".svg"), "w") as fh:
                    fh.write(page_to_svg(pg))
                with open(os.path.join(SVG_OUT, pg.id + "_colored.svg"), "w") as fh:
                    fh.write(page_to_svg(pg, colored=True))
    with open(os.path.join(OUT, "pages.json"), "w") as fh:
        json.dump(catalog, fh, separators=(",", ":"))
    n = len(catalog["pages"])
    ids = set(p["id"] for p in catalog["pages"])
    assert len(ids) == n, "duplicate page ids!"
    # every fillable region must have a guide color (complete colored sample)
    missing_gc = [p["id"] for p in catalog["pages"]
                  for r in p["regions"] if r["kind"] == "fill" and "gc" not in r]
    assert not missing_gc, f"regions without guide color: {missing_gc[:10]}"
    bad = validate_bounds(catalog)
    if bad:
        for b in bad[:20]:
            print("BORDER CLIP:", b)
        raise SystemExit(f"border clipping in {len(bad)} points - fix before shipping")
    size_mb = os.path.getsize(os.path.join(OUT, "pages.json")) / 1e6
    print(f"OK pages={n} free={total_free} categories={len(CATEGORIES)} "
          f"species={len(SPECIES)} json={size_mb:.2f}MB bounds=0-clip gc=100%")


if __name__ == "__main__":
    main()
