#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project list card for ilovfyu's profile — rendered locally in the dusk theme.

Why: the "Popular repositories" pins on github.com are GitHub's own UI. You can
choose *which* repos are pinned, but you cannot restyle the cards, and a repo with
an empty "About" field renders as a big blank box. So we render our own card from
the public API — description, language, stars, last push, plus an overall language
breakdown — and refresh it automatically alongside the contribution cards.

This card also replaces the third-party top-languages card, so every number on the
profile comes from one pipeline with one set of definitions.

Repo descriptions come straight from each repo's "About" field on GitHub. Add one
there (pencil next to "About"), and the next run shows it.

Usage:
    python3 tools/build_projects.py
    python3 tools/build_projects.py --pin SkillForge,ilovfyu
    python3 tools/build_projects.py --exclude ilovfyu
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_assets import f, grad, P, UI, MONO                      # noqa: E402
from build_heatmap import CARD_W, PAD, card_frame, title_block      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
UA = {"User-Agent": "ilovfyu-profile-build", "Accept": "application/vnd.github+json"}

REPOS_API = "https://api.github.com/users/{user}/repos?per_page=100&sort=pushed"
LANGS_API = "https://api.github.com/repos/{full}/languages"

HEADER_H = 70       # title row only
ROW_H = 76          # repo with a description
ROW_H_BARE = 54     # repo without one — keeps the card from looking unfinished
META_W = 210        # right-hand column reserved for language / stars / date
LANG_BAR_H = 9
LANG_BLOCK = 52     # stacked bar + legend
LANG_MAX = 5        # legend entries before the rest are folded into "其他"

# official-ish language colours; anything unknown falls back to the theme accent
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "TSX": "#3178C6", "JSX": "#F1E05A", "Rust": "#DEA584", "Go": "#00ADD8",
    "Java": "#B07219", "C": "#555555", "C++": "#F34B7D", "C#": "#178600",
    "Shell": "#89E051", "HTML": "#E34C26", "CSS": "#563D7C", "Vue": "#41B883",
    "Svelte": "#FF3E00", "Ruby": "#701516", "PHP": "#4F5D95", "Kotlin": "#A97BFF",
    "Swift": "#F05138", "Dart": "#00B4AB", "Lua": "#000080", "Zig": "#EC915C",
    "Jupyter Notebook": "#DA5B0B", "Markdown": "#083FA1", "Dockerfile": "#384D54",
}


def esc(s):
    """XML-escape — a repo description containing & or < would otherwise break the SVG."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def text_w(s, size, mono=False):
    """Rough rendered width: CJK ~1em; latin ~0.6em mono, ~0.52em proportional."""
    latin = size * (0.6 if mono else 0.52)
    return sum(size if ord(c) > 0x2E80 else latin for c in s)


def fit(s, max_px, size):
    if text_w(s, size) <= max_px:
        return s
    out = ""
    for ch in s:
        if text_w(out + ch + "…", size) > max_px:
            break
        out += ch
    return out + "…"


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as fh:
        return json.loads(fh.read().decode("utf-8"))


def fetch_repos(user):
    return _get(REPOS_API.format(user=user))


def fetch_languages(repos):
    """Sum byte counts across the chosen repos -> [(name, percent)] biggest first."""
    total = {}
    for r in repos:
        try:
            data = _get(LANGS_API.format(full=r["full_name"]))
        except Exception:
            continue
        for name, nbytes in data.items():
            total[name] = total.get(name, 0) + nbytes
    if not total:
        return []
    s = float(sum(total.values()))
    ranked = sorted(total.items(), key=lambda kv: -kv[1])
    return [(n, v * 100.0 / s) for n, v in ranked]


def pick(repos, limit, exclude, pin):
    """Forks and archives out; explicitly pinned names first, then substance."""
    keep = [r for r in repos
            if not r.get("fork") and not r.get("archived") and r["name"] not in exclude]
    rank = {name: i for i, name in enumerate(pin)}
    keep.sort(key=lambda r: (
        rank.get(r["name"], len(rank)),                 # pinned order wins
        not bool(r.get("description")),                 # then: has a description
        -r.get("stargazers_count", 0),                  # then: stars
        _neg(r.get("pushed_at") or ""),                 # then: most recently pushed
    ))
    return keep[:limit]


def _neg(iso):
    """Sort helper so that a later pushed_at sorts first under ascending key."""
    return tuple(-ord(c) for c in iso)


def ago(iso):
    if not iso:
        return ""
    try:
        d = dt.datetime.strptime(iso[:10], "%Y-%m-%d").date()
    except ValueError:
        return ""
    days = (dt.date.today() - d).days
    if days <= 0:
        return "今天"
    if days == 1:
        return "昨天"
    if days < 30:
        return "%d 天前" % days
    if days < 365:
        return "%d 个月前" % (days // 30)
    return "%d 年前" % (days // 365)


def lang_block(pal, langs):
    """A stacked proportion bar plus a legend — replaces the old external card."""
    if not langs:
        return "", 0

    shown = langs[:LANG_MAX]
    rest = sum(p for _, p in langs[LANG_MAX:])
    if rest > 0.05:
        shown = shown + [("其他", rest)]

    bar_y = HEADER_H - 6
    x = float(PAD)
    inner = CARD_W - PAD * 2
    parts = []
    for i, (name, pct) in enumerate(shown):
        w = inner * pct / 100.0
        if w < 1.2:
            continue
        r = 4.5 if i in (0, len(shown) - 1) else 0
        parts.append('<rect x="%s" y="%s" width="%s" height="%d" rx="%s" fill="%s">'
                     "<title>%s %.1f%%</title></rect>"
                     % (f(x), f(bar_y), f(w), LANG_BAR_H, f(r),
                        LANG_COLORS.get(name, pal["card_edge_b"]), esc(name), pct))
        x += w

    # legend, laid out left-to-right with measured widths, dropping what won't fit
    ly = bar_y + LANG_BAR_H + 22
    lx = float(PAD)
    limit = CARD_W - PAD
    legend = []
    for name, pct in shown:
        label = "%s %.1f%%" % (name, pct)
        w = 11 + text_w(label, 11.5, mono=True)
        if lx + w > limit:
            break
        legend.append('<circle cx="%s" cy="%s" r="4.5" fill="%s"/>'
                      % (f(lx + 4.5), f(ly - 4), LANG_COLORS.get(name, pal["card_edge_b"])))
        legend.append('<text x="%s" y="%s" font-family="%s" font-size="11.5" fill="%s">%s</text>'
                      % (f(lx + 15), f(ly), MONO, pal["card_muted"], esc(label)))
        lx += w + 22

    # hairline closing the language block off from the repo list
    parts.append('<line x1="%d" y1="%s" x2="%d" y2="%s" stroke="%s" stroke-width="1" '
                 'opacity="0.6"/>'
                 % (PAD, f(HEADER_H + LANG_BLOCK - 16), CARD_W - PAD,
                    f(HEADER_H + LANG_BLOCK - 16), pal["card_row"]))

    return "".join(parts) + "".join(legend), LANG_BLOCK


def card(theme, repos, user, langs):
    pal = P[theme]
    rows = [(r, ROW_H if r.get("description") else ROW_H_BARE) for r in repos]
    lang_svg, lang_h = lang_block(pal, langs)
    top = HEADER_H + lang_h
    h = top + sum(rh for _, rh in rows) + 16
    bg, edge, bg_rect, edge_rect = card_frame(theme, pal, h)

    body = []
    y = top
    for i, (r, rh) in enumerate(rows):
        name_y = y + 26
        desc = (r.get("description") or "").strip()
        lang = r.get("language")
        dot = LANG_COLORS.get(lang, pal["card_edge_b"])

        body.append('<text x="%d" y="%s" font-family="%s" font-size="15.5" '
                    'font-weight="700" fill="%s">%s</text>'
                    % (PAD, f(name_y), MONO, pal["card_title_b"], esc(r["name"])))
        if desc:
            body.append('<text x="%d" y="%s" font-family="%s" font-size="12.5" fill="%s">%s</text>'
                        % (PAD, f(name_y + 23), UI, pal["card_muted"],
                           esc(fit(desc, CARD_W - PAD * 2 - META_W, 12.5))))

        # Right-hand meta as a tidy two-line stack: language on the first line,
        # "stars · last push" on the second. Keeping them on separate lines is
        # what stops the two right-aligned runs from colliding.
        mx = CARD_W - PAD
        if lang:
            lw = text_w(lang, 12, mono=True)
            body.append('<text x="%d" y="%s" text-anchor="end" font-family="%s" '
                        'font-size="12" fill="%s">%s</text>'
                        % (mx, f(name_y), MONO, pal["card_text"], esc(lang)))
            body.append('<circle cx="%s" cy="%s" r="4.6" fill="%s"/>'
                        % (f(mx - lw - 10), f(name_y - 4), dot))

        meta = []
        if r.get("stargazers_count"):
            meta.append("★ %d" % r["stargazers_count"])
        when = ago(r.get("pushed_at"))
        if when:
            meta.append("%s更新" % when)
        if meta:
            body.append('<text x="%d" y="%s" text-anchor="end" font-family="%s" '
                        'font-size="11.5" fill="%s" opacity="0.9">%s</text>'
                        % (mx, f(name_y + 23), MONO, pal["card_muted"],
                           esc(" · ".join(meta))))

        if i < len(rows) - 1:
            body.append('<line x1="%d" y1="%s" x2="%d" y2="%s" stroke="%s" '
                        'stroke-width="1" opacity="0.6"/>'
                        % (PAD, f(y + rh - 8), CARD_W - PAD, f(y + rh - 8), pal["card_row"]))
        y += rh

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-labelledby="pt pd">
  <title id="pt">项目与语言构成</title>
  <desc id="pd">%s 的 %d 个公开仓库：主要语言构成、各仓库简介、语言、star 与最近更新时间。</desc>
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
</svg>
""" % (
        CARD_W, h, CARD_W, h,
        user, len(repos),
        bg, edge,
        grad("titleFill", [(0.0, pal["card_title_a"]), (1.0, pal["card_title_b"])]),
        bg_rect, edge_rect,
        UI,
        title_block(pal, "项目", "PROJECTS", "%d 个公开仓库" % len(repos)),
        "".join(body),
        lang_svg,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="ilovfyu")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--exclude", default="", help="逗号分隔，排除某些仓库")
    ap.add_argument("--pin", default="SkillForge,ilovfyu", help="逗号分隔，按此顺序排在最前")
    args = ap.parse_args()

    exclude = {s.strip() for s in args.exclude.split(",") if s.strip()}
    pin = [s.strip() for s in args.pin.split(",") if s.strip()]

    try:
        repos = fetch_repos(args.user)
    except Exception as exc:
        print("fetch repos failed: %s" % exc, file=sys.stderr)
        return 1

    chosen = pick(repos, args.limit, exclude, pin)
    if not chosen:
        print("no public repositories to show", file=sys.stderr)
        return 1

    for r in chosen:
        if not (r.get("description") or "").strip():
            print("  ! %s 没有写 About 简介 —— 首页卡片上会是空的，建议补上"
                  % r["full_name"], file=sys.stderr)

    langs = fetch_languages(chosen)
    if not langs:
        print("  ! 没取到语言构成数据，卡片上会省略这一块", file=sys.stderr)

    if not os.path.isdir(ASSETS):
        os.makedirs(ASSETS)
    for theme in ("light", "dark"):
        path = os.path.join(ASSETS, "projects-%s.svg" % theme)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(card(theme, chosen, args.user, langs))
        print("  %-34s %6.1f KB" % (os.path.relpath(path, ROOT),
                                    os.path.getsize(path) / 1024.0))
    print("done: %s" % ", ".join(r["name"] for r in chosen))
    if langs:
        print("langs: " + ", ".join("%s %.1f%%" % (n, p) for n, p in langs[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
