#!/usr/bin/env python3
"""Generate 512 unique dino coloring pages as JSON + SVG previews.

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
    """Deterministic string hash (python hash() is randomized)."""
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) % 100003
    return h


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def ellipse(cx, cy, rx, ry, rot=0.0):
    """Ellipse as 4 cubic beziers, optional rotation (radians)."""
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

    def fill(self, d):
        self._n += 1
        self.regions.append({"id": f"r{self._n}", "d": d, "kind": "fill"})

    def fixed(self, d, color="#222222", stroke=False, sw=7):
        self._n += 1
        r = {"id": f"r{self._n}", "d": d, "kind": "fixed", "color": color}
        if stroke:
            r["stroke"] = True
            r["sw"] = sw
        self.regions.append(r)


# ---------- shared scenery ----------

def sky(pg):
    pg.fill(f"M 0 0 L {W} 0 L {W} {H} L 0 {H} Z")


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
    pg.fill(d)


def sun(pg, rng, cx=None, cy=170):
    cx = cx if cx is not None else rng.choice([150, 870])
    r = rng.randint(60, 85)
    pg.fill(ellipse(cx, cy, r, r))
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
    pg.fill(d)


def volcano(pg, rng, cx=820, base=800):
    w, h = rng.randint(180, 240), rng.randint(220, 300)
    pg.fill(
        f"M {f(cx-w)} {f(base)} Q {f(cx-w*0.35)} {f(base-h*0.75)} {f(cx-w*0.28)} {f(base-h)}"
        f" L {f(cx+w*0.28)} {f(base-h)} Q {f(cx+w*0.35)} {f(base-h*0.75)} {f(cx+w)} {f(base)} Z"
    )
    pg.fill(ellipse(cx, base - h - 55, 70, 42))


def tree(pg, rng, cx, base):
    th = rng.randint(120, 190)
    tw = rng.randint(22, 32)
    pg.fill(f"M {f(cx-tw)} {f(base)} L {f(cx-tw*0.6)} {f(base-th)} L {f(cx+tw*0.6)} {f(base-th)} L {f(cx+tw)} {f(base)} Z")
    pg.fill(ellipse(cx, base - th - 60, 85 + rng.randint(-10, 20), 70))


def flower(pg, rng, cx, cy):
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        pg.fill(ellipse(cx + math.cos(a) * 24, cy + math.sin(a) * 24, 17, 17))
    pg.fill(ellipse(cx, cy, 13, 13))
    pg.fixed(f"M {f(cx)} {f(cy+38)} L {f(cx)} {f(cy+85)}", stroke=True, sw=8)


def butterfly(pg, rng, cx, cy):
    pg.fill(ellipse(cx - 26, cy - 12, 26, 20, -0.4))
    pg.fill(ellipse(cx + 26, cy - 12, 26, 20, 0.4))
    pg.fill(ellipse(cx - 20, cy + 16, 18, 14, -0.3))
    pg.fill(ellipse(cx + 20, cy + 16, 18, 14, 0.3))
    pg.fixed(ellipse(cx, cy, 7, 24), "#222222")


def balloon(pg, rng, cx, cy):
    pg.fill(ellipse(cx, cy, 55, 68))
    pg.fixed(f"M {f(cx)} {f(cy+68)} Q {f(cx-18)} {f(cy+140)} {f(cx+8)} {f(cy+205)}", stroke=True, sw=6)


def party_hat(pg, rng, cx, cy, s=1.0):
    pg.fill(f"M {f(cx-52*s)} {f(cy)} L {f(cx)} {f(cy-115*s)} L {f(cx+52*s)} {f(cy)} Z")
    pg.fill(ellipse(cx, cy - 115 * s, 20 * s, 20 * s))


def egg(pg, rng, cx, cy, s=1.0, cracked=False):
    pg.fill(
        f"M {f(cx)} {f(cy-95*s)}"
        f" C {f(cx+58*s)} {f(cy-95*s)} {f(cx+72*s)} {f(cy-10*s)} {f(cx+70*s)} {f(cy+20*s)}"
        f" C {f(cx+66*s)} {f(cy+75*s)} {f(cx-66*s)} {f(cy+75*s)} {f(cx-70*s)} {f(cy+20*s)}"
        f" C {f(cx-72*s)} {f(cy-10*s)} {f(cx-58*s)} {f(cy-95*s)} {f(cx)} {f(cy-95*s)} Z"
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
    pg.fill(poly(pts))


def rainbow(pg, rng, cx=512, cy=340, r0=260):
    for i in range(3):
        r_out, r_in = r0 - i * 46, r0 - i * 46 - 40
        d = (
            f"M {f(cx-r_out)} {f(cy)}"
            f" C {f(cx-r_out)} {f(cy-r_out*1.32)} {f(cx+r_out)} {f(cy-r_out*1.32)} {f(cx+r_out)} {f(cy)}"
            f" L {f(cx+r_in)} {f(cy)}"
            f" C {f(cx+r_in)} {f(cy-r_in*1.32)} {f(cx-r_in)} {f(cy-r_in*1.32)} {f(cx-r_in)} {f(cy)} Z"
        )
        pg.fill(d)


def eye(pg, cx, cy, r=26, look=0.0):
    pg.fill(ellipse(cx, cy, r, r))
    pg.fixed(ellipse(cx + look * r * 0.3, cy, r * 0.42, r * 0.42), "#222222")


def smile(pg, cx, cy, w=60, up=28):
    pg.fixed(f"M {f(cx-w)} {f(cy)} Q {f(cx)} {f(cy+up)} {f(cx+w)} {f(cy)}", stroke=True, sw=9)


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
    pg.fill(ellipse(cx, cy, rx, ry))


def tail(pg, rng, x0, y0, flip=1, length=None, up=None):
    ln = length or rng.randint(230, 320)
    u = up or rng.randint(90, 170)
    d = (
        f"M {f(x0)} {f(y0-70)}"
        f" Q {f(x0+flip*ln*0.7)} {f(y0-u)} {f(x0+flip*ln)} {f(y0-u-30)}"
        f" Q {f(x0+flip*(ln*0.75))} {f(y0-20)} {f(x0)} {f(y0+55)} Z"
    )
    pg.fill(d)


# ---------- species builders ----------

def trex(pg, rng, flip=1, cx=470, cy=560):
    rx, ry = rng.randint(170, 200), rng.randint(140, 160)
    tail(pg, rng, cx - flip * rx * 0.8, cy, -flip)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.5, lw=52, lh=150)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx + flip * 20, cy + 35, rx * 0.55, ry * 0.55)
    hx, hy = cx + flip * (rx * 0.75), cy - ry - rng.randint(60, 100)
    pg.fill(ellipse(hx, hy, 120, 100))
    pg.fill(ellipse(hx + flip * 95, hy + 25, 70, 48))
    pg.fill(ellipse(cx + flip * (rx * 0.55), cy - 20, 55, 22, 0.5 * flip))
    pg.fill(ellipse(cx + flip * (rx * 0.62), cy + 40, 50, 20, 0.2 * flip))
    tx = hx + flip * 60
    pg.fixed(f"M {f(tx)} {f(hy+60)} L {f(tx+flip*22)} {f(hy+78)} L {f(tx+flip*44)} {f(hy+60)} L {f(tx+flip*66)} {f(hy+78)}", stroke=True, sw=7)
    eye(pg, hx + flip * 35, hy - 25, 26, flip * 0.5)
    smile(pg, hx + flip * 55, hy + 42, 40, 18)
    return hx, hy


def stego(pg, rng, flip=1, cx=500, cy=590):
    rx, ry = rng.randint(200, 235), rng.randint(130, 150)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=rng.randint(200, 260), up=60)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=44, lh=135, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    n = rng.choice([4, 5, 6])
    for i in range(n):
        t = i / (n - 1)
        px = cx - rx * 0.8 + t * rx * 1.6
        py = cy - ry * math.sqrt(max(0.05, 1 - ((px - cx) / rx) ** 2)) + 6
        s = 55 + 28 * math.sin(math.pi * t)
        pg.fill(f"M {f(px-s*0.7)} {f(py)} Q {f(px)} {f(py-s*1.7)} {f(px+s*0.7)} {f(py)} Z")
    hx, hy = cx + flip * (rx * 0.95), cy - 55
    pg.fill(ellipse(hx, hy, 88, 66))
    eye(pg, hx + flip * 26, hy - 12, 20, flip * 0.4)
    smile(pg, hx + flip * 40, hy + 22, 30, 14)
    sx = cx - flip * (rx + 110)
    for k in range(2):
        pg.fill(f"M {f(sx+k*36*flip)} {f(cy-130)} L {f(sx+k*36*flip+14)} {f(cy-195)} L {f(sx+k*36*flip+28)} {f(cy-130)} Z")
    return hx, hy


def trike(pg, rng, flip=1, cx=520, cy=590):
    rx, ry = rng.randint(190, 220), rng.randint(135, 155)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=200, up=50)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=46, lh=130, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    hx, hy = cx + flip * (rx * 0.9), cy - ry * 0.55
    pg.fill(ellipse(hx - flip * 30, hy - 30, 105, 120))
    pg.fill(ellipse(hx + flip * 30, hy, 95, 75))
    pg.fill(f"M {f(hx+flip*105)} {f(hy-10)} Q {f(hx+flip*165)} {f(hy+5)} {f(hx+flip*112)} {f(hy+42)} Z")
    pg.fill(f"M {f(hx+flip*10)} {f(hy-62)} L {f(hx+flip*28)} {f(hy-150)} L {f(hx+flip*52)} {f(hy-58)} Z")
    pg.fill(f"M {f(hx-flip*36)} {f(hy-66)} L {f(hx-flip*20)} {f(hy-148)} L {f(hx+flip*2)} {f(hy-60)} Z")
    pg.fill(f"M {f(hx+flip*74)} {f(hy+28)} L {f(hx+flip*118)} {f(hy+14)} L {f(hx+flip*82)} {f(hy+52)} Z")
    eye(pg, hx + flip * 52, hy - 8, 20, flip * 0.4)
    smile(pg, hx + flip * 92, hy + 34, 24, 12)
    return hx, hy


def brachio(pg, rng, flip=1, cx=470, cy=620):
    rx, ry = rng.randint(190, 220), rng.randint(140, 160)
    tail(pg, rng, cx - flip * rx * 0.85, cy, -flip, length=rng.randint(240, 300), up=80)
    legs(pg, rng, cx, cy + ry * 0.55, spread=rx * 0.55, lw=50, lh=140, n=4)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 40, rx * 0.6, ry * 0.5)
    nx = cx + flip * rx * 0.7
    top = rng.randint(150, 230)
    d = (
        f"M {f(nx-60)} {f(cy-40)}"
        f" Q {f(nx+flip*40)} {f(top+120)} {f(nx+flip*70)} {f(top)}"
        f" L {f(nx+flip*160)} {f(top+30)}"
        f" Q {f(nx+flip*90)} {f(top+220)} {f(nx+80)} {f(cy)} Z"
    )
    pg.fill(d)
    hx, hy = nx + flip * 115, top - 10
    pg.fill(ellipse(hx, hy, 85, 62))
    eye(pg, hx + flip * 22, hy - 12, 19, flip * 0.4)
    smile(pg, hx + flip * 38, hy + 20, 26, 12)
    return hx, hy


def ptero(pg, rng, flip=1, cx=512, cy=430):
    ww = rng.randint(300, 360)
    pg.fill(f"M {f(cx)} {f(cy)} Q {f(cx-ww*0.6)} {f(cy-190)} {f(cx-ww)} {f(cy-60)} Q {f(cx-ww*0.5)} {f(cy+40)} {f(cx-60)} {f(cy+60)} Z")
    pg.fill(f"M {f(cx)} {f(cy)} Q {f(cx+ww*0.6)} {f(cy-190)} {f(cx+ww)} {f(cy-60)} Q {f(cx+ww*0.5)} {f(cy+40)} {f(cx+60)} {f(cy+60)} Z")
    pg.fill(ellipse(cx, cy + 40, 95, 120))
    belly(pg, cx, cy + 70, 55, 70)
    hx, hy = cx, cy - 110
    pg.fill(ellipse(hx, hy, 78, 64))
    pg.fill(f"M {f(hx-flip*20)} {f(hy-52)} Q {f(hx-flip*130)} {f(hy-110)} {f(hx-flip*60)} {f(hy-20)} Z")
    pg.fill(f"M {f(hx+flip*60)} {f(hy-14)} L {f(hx+flip*175)} {f(hy+16)} L {f(hx+flip*62)} {f(hy+34)} Z")
    eye(pg, hx + flip * 22, hy - 10, 19, flip * 0.4)
    return hx, hy


def swimmer(pg, rng, flip=1, cx=500, cy=560):
    rx, ry = rng.randint(170, 200), rng.randint(95, 115)
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 25, rx * 0.6, ry * 0.5)
    pg.fill(ellipse(cx - 60, cy + ry - 8, 75, 30, 0.5))
    pg.fill(ellipse(cx + 80, cy + ry - 8, 75, 30, -0.4))
    nx = cx + flip * rx * 0.75
    top = rng.randint(200, 280)
    pg.fill(
        f"M {f(nx-50)} {f(cy-30)} Q {f(nx+flip*30)} {f(top+100)} {f(nx+flip*55)} {f(top)}"
        f" L {f(nx+flip*135)} {f(top+35)} Q {f(nx+flip*75)} {f(top+200)} {f(nx+70)} {f(cy+10)} Z"
    )
    hx, hy = nx + flip * 95, top - 5
    pg.fill(ellipse(hx, hy, 75, 55))
    eye(pg, hx + flip * 20, hy - 10, 18, flip * 0.4)
    smile(pg, hx + flip * 34, hy + 18, 24, 11)
    pg.fill(f"M {f(cx-flip*rx)} {f(cy-20)} Q {f(cx-flip*(rx+130))} {f(cy-90)} {f(cx-flip*(rx+90))} {f(cy+10)} Q {f(cx-flip*(rx+130))} {f(cy+80)} {f(cx-flip*rx)} {f(cy+30)} Z")
    return hx, hy


def baby_dino(pg, rng, flip=1, cx=512, cy=560, s=1.0):
    rx, ry = 150 * s, 140 * s
    pg.fill(ellipse(cx, cy, rx, ry))
    belly(pg, cx, cy + 30 * s, rx * 0.6, ry * 0.55)
    legs(pg, rng, cx, cy + ry * 0.6, spread=rx * 0.45, lw=38 * s, lh=85 * s)
    hx, hy = cx, cy - ry - 60 * s
    pg.fill(ellipse(hx, hy, 125 * s, 110 * s))
    eye(pg, hx - 45 * s, hy - 10, 30 * s, 0.3)
    eye(pg, hx + 45 * s, hy - 10, 30 * s, 0.3)
    smile(pg, hx, hy + 52 * s, 42 * s, 22 * s)
    tail(pg, rng, cx - flip * rx * 0.8, cy + 20, -flip, length=170, up=60)
    for k in (-1, 0, 1):
        px = hx + k * 46 * s
        pg.fill(f"M {f(px-20*s)} {f(hy-100*s)} Q {f(px)} {f(hy-160*s)} {f(px+20*s)} {f(hy-100*s)} Z")
    return hx, hy


SPECIES = {
    "trex": trex,
    "stego": stego,
    "trike": trike,
    "brachio": brachio,
    "ptero": ptero,
    "swimmer": swimmer,
    "baby": baby_dino,
}


def water_scene(pg, rng):
    sky(pg)
    sun(pg, rng)
    if rng.random() < 0.8:
        cloud(pg, rng, rng.randint(250, 750), rng.randint(120, 220))
    pg.fill(f"M 0 {H} L 0 700 Q 256 660 512 700 Q 768 740 {W} 700 L {W} {H} Z")
    for wy in (790, 880):
        pg.fixed(open_quad([(80, wy), (180, wy - 30), (280, wy), (380, wy + 25), (480, wy)]), stroke=True, sw=7)
        pg.fixed(open_quad([(560, wy + 20), (660, wy - 12), (760, wy + 20), (860, wy + 45), (940, wy + 20)]), stroke=True, sw=7)


def land_scene(pg, rng, extras=True):
    sky(pg)
    if rng.random() < 0.75:
        sun(pg, rng)
    nclouds = rng.randint(0, 2)
    for i in range(nclouds):
        cloud(pg, rng, 200 + i * 480 + rng.randint(-80, 80), rng.randint(110, 240))
    ground(pg, rng)
    if extras:
        pick = rng.random()
        if pick < 0.3:
            volcano(pg, rng, rng.choice([180, 840]), 810)
        elif pick < 0.6:
            tree(pg, rng, rng.choice([140, 880]), 830)


def accessory(pg, rng, hx, hy, kind):
    if kind == "hat":
        party_hat(pg, rng, hx, hy - 85)
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


TITLES = {
    "trex": "T-Rex", "stego": "Stegosaurus", "trike": "Triceratops",
    "brachio": "Long Neck", "ptero": "Pterodactyl", "swimmer": "Sea Dino",
    "baby": "Baby Dino",
}
ADJ = ["Happy", "Sleepy", "Playful", "Silly", "Friendly", "Curious", "Jolly",
       "Bouncy", "Giggly", "Sunny", "Cheerful", "Dancing", "Roaring", "Tiny",
       "Smiling", "Waving", "Jumping", "Singing", "Dreamy", "Brave"]
ACC_NAME = {"hat": "with Party Hat", "balloon": "with Balloon", "flower": "with Flower",
            "butterfly": "and Butterfly", "stars": "under the Stars", "rainbow": "under a Rainbow",
            "egg": "and the Egg", "none": ""}

CATEGORIES = [
    ("trex", "T-Rex Friends", "trex"),
    ("stego", "Spiky Stegos", "stego"),
    ("trike", "Horned Heroes", "trike"),
    ("brachio", "Long Necks", "brachio"),
    ("ptero", "Sky Flyers", "ptero"),
    ("swimmer", "Splashy Swimmers", "swimmer"),
    ("baby", "Baby Dinos", "baby"),
    ("party", "Dino Party", None),
]


def build_page(idx, cat_key, species, rng):
    acc_kinds = ["none", "hat", "balloon", "flower", "butterfly", "stars", "rainbow", "egg"]
    if cat_key == "party":
        species = rng.choice(["trex", "stego", "trike", "brachio", "baby"])
        acc = rng.choice(["hat", "balloon", "stars", "rainbow"])
    else:
        acc = acc_kinds[idx % len(acc_kinds)]
    adj = ADJ[(idx * 7 + (ci_hash(cat_key) % 13)) % len(ADJ)]
    title = f"{adj} {TITLES[species]} {ACC_NAME[acc]}".strip()
    title = f"{title} #{idx + 1}"
    pg = Page(f"{cat_key}_{idx+1:02d}", title, cat_key)
    flip = 1 if rng.random() < 0.6 else -1
    if species == "swimmer":
        water_scene(pg, rng)
    elif species == "ptero":
        sky(pg)
        sun(pg, rng)
        cloud(pg, rng, rng.randint(150, 400), rng.randint(500, 700))
        cloud(pg, rng, rng.randint(620, 880), rng.randint(550, 750))
        ground(pg, rng, y=900)
    else:
        land_scene(pg, rng)
    if acc == "rainbow":
        rainbow(pg, rng)
    hx, hy = SPECIES[species](pg, rng, flip)
    if acc not in ("none", "rainbow"):
        accessory(pg, rng, hx, hy, acc)
    if cat_key == "party" and rng.random() < 0.6:
        egg(pg, rng, rng.choice([150, 890]), 845, 0.8, cracked=True)
    return pg


def page_to_svg(pg):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    for r in pg.regions:
        if r["kind"] == "fill":
            parts.append(f'<path d="{r["d"]}" fill="#FFFFFF" stroke="#222222" stroke-width="6"/>')
        elif r.get("stroke"):
            parts.append(f'<path d="{r["d"]}" fill="none" stroke="{r.get("color", "#222222")}" stroke-width="{r.get("sw", 7)}" stroke-linecap="round"/>')
        else:
            parts.append(f'<path d="{r["d"]}" fill="{r.get("color", "#222222")}"/>')
    parts.append("</svg>")
    return "".join(parts)


PAGES_PER_CAT = 64   # 8 categories x 64 = 512 pages
FREE_PER_CAT = 13    # 8 x 13 = 104 free pages


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SVG_OUT, exist_ok=True)
    catalog = {"categories": [], "pages": []}
    total_free = 0
    for ci, (cat_key, cat_title, species) in enumerate(CATEGORIES):
        catalog["categories"].append({"id": cat_key, "title": cat_title})
        for idx in range(PAGES_PER_CAT):
            rng = random.Random(ci * 100000 + idx * 7919 + 42)
            pg = build_page(idx, cat_key, species, rng)
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
            if idx < 3:
                with open(os.path.join(SVG_OUT, pg.id + ".svg"), "w") as fh:
                    fh.write(page_to_svg(pg))
    with open(os.path.join(OUT, "pages.json"), "w") as fh:
        json.dump(catalog, fh, separators=(",", ":"))
    n = len(catalog["pages"])
    ids = set(p["id"] for p in catalog["pages"])
    assert len(ids) == n, "duplicate page ids!"
    size_mb = os.path.getsize(os.path.join(OUT, "pages.json")) / 1e6
    print(f"OK pages={n} free={total_free} categories={len(CATEGORIES)} json={size_mb:.2f}MB")


if __name__ == "__main__":
    main()
