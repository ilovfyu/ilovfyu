#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asset generator for ilovfyu's GitHub profile.

Theme: "Your Name" / 黄昏 (kataware-doki) dusk sky.
Emits light + dark SVG variants for banner / card / divider / footer.

Pure standard library, no network, deterministic (fixed random seeds).

Usage:
    python3 tools/build_assets.py
"""

import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

W = 1200          # banner width
H = 400           # banner height
HORIZON = 300     # water line

JP = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Yu Gothic','Noto Sans JP','Microsoft YaHei',system-ui,sans-serif"
UI = "'Avenir Next','Futura','Segoe UI',system-ui,-apple-system,'Helvetica Neue',sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


# --------------------------------------------------------------------------
# palettes
# --------------------------------------------------------------------------

P = {
    "dark": {
        "sky": [
            (0.00, "#080418"), (0.30, "#1b0c3c"), (0.52, "#3f1d68"),
            (0.68, "#7b2c73"), (0.80, "#bd4763"), (0.90, "#ef8551"),
            (1.00, "#ffc06a"),
        ],
        "water": [("0%", "#170c2c"), ("40%", "#100823"), ("100%", "#1a0f36")],
        "torii": "#06030e",
        "ridge_far": "#1a1038",
        "ridge_far_op": "0.75",
        "town": "#0a0518",
        "town_edge": "#3a2160",
        "star": "#fff6dd",
        "star_count": 78,
        "sun": "#ffd98a",
        "sun_r": 34,
        "glow_op": "0.55",
        "cloud": ["#6d3f8f", "#8e4a76", "#c05f6a"],
        "cloud_op": "0.30",
        "hairline": "#ffc477",
        "label": "#ffcf8a",
        "name_a": "#fff2c2",
        "name_b": "#ff9fc6",
        "sub": "#ffd9c0",
        "emblem": "#ffe6a8",
        "text_glow": "#1a0a33",
        "text_glow_op": "0.85",
        "card_bg": ["#150c33", "#251348"],
        "card_edge_a": "#ffc477",
        "card_edge_b": "#a97bff",
        "card_title_a": "#fff2c2",
        "card_title_b": "#ff9fc6",
        "card_text": "#e8d9ff",
        "card_muted": "#a98fd6",
        "card_row": "#3a2160",
        "light": "#ffd166",
        "window": "#ffd166",
        "waterline": "#ffbe74",
        "comet_a": "#fff6d8",
        "comet_b": "#ffd888",
        "comet_c": "#ff9ec4",
        "comet_d": "#a97bff",
        "sun_op": "0.85",
        "birds": "#c9a6ff",
        "birds_op": "0.5",
        # contribution heatmap: 5 levels, "the busier you are, the closer to sunset"
        "levels": ["#241a42", "#4a2a6b", "#8e3f7a", "#d9665f", "#ffc06a"],
        "grid_empty": "#1b1236",
    },
    "light": {
        "sky": [
            (0.00, "#3f7ad0"), (0.22, "#6f9ede"), (0.42, "#a9c0e6"),
            (0.58, "#e9c48f"), (0.72, "#ffb173"), (0.86, "#ff8f5f"),
            (1.00, "#ffd79a"),
        ],
        "water": [("0%", "#2b1c46"), ("40%", "#221638"), ("100%", "#3a2a58")],
        "torii": "#140d24",
        "ridge_far": "#6c5a9c",
        "ridge_far_op": "0.55",
        "town": "#241a42",
        "town_edge": "#4a3a72",
        "star": "#ffffff",
        "star_count": 14,
        "sun": "#fff3cf",
        "sun_r": 48,
        "glow_op": "0.75",
        "cloud": ["#ffffff", "#ffe3c2", "#ffc9a8"],
        "cloud_op": "0.55",
        "hairline": "#8a5a2b",
        "label": "#3a2f6e",
        "name_a": "#2b2a72",
        "name_b": "#8e2f63",
        "sub": "#3d3363",
        "emblem": "#ffb45c",
        "text_glow": "#ffffff",
        "text_glow_op": "0.75",
        "card_bg": ["#fff8ef", "#ffe9dc"],
        "card_edge_a": "#ff9a5c",
        "card_edge_b": "#8e5ad6",
        "card_title_a": "#2b2a72",
        "card_title_b": "#b8326e",
        "card_text": "#3d3363",
        "card_muted": "#8a7bb5",
        "card_row": "#e6d5ea",
        "light": "#ff9a3c",
        "window": "#ffb347",
        "waterline": "#ffcf8a",
        "comet_a": "#fffdf2",
        "comet_b": "#ffe0a0",
        "comet_c": "#ffb0cf",
        "comet_d": "#c39bff",
        "sun_op": "0.95",
        "birds": "#5b4a8a",
        "birds_op": "0.45",
        # contribution heatmap: 5 levels, "the busier you are, the closer to sunset"
        "levels": ["#efe4f2", "#cda9de", "#e07ba8", "#ff9a5c", "#ffc93c"],
        "grid_empty": "#f3ebf6",
    },
}


def f(v):
    """Compact number formatting."""
    return ("%.2f" % v).rstrip("0").rstrip(".")


def grad(id_, stops, x1="0", y1="0", x2="1", y2="0", units="objectBoundingBox"):
    body = "".join(
        '<stop offset="%s" stop-color="%s"%s/>' % (
            off if isinstance(off, str) else f(off), col,
            ' stop-opacity="%s"' % op if op is not None else "",
        )
        for off, col, op in ((s[0], s[1], s[2] if len(s) > 2 else None) for s in stops)
    )
    return ('<linearGradient id="%s" gradientUnits="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
            % (id_, units, x1, y1, x2, y2, body))


def vgrad(id_, stops, y1, y2):
    return grad(id_, stops, "0", str(y1), "0", str(y2), "userSpaceOnUse")


def radial(id_, stops, cx, cy, r):
    body = "".join(
        '<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (f(off), col, f(op))
        for off, col, op in stops
    )
    return ('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">%s</radialGradient>'
            % (id_, f(cx), f(cy), f(r), body))


# --------------------------------------------------------------------------
# scenery pieces
# --------------------------------------------------------------------------

def star_field(rnd, count, max_y, col, min_y=8):
    out = []
    for _ in range(count):
        x = rnd.uniform(0, W)
        y = rnd.uniform(min_y, max_y)
        # denser toward the top of the frame
        if rnd.random() < 0.45:
            y = rnd.uniform(min_y, max_y * 0.55)
        r = rnd.choice([0.7, 0.9, 1.0, 1.1, 1.4, 1.7])
        op = rnd.uniform(0.25, 0.95)
        dur = rnd.uniform(2.6, 5.4)
        beg = rnd.uniform(0, 5)
        out.append(
            '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s">'
            '<animate attributeName="opacity" values="%s;%s;%s" dur="%ss" begin="%ss" '
            'repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
            "</circle>" % (f(x), f(y), f(r), col, f(op), f(op), f(op * 0.2), f(op), f(dur), f(beg))
        )
    return "\n      ".join(out)


def clouds(rnd, spec, pal):
    """spec: list of (x, y, rx, ry, color_index, opacity, dur, travel)"""
    out = []
    for x, y, rx, ry, ci, op, dur, travel in spec:
        col = pal["cloud"][ci % len(pal["cloud"])]
        out.append(
            '<g opacity="%s" filter="url(#soft)">'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="0.7"/>'
            '<animateTransform attributeName="transform" type="translate" '
            'values="0 0; %s 0; 0 0" dur="%ss" repeatCount="indefinite"/>'
            "</g>" % (
                f(op), f(x), f(y), f(rx), f(ry), col,
                f(x + rx * 0.35), f(y - ry * 0.45), f(rx * 0.55), f(ry * 0.7), col,
                f(travel), f(dur),
            )
        )
    return "\n      ".join(out)


def shooting_star(rnd, x, y, length, angle, pal, dur):
    """A short meteor streak; fades in and out on a long loop."""
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    x2, y2 = x + dx * length, y + dy * length
    return (
        '<g opacity="0">'
        '<path d="M%s,%s L%s,%s" stroke="url(#streak)" stroke-width="1.6" stroke-linecap="round"/>'
        '<circle cx="%s" cy="%s" r="1.8" fill="#fffaf0"/>'
        '<animate attributeName="opacity" values="0;0;0.9;0" keyTimes="0;0.72;0.80;0.92" '
        'dur="%ss" begin="%ss" repeatCount="indefinite"/>'
        "</g>" % (f(x), f(y), f(x2), f(y2), f(x2), f(y2), f(dur), f(rnd.uniform(0, 12)))
    )


def wedge_pts(hx, hy, angle, off_deg, ln, w0, w1, gid, op):
    """A tapered comet-tail filament: narrow at the head, flaring out behind."""
    aa = math.radians(angle + off_deg)
    ddx, ddy = math.cos(aa), -math.sin(aa)
    nnx, nny = -ddy, ddx
    p = [
        (hx + nnx * w0, hy + nny * w0),
        (hx - nnx * w0, hy - nny * w0),
        (hx + ddx * ln - nnx * w1, hy + ddy * ln - nny * w1),
        (hx + ddx * ln + nnx * w1, hy + ddy * ln + nny * w1),
    ]
    pts = " ".join("%s,%s" % (f(px), f(py)) for px, py in p)
    return '<polygon points="%s" fill="url(#%s)" opacity="%s"/>' % (pts, gid, f(op))


def comet_grads(head, angle, length, pal, glow_r=34):
    """Gradients for a comet, aligned with its own head + tail direction."""
    hx, hy = head
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    ex, ey = hx + dx * length, hy + dy * length

    def g(id_, stops):
        return grad(id_, stops, str(hx), str(hy), str(ex), str(ey), "userSpaceOnUse")

    return "\n    ".join([
        radial("headGlow", [(0.0, "#fffbe8", 1.0), (0.22, pal["comet_b"], 0.55),
                            (0.55, pal["comet_c"], 0.16), (1.0, pal["comet_c"], 0.0)], hx, hy, glow_r),
        g("cMain", [(0.0, pal["comet_a"], "0.95"), (0.12, pal["comet_b"], "0.80"),
                    (0.45, pal["comet_c"], "0.34"), (1.0, pal["comet_d"], "0.0")]),
        g("cSplit", [(0.0, pal["comet_a"], "0.85"), (0.20, pal["comet_c"], "0.55"),
                     (1.0, pal["comet_d"], "0.0")]),
        g("cThin", [(0.0, "#ffffff", "0.9"), (0.30, pal["comet_b"], "0.45"),
                    (1.0, pal["comet_d"], "0.0")]),
        g("cGlow", [(0.0, pal["comet_b"], "0.42"), (0.5, pal["comet_c"], "0.18"),
                    (1.0, pal["comet_d"], "0.0")]),
    ])


def comet(head, angle, length, pal, scale=1.0):
    """The splitting comet (Tiamat). Head at `head`, filaments sweeping behind it."""
    hx, hy = head
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    nx, ny = -dy, dx          # perpendicular

    def wedge(off_deg, ln, w0, w1, gid, op):
        return wedge_pts(hx, hy, angle, off_deg, ln, w0, w1, gid, op)

    # slim filaments + a faint haze, so the comet reads as a comet and not a beam
    parts = [
        wedge(1.5, length * 1.02, 4.5 * scale, 26 * scale, "cGlow", 0.16),
        wedge(0.0, length * 1.00, 3.2 * scale, 8.5 * scale, "cMain", 0.95),
        wedge(7.5, length * 0.78, 2.2 * scale, 6.0 * scale, "cSplit", 0.78),
        wedge(-6.0, length * 0.90, 1.6 * scale, 4.2 * scale, "cThin", 0.62),
        wedge(14.0, length * 0.52, 1.3 * scale, 4.8 * scale, "cSplit", 0.50),
    ]

    # sparkles trailing off the head
    sparks = []
    for i in range(9):
        t = rnd.uniform(0.06, 1.0)
        jitter = rnd.uniform(-1, 1) * 22 * scale
        sx = hx + dx * length * t + nx * jitter * t
        sy = hy + dy * length * t + ny * jitter * t
        sparks.append(
            '<circle cx="%s" cy="%s" r="%s" fill="#fff8e2" opacity="%s">'
            '<animate attributeName="opacity" values="%s;0;%s" dur="%ss" repeatCount="indefinite"/>'
            "</circle>" % (
                f(sx), f(sy), f(rnd.uniform(0.8, 2.1)), f(rnd.uniform(0.3, 0.85)),
                f(rnd.uniform(0.4, 0.9)), f(rnd.uniform(0.4, 0.9)), f(rnd.uniform(2.0, 4.5)),
            )
        )

    return (
        '<g>\n        %s\n        <animateTransform attributeName="transform" type="translate" '
        'values="0 0; -14 9; 0 0" dur="26s" repeatCount="indefinite"/>\n'
        "        <circle cx=\"%s\" cy=\"%s\" r=\"%s\" fill=\"url(#headGlow)\"/>\n"
        '        <ellipse cx="%s" cy="%s" rx="%s" ry="2.1" fill="url(#flareH)" opacity="0.8"/>\n'
        '        <ellipse cx="%s" cy="%s" rx="1.5" ry="%s" fill="url(#flareV)" opacity="0.55"/>\n'
        '        <circle cx="%s" cy="%s" r="%s" fill="#fffdf5"/>\n'
        "        %s\n      </g>" % (
            "\n        ".join(parts),
            f(hx), f(hy), f(30 * scale),
            f(hx), f(hy), f(80 * scale),
            f(hx), f(hy), f(48 * scale),
            f(hx), f(hy), f(6.4 * scale),
            "\n        ".join(sparks),
        )
    )


def ridge(rnd, count, base_y, amp, fill, op, sharp=0.0):
    pts = []
    for i in range(count + 1):
        x = W * i / count
        y = base_y - amp * (0.30 + 0.70 * rnd.random() ** (1.0 - sharp * 0.6))
        pts.append((x, y))
    d = "M%s,%s L%s,%s " % (f(pts[0][0]), f(base_y), f(pts[0][0]), f(pts[0][1]))
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d += "Q%s,%s %s,%s " % (f(x0), f(y0), f(mx), f(my))
    d += "L%s,%s L%s,%s Z" % (f(pts[-1][0]), f(pts[-1][1]), f(pts[-1][0]), f(base_y))
    return '<path d="%s" fill="%s" opacity="%s"/>' % (d, fill, op)


def town(rnd, pal):
    """Silhouetted town skyline sitting on the horizon, with lit windows."""
    builds = []
    x = -20.0
    while x < W + 20:
        bw = rnd.uniform(20, 54)
        bh = rnd.uniform(10, 46)
        builds.append((x, bw, bh))
        x += bw + rnd.uniform(1, 9)

    body = []
    for bx, bw, bh in builds:
        top = HORIZON - bh
        body.append('<rect x="%s" y="%s" width="%s" height="%s"/>' % (f(bx), f(top), f(bw), f(bh + 4)))
    # a landmark tower + a thin antenna (reads as a tower, not a cross)
    tx = rnd.uniform(320, 520)
    body.append('<rect x="%s" y="%s" width="16" height="62"/>' % (f(tx), f(HORIZON - 58)))
    body.append('<rect x="%s" y="%s" width="9" height="14"/>' % (f(tx + 3.5), f(HORIZON - 72)))
    body.append('<rect x="%s" y="%s" width="2" height="20"/>' % (f(tx + 7), f(HORIZON - 92)))
    ax = rnd.uniform(760, 940)
    body.append('<rect x="%s" y="%s" width="3" height="52"/>' % (f(ax), f(HORIZON - 46)))

    windows = []
    for bx, bw, bh in builds:
        if bw < 24 or bh < 18:
            continue
        cols = max(1, int(bw // 11))
        rows = max(1, int(bh // 12))
        for c in range(cols):
            for r in range(rows):
                if rnd.random() > 0.42:
                    continue
                wx = bx + 5 + c * 11
                wy = HORIZON - bh + 5 + r * 12
                if wy > HORIZON - 4:
                    continue
                op = rnd.uniform(0.45, 1.0)
                windows.append(
                    '<rect x="%s" y="%s" width="3.4" height="4.2" fill="%s" opacity="%s">'
                    '<animate attributeName="opacity" values="%s;%s;%s" dur="%ss" begin="%ss" '
                    'repeatCount="indefinite"/></rect>' % (
                        f(wx), f(wy), pal["window"], f(op), f(op), f(op * 0.25), f(op),
                        f(rnd.uniform(3, 9)), f(rnd.uniform(0, 8)),
                    )
                )

    return (
        '<g fill="%s">%s</g>\n      <g>%s</g>' % (pal["town"], "".join(body), "".join(windows))
    ), buildings_to_reflections(builds, pal), '<g fill="%s">%s</g>' % (pal["town"], "".join(body))


def buildings_to_reflections(builds, pal):
    """Warm light streaks in the water directly under lit windows."""
    out = []
    for bx, bw, bh in builds:
        if rnd.random() > 0.5:
            continue
        rx = bx + bw / 2 + rnd.uniform(-6, 6)
        ln = rnd.uniform(10, 40)
        out.append(
            '<rect x="%s" y="%s" width="2.6" height="%s" fill="%s" opacity="%s">'
            '<animate attributeName="opacity" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>'
            "</rect>" % (
                f(rx), f(HORIZON + 3), f(ln), pal["window"], f(rnd.uniform(0.10, 0.30)),
                "0.10", "0.30", "0.10", f(rnd.uniform(4, 10)),
            )
        )
    return "".join(out)


def glitter(rnd, cx, top, bottom, col, count=90):
    """The sun's broken reflection: short warm dashes fanning out across the water."""
    out = []
    y = top + 5.0
    span = float(bottom - top)
    while y < bottom - 3:
        t = (y - top) / span                       # 0 at the waterline, 1 at the frame edge
        spread = 34 + 290 * t
        for _ in range(1 + int(5 * t) + rnd.randint(0, 2)):
            x = cx + rnd.uniform(-spread, spread)
            w = rnd.uniform(9, 34) * (0.45 + t)
            h = rnd.uniform(1.1, 2.4)
            op = min(0.85, (1.0 - t) ** 1.15 * rnd.uniform(0.22, 0.80))
            out.append(
                '<rect x="%s" y="%s" width="%s" height="%s" rx="1" fill="%s" opacity="%s">'
                '<animate attributeName="opacity" values="%s;%s;%s" dur="%ss" begin="%ss" '
                'repeatCount="indefinite"/></rect>' % (
                    f(x), f(y), f(w), f(h), col, f(op), f(op), f(op * 0.3), f(op),
                    f(rnd.uniform(3.0, 7.5)), f(rnd.uniform(0, 6)),
                )
            )
        y += rnd.uniform(3.6, 7.0)
    return '<g filter="url(#soft2)">%s</g>' % "".join(out[:count])


def torii(x, base_y, h, w, fill, op, reflection=True, rim=None):
    """A small torii standing in the water, with its reflection."""
    post = w * 0.085
    top = base_y - h
    g = [
        # uprights
        '<rect x="%s" y="%s" width="%s" height="%s" rx="1.4"/>' % (f(x - w / 2), f(top + h * 0.10), f(post), f(h * 0.90)),
        '<rect x="%s" y="%s" width="%s" height="%s" rx="1.4"/>' % (f(x + w / 2 - post), f(top + h * 0.10), f(post), f(h * 0.90)),
        # nuki (lower beam)
        '<rect x="%s" y="%s" width="%s" height="%s" rx="1"/>' % (f(x - w * 0.40), f(top + h * 0.22), f(w * 0.80), f(h * 0.055)),
        # kasagi (top beam, gently curved)
        '<path d="M%s,%s Q%s,%s %s,%s L%s,%s Q%s,%s %s,%s Z"/>' % (
            f(x - w * 0.60), f(top + h * 0.10),
            f(x), f(top - h * 0.02),
            f(x + w * 0.60), f(top + h * 0.10),
            f(x + w * 0.60), f(top + h * 0.10 + h * 0.06),
            f(x), f(top + h * 0.05),
            f(x - w * 0.60), f(top + h * 0.10 + h * 0.06),
        ),
        # shimaki
        '<rect x="%s" y="%s" width="%s" height="%s" rx="1"/>' % (f(x - w * 0.46), f(top + h * 0.17), f(w * 0.92), f(h * 0.05)),
    ]
    body = '<g fill="%s" opacity="%s"%s>%s</g>' % (
        fill, op,
        ' stroke="%s" stroke-width="0.9" stroke-opacity="0.4"' % rim if rim else "",
        "".join(g),
    )
    if reflection:
        # mirror the whole torii around the water line (y -> 2*base_y - y)
        body += ('<g fill="%s" opacity="%s" transform="matrix(1,0,0,-1,0,%s)">%s</g>'
                 % (fill, f(float(op) * 0.30), f(base_y * 2), "".join(g)))
    return body


def reeds(rnd, x0, direction, base_y, col, op, n=8, hmax=60):
    out = []
    for i in range(n):
        x = x0 + direction * i * rnd.uniform(11, 20)
        h = rnd.uniform(hmax * 0.45, hmax)
        bend = direction * rnd.uniform(6, 22)
        w = rnd.uniform(1.6, 2.8)
        out.append(
            '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="%s" fill="none" '
            'stroke-linecap="round"/>' % (
                f(x), f(base_y), f(x + bend * 0.4), f(base_y - h * 0.6),
                f(x + bend), f(base_y - h), col, f(w),
            )
        )
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>'
                   % (f(x + bend), f(base_y - h - 3), f(rnd.uniform(2.2, 3.4)), f(rnd.uniform(4, 7)), col))
    return '<g opacity="%s">%s</g>' % (op, "".join(out))


def birds(rnd, pal):
    """Faint distant birds; kept clear of the centred title block."""
    out = []
    for _ in range(rnd.randint(3, 5)):
        x = rnd.uniform(70, 340) if rnd.random() < 0.5 else rnd.uniform(860, 1120)
        y = rnd.uniform(60, 200)
        s = rnd.uniform(4, 9)
        out.append(
            '<path d="M%s,%s q%s,%s %s,0 q%s,%s %s,0" stroke="%s" stroke-width="1.5" fill="none" '
            'stroke-linecap="round" opacity="%s">'
            '<animateTransform attributeName="transform" type="translate" values="0 0; %s %s; 0 0" '
            'dur="%ss" repeatCount="indefinite"/></path>' % (
                f(x), f(y), f(s * 0.5), f(-s * 0.55), f(s), f(s * 0.5), f(-s * 0.55), f(s),
                pal["birds"], pal["birds_op"], f(rnd.uniform(-30, 30)), f(rnd.uniform(-8, 8)),
                f(rnd.uniform(16, 30)),
            )
        )
    return "".join(out)


# --------------------------------------------------------------------------
# banner
# --------------------------------------------------------------------------

def banner(theme):
    global rnd
    rnd = random.Random(2024 if theme == "dark" else 4096)
    pal = P[theme]
    sky_stops = [(off, col) for off, col in pal["sky"]]

    comet_len = 340 if theme == "dark" else 300
    comet_head = (912, 156) if theme == "dark" else (930, 132)

    cloud_spec = (
        [(150, 168, 132, 15, 0, 0.34, 26, 36),
         (1010, 214, 150, 13, 1, 0.30, 32, -30),
         (612, 258, 226, 19, 2, 0.24, 38, 28),
         (250, 236, 158, 14, 0, 0.22, 30, -24),
         (352, 108, 112, 11, 1, 0.20, 34, 30)]
        if theme == "dark" else
        [(190, 196, 140, 16, 0, 0.60, 28, 34),
         (960, 152, 158, 14, 1, 0.55, 34, -32),
         (600, 250, 236, 20, 2, 0.45, 40, 26),
         (1010, 236, 150, 13, 1, 0.42, 30, -22),
         (300, 96, 118, 12, 0, 0.35, 32, 28)]
    )

    town_svg, reflect_svg, town_body = town(rnd, pal)
    ridge_path = ridge(rnd, 16, HORIZON, 62 if theme == "dark" else 56,
                       pal["ridge_far"], pal["ridge_far_op"], 0.5)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" width="1200" height="400" role="img" aria-labelledby="t d">
  <title id="t">ilovfyu — 黄昏 / dusk sky</title>
  <desc id="d">An illustrated twilight sky with a splitting comet, silhouetted mountains, a small town and its reflection on still water.</desc>
  <defs>
    {sky}
    {water}
    {sunGlow}
    {cometGrads}
    {streak}
    {flareH}
    {flareV}
    {nameFill}
    {reflMask}
    {soft}
    {soft2}
    {textShadow}
  </defs>

  <rect width="1200" height="400" fill="url(#skyG)"/>

  <g>
      {stars}
  </g>

  <g opacity="{sun_op}">
    <circle cx="600" cy="{sun_y}" r="250" fill="url(#sunGlow)"/>
    <circle cx="600" cy="{sun_y}" r="{sun_r}" fill="{sun}" opacity="0.95"/>
    <circle cx="600" cy="{sun_y}" r="{sun_r2}" fill="#fffbe9" opacity="0.9"/>
  </g>

  <g>
      {clouds}
  </g>

  <g>
      {shooting}
  </g>

  <g>
      {birds}
  </g>

  <g>
      {comet}
  </g>

  <g>
      {ridge_far}
  </g>

  <g>
      {town_svg}
  </g>

  <rect x="0" y="{horizon}" width="1200" height="{water_h}" fill="url(#waterG)"/>
  <ellipse cx="600" cy="{horizon}" rx="560" ry="18" fill="url(#sunGlow)" opacity="0.35"/>

  <!-- inverted scenery: what makes the water read as water -->
  <g mask="url(#reflMask)" filter="url(#soft2)" transform="matrix(1,0,0,-1,0,{mirror})">
    <g opacity="0.30">{ridge_far}</g>
    <g opacity="0.55">{town_body}</g>
  </g>

  <g>
      {glitter}
  </g>

  <g filter="url(#soft2)" opacity="0.5">
      <rect x="{comet_x2}" y="{horizon}" width="20" height="82" fill="url(#streak)"/>
  </g>
  <g filter="url(#soft2)">
      {reflections}
  </g>

  {torii}

  <line x1="0" y1="{horizon}" x2="1200" y2="{horizon}" stroke="{waterline}" stroke-width="1.2" opacity="0.45"/>

  <g text-anchor="middle" font-family="{ui}">
    <g filter="url(#textShadow)">
      <text x="600" y="86" font-size="13.5" letter-spacing="11" fill="{label}" opacity="0.92">{label_text}</text>
      <text x="600" y="176" font-size="92" font-weight="700" letter-spacing="3" fill="url(#nameFill)">ilovfyu</text>
      <text x="600" y="222" font-size="18.5" letter-spacing="6.5" fill="{sub}" opacity="0.95">{sub_text}</text>
    </g>
    <path d="M470,104 L600,104 M600,104 L730,104" stroke="{hairline}" stroke-width="1" opacity="0.55"/>
    <path d="M600,96 l4.6,8 l-4.6,8 l-4.6,-8 Z" fill="{hairline}" opacity="0.85"/>
  </g>
</svg>
""".format(
        sky=vgrad("skyG", sky_stops, 0, HORIZON),
        water=vgrad("waterG", pal["water"], HORIZON, H),
        sunGlow=radial("sunGlow", [(0.0, "#fff6d0", 0.85 if theme == "light" else 0.62),
                                   (0.35, pal["sun"], 0.42 if theme == "light" else 0.28),
                                   (0.72, "#ff8f5f", 0.12),
                                   (1.0, "#ff8f5f", 0.0)], 600, HORIZON - 6, 250),
        cometGrads=comet_grads(comet_head, 27, comet_len, pal),
        streak=grad("streak", [(0.0, "#fff8e2", "0.55"), (1.0, "#fff8e2", "0.0")], "0", "0", "0", "1"),
        nameFill=grad("nameFill", [(0.0, pal["name_a"]), (1.0, pal["name_b"])]),
        reflMask=('<linearGradient id="reflFade" gradientUnits="userSpaceOnUse" x1="0" y1="%s" x2="0" y2="%s">'
                  '<stop offset="0" stop-color="#fff" stop-opacity="0.75"/>'
                  '<stop offset="0.55" stop-color="#fff" stop-opacity="0.22"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  '<mask id="reflMask"><rect x="0" y="%s" width="1200" height="%s" fill="url(#reflFade)"/></mask>'
                  % (HORIZON, H, HORIZON, H - HORIZON)),
        soft='<filter id="soft" x="-30%" y="-140%" width="160%" height="380%"><feGaussianBlur stdDeviation="9"/></filter>',
        soft2='<filter id="soft2" x="-15%" y="-15%" width="130%" height="130%"><feGaussianBlur stdDeviation="1.8"/></filter>',
        flareH=grad("flareH", [(0.0, "#fff6d8", "0.0"), (0.5, "#fffdf5", "0.95"), (1.0, "#fff6d8", "0.0")]),
        flareV=grad("flareV", [(0.0, "#fff6d8", "0.0"), (0.5, "#fffdf5", "0.85"), (1.0, "#fff6d8", "0.0")],
                    "0", "0", "0", "1"),
        textShadow=('<filter id="textShadow" x="-20%%" y="-40%%" width="140%%" height="200%%">'
                    '<feDropShadow dx="0" dy="1.5" stdDeviation="7" flood-color="%s" flood-opacity="%s"/>'
                    "</filter>" % (pal["text_glow"], pal["text_glow_op"])),
        stars=star_field(rnd, pal["star_count"], HORIZON - 40, pal["star"]),
        sun_y=HORIZON - (4 if theme == "dark" else 9),
        sun_r=pal["sun_r"],
        sun=pal["sun"],
        comet_b=pal["comet_b"],
        sun_r2=pal["sun_r"] * 0.62,
        sun_op=pal["sun_op"],
        clouds=clouds(rnd, cloud_spec, pal),
        shooting="\n      ".join(
            shooting_star(rnd, rnd.uniform(80, 420), rnd.uniform(40, 120), rnd.uniform(60, 130), -32, pal,
                          rnd.uniform(9, 16)) for _ in range(2)
        ),
        birds=birds(rnd, pal),
        comet=comet(comet_head, 27, comet_len, pal),
        ridge_far=ridge_path,
        town_svg=town_svg,
        town_body=town_body,
        mirror=HORIZON * 2,
        horizon=HORIZON,
        water_h=H - HORIZON,
        water_h2=(H - HORIZON) - 8,
        comet_x=comet_head[0],
        comet_x2=comet_head[0],
        reflections=reflect_svg,
        glitter=glitter(rnd, 600, HORIZON, H, pal["window"]),
        torii=torii(286, 392, 96, 86, pal["torii"], "1", rim=pal["window"]),
        waterline=pal["waterline"],
        reeds_l=reeds(rnd, 26, -1 if False else 1, H, pal["town"], "0.9", n=7, hmax=66),
        reeds_r=reeds(rnd, 1176, -1, H, pal["town"], "0.9", n=7, hmax=58),
        ui=UI,
        label_text="KATAWARE-DOKI · 黄昏",
        sub_text="爱自由 · LOVE FREEDOM · 結び",
        hairline=pal["hairline"],
        label=pal["label"],
        sub=pal["sub"],
    )
    return svg


# --------------------------------------------------------------------------
# divider
# --------------------------------------------------------------------------

def divider(theme):
    pal = P[theme]
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 56" width="1200" height="56" role="img" aria-label="section divider">
  <defs>
    {line}
    {emblem}
    <filter id="dglow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
  </defs>
  <path d="M110,30 Q360,12 600,29 Q840,46 1090,26" stroke="url(#divLine)" stroke-width="1.6" fill="none"/>
  <g filter="url(#dglow)" opacity="0.55">
    <path d="M600,20 l5,9 l-5,9 l-5,-9 Z" fill="{emblem}"/>
  </g>
  <path d="M600,20 l5,9 l-5,9 l-5,-9 Z" fill="{emblem}">
    <animate attributeName="opacity" values="0.55;1;0.55" dur="4.5s" repeatCount="indefinite"/>
  </path>
  <path d="M368,23 l3,5.5 l-3,5.5 l-3,-5.5 Z" fill="{line_c}" opacity="0.8">
    <animate attributeName="opacity" values="0.8;0.25;0.8" dur="3.6s" begin="0.6s" repeatCount="indefinite"/>
  </path>
  <path d="M806,27 l3,5.5 l-3,5.5 l-3,-5.5 Z" fill="{line_c}" opacity="0.8">
    <animate attributeName="opacity" values="0.8;0.25;0.8" dur="3.9s" begin="1.4s" repeatCount="indefinite"/>
  </path>
  <circle cx="210" cy="27" r="1.6" fill="{line_c}" opacity="0.6"/>
  <circle cx="990" cy="30" r="1.6" fill="{line_c}" opacity="0.6"/>
</svg>
""".format(
        line=grad("divLine", [(0.0, pal["hairline"], "0.0"), (0.18, pal["hairline"], "0.75"),
                              (0.5, pal["emblem"], "1.0"), (0.82, pal["hairline"], "0.75"),
                              (1.0, pal["hairline"], "0.0")]),
        emblem=pal["emblem"],
        line_c=pal["hairline"],
    )


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------

def footer(theme):
    global rnd
    rnd = random.Random(77 if theme == "dark" else 91)
    pal = P[theme]

    if theme == "dark":
        sky = [(0.00, "#05030f"), (0.34, "#1a0b38"), (0.62, "#3d1b63"), (0.84, "#87356c"), (1.00, "#e8814f")]
    else:
        sky = [(0.00, "#2f6ac4"), (0.30, "#7fa5dd"), (0.55, "#dfc194"), (0.78, "#ffab73"), (1.00, "#ff9a63")]

    hills = ridge(rnd, 13, 260, 54, pal["town"], "0.95", 0.4)
    hills2 = ridge(rnd, 9, 260, 30, pal["ridge_far"], "0.55", 0.2)

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 260" width="1200" height="260" role="img" aria-labelledby="ft fd">
  <title id="ft">ilovfyu — footer</title>
  <desc id="fd">A twilight sky with stars and a comet trail over silhouetted hills.</desc>
  <defs>
    {sky}
    {nameFill}
    {cometGrads}
    {textShadow}
  </defs>

  <rect width="1200" height="260" fill="url(#fSky)"/>

  <g>{stars}</g>

  <g opacity="{birds_op}">{birds}</g>

  <g>
    {comet}
  </g>

  {hills2}
  {hills}

  <g text-anchor="middle" font-family="{jp}">
    <g filter="url(#textShadow)">
      <text x="600" y="104" font-size="50" font-weight="700" letter-spacing="10" fill="url(#nameFill)">爱自由.</text>
      <text x="600" y="142" font-size="12.5" letter-spacing="7.5" fill="{muted}" font-family="{mono}">KATAWARE-DOKI · 結び · 彗星</text>
      <text x="600" y="176" font-size="13" letter-spacing="2.4" fill="{muted}">Thanks for stopping by — またね。</text>
    </g>
  </g>

  <text x="600" y="242" text-anchor="middle" font-family="{mono}" font-size="11" letter-spacing="3" fill="{handle}" opacity="0.8">github.com/ilovfyu</text>
</svg>
""".format(
        sky=vgrad("fSky", sky, 0, 260),
        nameFill=grad("nameFill", [(0.0, pal["name_a"]), (1.0, pal["name_b"])]),
        cometGrads=comet_grads((1128, 46), 208, 300, pal),
        comet=comet((1128, 46), 208, 300, pal, scale=0.85),
        textShadow=('<filter id="textShadow" x="-20%%" y="-60%%" width="140%%" height="240%%">'
                    '<feDropShadow dx="0" dy="1.6" stdDeviation="8" flood-color="%s" flood-opacity="%s"/>'
                    "</filter>" % (pal["text_glow"], pal["text_glow_op"])),
        stars=star_field(rnd, 46 if theme == "dark" else 12, 210, pal["star"], 6),
        birds_op=pal["birds_op"],
        birds=birds(rnd, pal),
        hills2=hills2,
        hills=hills,
        jp=JP,
        mono=MONO,
        muted=pal["sub"],
        handle=pal["window"],
    )


# --------------------------------------------------------------------------
# profile card
# --------------------------------------------------------------------------

def card(theme):
    pal = P[theme]
    rows = [
        ("BIO", "爱自由.", JP),
        ("MODE", "coding under the dusk sky", MONO),
        ("ALIAS", "ilovfyu-niosle", MONO),
        ("SINCE", "2020.12 · GitHub", MONO),
    ]
    row_svg = []
    y = 150
    for label, value, fam in rows:
        row_svg.append('<text x="34" y="%d" font-family="%s" font-size="10.5" letter-spacing="2.4" '
                       'fill="%s" opacity="0.85">%s</text>' % (y, MONO, pal["card_muted"], label))
        row_svg.append('<text x="112" y="%d" font-family="%s" font-size="14.5" fill="%s">%s</text>'
                       % (y, fam, pal["card_text"], value))
        row_svg.append('<line x1="34" y1="%d" x2="486" y2="%d" stroke="%s" stroke-width="1" opacity="0.55"/>'
                       % (y + 15, y + 15, pal["card_row"]))
        y += 44

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 340" width="520" height="340" role="img" aria-labelledby="ct cd">
  <title id="ct">ilovfyu — profile card</title>
  <desc id="cd">A twilight-themed profile card with name, alias and quick facts.</desc>
  <defs>
    {bg}
    {edge}
    {nameFill}
    {comet}
    <clipPath id="cclip"><rect x="2" y="2" width="516" height="336" rx="20"/></clipPath>
  </defs>

  <g clip-path="url(#cclip)">
    <rect x="2" y="2" width="516" height="336" rx="20" fill="url(#cBg)"/>
    <polygon points="520,0 330,190 400,190" fill="url(#cComet)" opacity="0.5"/>
    <circle cx="486" cy="52" r="34" fill="{emblem}" opacity="0.16"/>
    <circle cx="486" cy="52" r="4" fill="{emblem}" opacity="0.9">
      <animate attributeName="opacity" values="0.9;0.3;0.9" dur="4s" repeatCount="indefinite"/>
    </circle>
  </g>

  <rect x="2" y="2" width="516" height="336" rx="20" fill="none" stroke="url(#cEdge)" stroke-width="1.6"/>

  <g font-family="{ui}">
    <text x="34" y="66" font-size="34" font-weight="700" letter-spacing="1.5" fill="url(#nameFill)">ilovfyu</text>
    <text x="34" y="92" font-family="{mono}" font-size="13" fill="{muted}">@ilovfyu-niosle</text>
    <path d="M34,112 L486,112" stroke="url(#cEdge)" stroke-width="1" opacity="0.75"/>
    {rows}
  </g>
</svg>
""".format(
        bg=vgrad("cBg", [(0, pal["card_bg"][0], "1"), (1, pal["card_bg"][1], "1")], 0, 340),
        edge=grad("cEdge", [(0.0, pal["card_edge_a"], "0.95"), (1.0, pal["card_edge_b"], "0.85")]),
        nameFill=grad("nameFill", [(0.0, pal["card_title_a"]), (1.0, pal["card_title_b"])]),
        comet=grad("cComet", [(0.0, pal["card_edge_b"], "0.55"), (1.0, pal["card_edge_b"], "0.0")]),
        emblem=pal["emblem"],
        ui=UI,
        mono=MONO,
        muted=pal["card_muted"],
        rows="\n    ".join(row_svg),
    )


# --------------------------------------------------------------------------

def main():
    if not os.path.isdir(ASSETS):
        os.makedirs(ASSETS)
    built = []
    jobs = [("banner", banner), ("card", card), ("divider", divider), ("footer", footer)]
    for name, fn in jobs:
        for theme in ("light", "dark"):
            path = os.path.join(ASSETS, "%s-%s.svg" % (name, theme))
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(fn(theme))
            built.append((path, os.path.getsize(path)))
    for path, size in built:
        print("  %-34s %6.1f KB" % (os.path.relpath(path, ROOT), size / 1024.0))
    print("done: %d files" % len(built))


if __name__ == "__main__":
    main()
