#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contribution card for ilovfyu's profile — rendered locally in the dusk theme.

Why this exists: the contribution graph and the "Contribution activity" feed on
github.com are GitHub's own UI, rendered outside the README container. No README,
CSS or theme can restyle them, and they cannot be removed either. The only way to
get *your* colours onto that data is to render your own card from the raw numbers
and embed the SVG. That is what this script does.

One card, two halves:
    top    53-week calendar heatmap + summary + numeric legend
    bottom 12-month bar rhythm

They used to be two separate cards, but both describe the same thing (commits), so
merging them removed a redundant title row and ~130px of scroll.

Data source: github.com/users/<user>/contributions  (GitHub's own calendar — primary,
             so the numbers match the profile page exactly)
             github-contributions-api.jogruber.de   (fallback; caches, can lag a day)

Raw data is cached to data/contributions.json so that `--offline` can rebuild the
SVGs and the daily Action's commit shows a readable data diff.

Usage:
    python3 tools/build_heatmap.py              # fetch, then render
    python3 tools/build_heatmap.py --offline    # render from data/contributions.json
    python3 tools/build_heatmap.py --user someone --years last
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_assets import f, grad, vgrad, radial, P, UI, MONO  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DATA_DIR = os.path.join(ROOT, "data")
DATA_FILE = os.path.join(DATA_DIR, "contributions.json")

API = "https://github-contributions-api.jogruber.de/v4/{user}?y={years}"
GH_CONTRIB = "https://github.com/users/{user}/contributions"
UA = {"User-Agent": "ilovfyu-profile-build", "Accept-Language": "en-US,en;q=0.9"}

# ── layout ────────────────────────────────────────────────────────────────────
# Designed at 900px wide on purpose: GitHub renders README content in a ~880px
# column, so a 1200px card would be scaled down 27% and the small labels (legend
# numbers, weekday names) would turn to mush. At 900px it is ~1:1.
CARD_W = 900
CELL = 12
GAP = 3
PITCH = CELL + GAP          # column pitch
LABEL_W = 30                # room for Mon/Wed/Fri labels
PAD = 32

GRID_Y = 96                 # top of the calendar grid
GRID_BOTTOM = GRID_Y + 7 * PITCH - GAP
SUMMARY_Y = 226             # baseline of the summary line
DIVIDER_Y = 260             # hairline between the two halves
BAR_BASE = 366.0            # baseline of the monthly bars
BAR_MAX_H = 74.0
CARD_H = 412

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["", "Mon", "", "Wed", "", "Fri", ""]   # Sunday-first rows


# ── data ──────────────────────────────────────────────────────────────────────

def fetch(user, years):
    """Fallback source: clean JSON, but it caches and can lag a day behind."""
    url = API.format(user=user, years=years)
    req = urllib.request.Request(url, headers={"User-Agent": "ilovfyu-profile-build"})
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode("utf-8"))


def fetch_github(user):
    """Primary source: GitHub's own contribution calendar.

    Authoritative, so the numbers match the profile page exactly. The third-party
    JSON API lagged by a day, which made our card say 23 while GitHub said 24 —
    both visible on the same page, which is worse than having no number at all.

    The calendar is server-rendered as empty <td data-date data-level> cells plus
    separate <tool-tip for="..."> nodes holding the counts.
    """
    req = urllib.request.Request(GH_CONTRIB.format(user=user), headers=UA)
    html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")

    cells = {}
    for tag in re.findall(r"<td\b[^>]*>", html):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        i = re.search(r'\bid="([^"]+)"', tag)
        lv = re.search(r'data-level="(\d+)"', tag)
        if d and i and lv:
            cells[i.group(1)] = {"date": d.group(1), "level": int(lv.group(1)), "count": 0}

    for ident, text in re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>',
                                  html, re.S):
        if ident not in cells:
            continue
        m = re.match(r"\s*(\d+|No)\s+contribution", text, re.I)
        if m:
            cells[ident]["count"] = 0 if m.group(1).lower() == "no" else int(m.group(1))

    days = sorted(cells.values(), key=lambda c: c["date"])
    if len(days) < 300:
        raise ValueError("only parsed %d day cells" % len(days))
    return {"total": {"lastYear": sum(d["count"] for d in days)}, "contributions": days}


def normalise(raw):
    """Sort by date, coerce types, drop anything unparseable."""
    days = []
    for row in raw.get("contributions", []):
        try:
            d = dt.date.fromisoformat(row["date"])
        except (KeyError, ValueError):
            continue
        days.append({
            "date": d,
            "count": int(row.get("count", 0)),
            "level": max(0, min(4, int(row.get("level", 0)))),
        })
    days.sort(key=lambda x: x["date"])
    return days


def build_grid(days, weeks=53):
    """Lay the days out Sunday-first into `weeks` columns of 7, oldest on the left."""
    if not days:
        return [], None
    last = days[-1]["date"]
    end_sun = last + dt.timedelta(days=(6 - last.weekday()) % 7)
    start_sun = end_sun - dt.timedelta(days=weeks * 7 - 1)
    by_date = {d["date"]: d for d in days}

    cols = []
    for w in range(weeks):
        col = []
        for r in range(7):
            day = start_sun + dt.timedelta(days=w * 7 + r)
            col.append(by_date.get(day, {"date": day, "count": 0, "level": -1}))
        cols.append(col)
    return cols, start_sun


def legend_ranges(days):
    """Numeric range of each level, so the legend never relies on colour alone.

    GitHub picks its levels from quartiles, so a level can legitimately be empty
    (this account has no level-3 days at all). Fill those gaps by interpolating
    between the neighbouring levels instead of printing a blank.
    """
    buckets = {}
    for d in days:
        buckets.setdefault(d["level"], []).append(d["count"])
    present = {L: (min(v), max(v)) for L, v in buckets.items()}
    out = []
    for L in range(5):
        if L in present:
            lo, hi = present[L]
            out.append(str(lo) if lo == hi else "%d-%d" % (lo, hi))
            continue
        lower = [present[k][1] for k in present if k < L]
        upper = [present[k][0] for k in present if k > L]
        lo = (max(lower) + 1) if lower else None
        hi = (min(upper) - 1) if upper else None
        if lo is None and hi is None:
            out.append("")
        elif lo is None:
            out.append("<=%d" % hi)
        elif hi is None:
            out.append("%d+" % lo)
        elif lo > hi:
            out.append(str(lo))
        else:
            out.append("%d-%d" % (lo, hi))
    return out


def streaks(days):
    """(current, longest) runs of consecutive days with at least one contribution."""
    longest = run = 0
    prev = None
    for d in days:
        if d["count"] > 0:
            run = run + 1 if prev is not None and (d["date"] - prev).days == 1 else 1
            longest = max(longest, run)
        else:
            run = 0
        prev = d["date"]

    # current streak: walk back from the newest day. A quiet *today* has not
    # finished yet, so it must not kill the run (GitHub behaves the same way).
    tail = list(reversed(days))
    if tail and tail[0]["count"] == 0:
        tail = tail[1:]
    cur = 0
    expect = None
    for d in tail:
        if d["count"] <= 0:
            break
        if expect is not None and (expect - d["date"]).days != 1:
            break
        cur += 1
        expect = d["date"]
    return cur, longest


def monthly(days, n=12):
    """Totals for the last `n` calendar months, oldest first."""
    if not days:
        return []
    last = days[-1]["date"]
    keys = []
    y, m = last.year, last.month
    for _ in range(n):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()
    totals = {k: 0 for k in keys}
    for d in days:
        k = (d["date"].year, d["date"].month)
        if k in totals:
            totals[k] += d["count"]
    return [(k, totals[k]) for k in keys]


# ── shared chrome (also used by build_projects.py) ────────────────────────────

def card_frame(theme, pal, h):
    """Rounded panel + gradient border, matching assets/card-*.svg."""
    return (
        vgrad("bg", [(0, pal["card_bg"][0], "1"), (1, pal["card_bg"][1], "1")], 0, h),
        grad("edge", [(0.0, pal["card_edge_a"], "0.95"), (1.0, pal["card_edge_b"], "0.85")]),
        '<rect x="1" y="1" width="%d" height="%d" rx="20" fill="url(#bg)"/>' % (CARD_W - 2, h - 2),
        ('<rect x="1" y="1" width="%d" height="%d" rx="20" fill="none" '
         'stroke="url(#edge)" stroke-width="1.6"/>' % (CARD_W - 2, h - 2)),
    )


def title_block(pal, title, title_en, right_label):
    # CJK glyphs are ~1em wide, latin ~0.5em, so the subtitle offset has to be
    # measured rather than guessed with len().
    title_w = sum(19.0 if ord(c) > 0x2E80 else 9.5 for c in title)
    return (
        '<text x="%d" y="46" font-family="%s" font-size="19" font-weight="700" '
        'fill="url(#titleFill)">%s</text>'
        '<text x="%s" y="46" font-family="%s" font-size="12.5" letter-spacing="1.6" '
        'fill="%s" opacity="0.85">%s</text>'
        '<text x="%d" y="46" text-anchor="end" font-family="%s" font-size="13" '
        'fill="%s">%s</text>' % (
            PAD, UI, title,
            f(PAD + title_w + 14), MONO, pal["card_muted"], title_en,
            CARD_W - PAD, MONO, pal["card_text"], right_label,
        )
    )


# ── the card ──────────────────────────────────────────────────────────────────

def contributions(theme, days, cols, total):
    pal = P[theme]
    bg, edge, bg_rect, edge_rect = card_frame(theme, pal, CARD_H)

    # ── 53-week calendar ──────────────────────────────────────────────────────
    grid_w = len(cols) * PITCH - GAP
    gx = (CARD_W - (LABEL_W + grid_w)) / 2.0 + LABEL_W

    cells = []
    for w, col in enumerate(cols):
        for r, day in enumerate(col):
            lv = day["level"]
            fill = pal["grid_empty"] if lv < 0 else pal["levels"][lv]
            cells.append(
                '<rect x="%s" y="%s" width="%d" height="%d" rx="3" fill="%s">'
                "<title>%s — %d</title></rect>"
                % (f(gx + w * PITCH), f(GRID_Y + r * PITCH), CELL, CELL, fill,
                   day["date"].isoformat(), day["count"])
            )

    months, last_month = [], None
    for w, col in enumerate(cols):
        m = col[0]["date"].month
        if m != last_month:
            months.append('<text x="%s" y="%s" font-family="%s" font-size="11" fill="%s">%s</text>'
                          % (f(gx + w * PITCH), f(GRID_Y - 12), MONO, pal["card_muted"],
                             MONTHS[m - 1]))
            last_month = m

    weekdays = "".join(
        '<text x="%s" y="%s" text-anchor="end" font-family="%s" font-size="10.5" fill="%s">%s</text>'
        % (f(gx - 10), f(GRID_Y + r * PITCH + CELL * 0.78), MONO, pal["card_muted"], WEEKDAYS[r])
        for r in range(7) if WEEKDAYS[r]
    )

    # ── summary line + numeric legend ─────────────────────────────────────────
    active = sum(1 for d in days if d["count"] > 0)
    best = max((d["count"] for d in days), default=0)
    cur, longest = streaks(days)
    summary = (
        '<text x="%d" y="%s" font-family="%s" font-size="12" fill="%s" opacity="0.9">'
        "活跃 <tspan font-weight=\"700\" fill=\"%s\">%d</tspan> 天"
        "　·　当前连续 <tspan font-weight=\"700\" fill=\"%s\">%d</tspan> 天"
        "　·　最长连续 <tspan font-weight=\"700\" fill=\"%s\">%d</tspan> 天"
        "　·　单日最多 <tspan font-weight=\"700\" fill=\"%s\">%d</tspan> 次</text>"
        % (PAD, f(SUMMARY_Y), MONO, pal["card_muted"],
           pal["card_text"], active, pal["card_text"], cur,
           pal["card_text"], longest, pal["card_text"], best)
    )

    labels = legend_ranges(days)
    lw = CELL + 13
    legend_w = 5 * lw - 13
    lx = CARD_W - PAD - legend_w - 42
    ly = SUMMARY_Y - 15
    legend = ['<text x="%s" y="%s" text-anchor="end" font-family="%s" font-size="11" '
              'fill="%s">少</text>'
              % (f(lx - 8), f(ly + CELL * 0.82), MONO, pal["card_muted"])]
    for i in range(5):
        x = lx + i * lw
        legend.append('<rect x="%s" y="%s" width="%d" height="%d" rx="3" fill="%s"/>'
                      % (f(x), f(ly), CELL, CELL, pal["levels"][i]))
        if labels[i]:
            legend.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                          'font-size="9" fill="%s" opacity="0.9">%s</text>'
                          % (f(x + CELL / 2), f(ly + CELL + 13), MONO,
                             pal["card_muted"], labels[i]))
    legend.append('<text x="%s" y="%s" font-family="%s" font-size="11" fill="%s">多</text>'
                  % (f(lx + legend_w + 8), f(ly + CELL * 0.82), MONO, pal["card_muted"]))

    # ── monthly rhythm ────────────────────────────────────────────────────────
    data = monthly(days, 12)
    peak = max([c for _, c in data] + [1])
    bar_w, gap = 46, 24
    span = len(data) * (bar_w + gap) - gap
    x0 = (CARD_W - span) / 2.0
    svg_ly = SUMMARY_Y - 15 + CELL + 13   # bottom of the legend numbers

    bars = []
    for i, ((y, m), count) in enumerate(data):
        x = x0 + i * (bar_w + gap)
        hgt = max((count / float(peak)) * BAR_MAX_H, 3.0)   # empty months keep a stub
        top = BAR_BASE - hgt
        col = pal["levels"][4] if count and count >= peak * 0.66 else \
              pal["levels"][3] if count and count >= peak * 0.33 else \
              pal["levels"][2] if count else pal["grid_empty"]
        bars.append('<rect x="%s" y="%s" width="%d" height="%s" rx="6" fill="%s" '
                    'opacity="%s"><title>%d-%02d — %d 次</title></rect>'
                    % (f(x), f(top), bar_w, f(hgt), col, "1" if count else "0.9", y, m, count))
        bars.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                    'font-size="13" font-weight="700" fill="%s" opacity="%s">%s</text>'
                    % (f(x + bar_w / 2), f(top - 10), UI, pal["card_text"],
                       "1" if count else "0.35", count if count else "·"))
        bars.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                    'font-size="11" fill="%s">%s</text>'
                    % (f(x + bar_w / 2), f(BAR_BASE + 22), MONO, pal["card_muted"],
                       MONTHS[m - 1]))
    bars.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2" '
                'opacity="0.75"/>'
                % (f(x0 - 6), f(BAR_BASE + 1), f(x0 + span + 6), f(BAR_BASE + 1),
                   pal["card_row"]))

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-labelledby="ct cd">
  <title id="ct">贡献</title>
  <desc id="cd">最近 53 周的公开提交热力图（共 %d 次，活跃 %d 天，最长连续 %d 天），以及最近 12 个月的提交量柱状图。</desc>
  <defs>
    %s
    %s
    %s
  </defs>
  %s
  %s
  <g font-family="%s">
    %s
  </g>
  <g>
    %s
  </g>
  <g>
    %s
  </g>
  <g>
    %s
  </g>
  <line x1="%d" y1="%s" x2="%d" y2="%s" stroke="%s" stroke-width="1" opacity="0.7"/>
  <g>
    %s
  </g>
</svg>
""" % (
        CARD_W, CARD_H, CARD_W, CARD_H,
        total, active, longest,
        bg, edge,
        grad("titleFill", [(0.0, pal["card_title_a"]), (1.0, pal["card_title_b"])]),
        bg_rect, edge_rect,
        UI,
        title_block(pal, "贡献", "CONTRIBUTIONS", "近一年 %d 次公开提交" % total),
        "".join(months) + weekdays,
        "".join(cells),
        summary + "".join(legend),
        PAD, f(DIVIDER_Y), CARD_W - PAD, f(DIVIDER_Y), pal["card_row"],
        "".join(bars),
    )


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="ilovfyu")
    ap.add_argument("--years", default="last", help="last | all | 2025 | ...")
    ap.add_argument("--offline", action="store_true", help="rebuild from data/contributions.json")
    args = ap.parse_args()

    raw = None
    if not args.offline:
        # GitHub's own calendar first (authoritative); the JSON API only covers
        # a rolling year, so it is skipped when a specific range was asked for.
        sources = []
        if args.years == "last":
            sources.append(("github.com", lambda: fetch_github(args.user)))
        sources.append(("jogruber", lambda: fetch(args.user, args.years)))

        for label, fn in sources:
            try:
                raw = fn()
                print("fetched %d days from %s"
                      % (len(raw.get("contributions", [])), label))
                break
            except Exception as exc:
                print("  %s failed: %s" % (label, exc), file=sys.stderr)
        if raw is None:
            if not os.path.exists(DATA_FILE):
                print("no source available and no cache", file=sys.stderr)
                return 1
            print("all sources failed — falling back to cached data", file=sys.stderr)

    if raw is None:
        with open(DATA_FILE, encoding="utf-8") as fh:
            raw = json.load(fh)
    else:
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR)
        with open(DATA_FILE, "w", encoding="utf-8") as fh:
            json.dump({"total": raw.get("total", {}),
                       "contributions": [
                           {"date": d["date"].isoformat(), "count": d["count"],
                            "level": d["level"]}
                           for d in normalise(raw)]},
                      fh, ensure_ascii=False, indent=1, sort_keys=True)

    days = normalise(raw)
    cols, _ = build_grid(days)
    total = sum(d["count"] for d in days)
    if not os.path.isdir(ASSETS):
        os.makedirs(ASSETS)

    for theme in ("light", "dark"):
        path = os.path.join(ASSETS, "contributions-%s.svg" % theme)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(contributions(theme, days, cols, total))
        print("  %-34s %6.1f KB" % (os.path.relpath(path, ROOT),
                                    os.path.getsize(path) / 1024.0))
    print("done: %d days, %d contributions, %d active days" %
          (len(days), total, sum(1 for d in days if d["count"] > 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
