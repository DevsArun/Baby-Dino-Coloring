#!/usr/bin/env python3
"""App icon: cute dino holding a crayon on a rainbow splash background.
Writes launcher mipmaps into android-overlay + a 512px Amazon listing icon
+ a 320x180 Fire TV leanback banner."""
import math
import os

import cairo

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIZE = 1024


def rounded_rect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def draw(cr):
    # soft cream background with vertical gradient
    g = cairo.LinearGradient(0, 0, 0, SIZE)
    g.add_color_stop_rgb(0, 1.0, 0.97, 0.88)
    g.add_color_stop_rgb(1, 1.0, 0.90, 0.75)
    rounded_rect(cr, 0, 0, SIZE, SIZE, 200)
    cr.set_source(g)
    cr.fill()

    # rainbow splash arcs behind dino
    rainbow = [(0.90, 0.22, 0.21), (0.98, 0.60, 0.01), (0.99, 0.85, 0.21),
               (0.30, 0.69, 0.31), (0.12, 0.53, 0.90), (0.56, 0.14, 0.67)]
    cx, cy = SIZE / 2, SIZE * 0.78
    for i, (r, g2, b) in enumerate(rainbow):
        cr.set_source_rgb(r, g2, b)
        cr.set_line_width(46)
        cr.arc(cx, cy, 470 - i * 52, math.pi * 1.05, math.pi * 1.95)
        cr.stroke()

    # dino body (green)
    body = (0.35, 0.72, 0.35)
    dark = (0.13, 0.13, 0.13)
    cr.set_source_rgb(*body)
    cr.save()
    cr.translate(cx, SIZE * 0.66)
    cr.scale(1.0, 0.92)
    cr.arc(0, 0, 250, 0, 2 * math.pi)
    cr.fill()
    cr.restore()
    # belly
    cr.set_source_rgb(0.85, 0.95, 0.75)
    cr.save()
    cr.translate(cx, SIZE * 0.72)
    cr.scale(1.0, 0.85)
    cr.arc(0, 0, 150, 0, 2 * math.pi)
    cr.fill()
    cr.restore()
    # head
    cr.set_source_rgb(*body)
    cr.arc(cx, SIZE * 0.36, 200, 0, 2 * math.pi)
    cr.fill()
    # head spikes
    cr.set_source_rgb(0.99, 0.65, 0.15)
    for dx in (-90, 0, 90):
        cr.move_to(cx + dx - 40, SIZE * 0.36 - 170)
        cr.curve_to(cx + dx, SIZE * 0.36 - 290, cx + dx, SIZE * 0.36 - 290,
                    cx + dx + 40, SIZE * 0.36 - 170)
        cr.close_path()
        cr.fill()
    # eyes
    for dx in (-75, 75):
        cr.set_source_rgb(1, 1, 1)
        cr.arc(cx + dx, SIZE * 0.33, 52, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgb(*dark)
        cr.arc(cx + dx + 8, SIZE * 0.335, 24, 0, 2 * math.pi)
        cr.fill()
    # smile
    cr.set_source_rgb(*dark)
    cr.set_line_width(16)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.arc(cx, SIZE * 0.38, 95, math.pi * 0.15, math.pi * 0.85)
    cr.stroke()
    # cheeks
    cr.set_source_rgba(0.95, 0.5, 0.5, 0.55)
    for dx in (-140, 140):
        cr.arc(cx + dx, SIZE * 0.41, 34, 0, 2 * math.pi)
        cr.fill()
    # arm + crayon
    cr.set_source_rgb(*body)
    cr.set_line_width(70)
    cr.move_to(cx + 190, SIZE * 0.62)
    cr.curve_to(cx + 300, SIZE * 0.56, cx + 330, SIZE * 0.50,
                cx + 330, SIZE * 0.44)
    cr.stroke()
    # crayon (red, tilted)
    cr.save()
    cr.translate(cx + 330, SIZE * 0.40)
    cr.rotate(-0.35)
    cr.set_source_rgb(0.90, 0.22, 0.21)
    rounded_rect(cr, -38, -10, 76, 200, 20)
    cr.fill()
    cr.move_to(-38, -10)
    cr.line_to(0, -85)
    cr.line_to(38, -10)
    cr.close_path()
    cr.fill()
    cr.restore()


def render(size):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    cr = cairo.Context(surf)
    cr.scale(size / SIZE, size / SIZE)
    draw(cr)
    return surf


def render_banner():
    """Fire TV leanback banner: 320x180."""
    w, h = 320, 180
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(surf)
    # background
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, 1.0, 0.97, 0.88)
    g.add_color_stop_rgb(1, 1.0, 0.90, 0.75)
    cr.set_source(g)
    cr.paint()
    # mini dino on the left (reuse main draw, scaled+cropped)
    cr.save()
    cr.translate(-70, -15)
    cr.scale(320 / SIZE, 320 / SIZE)
    draw(cr)
    cr.restore()
    # text
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(26)
    cr.set_source_rgb(0.15, 0.35, 0.15)
    cr.move_to(150, 80)
    cr.show_text("Baby Dino")
    cr.move_to(150, 112)
    cr.show_text("Coloring")
    return surf


def main():
    targets = {
        "mipmap-mdpi": 48, "mipmap-hdpi": 72, "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144, "mipmap-xxxhdpi": 192,
    }
    for folder, size in targets.items():
        out_dir = os.path.join(ROOT, "android-overlay", "app", "src", "main",
                               "res", folder)
        os.makedirs(out_dir, exist_ok=True)
        render(size).write_to_png(os.path.join(out_dir, "ic_launcher.png"))
    banner_dir = os.path.join(ROOT, "android-overlay", "app", "src", "main",
                              "res", "drawable-xhdpi")
    os.makedirs(banner_dir, exist_ok=True)
    render_banner().write_to_png(os.path.join(banner_dir, "banner.png"))
    store_dir = os.path.join(ROOT, "store")
    os.makedirs(store_dir, exist_ok=True)
    render(512).write_to_png(os.path.join(store_dir, "icon_512.png"))
    render(114).write_to_png(os.path.join(store_dir, "icon_114.png"))
    print("icons + banner written")


if __name__ == "__main__":
    main()
