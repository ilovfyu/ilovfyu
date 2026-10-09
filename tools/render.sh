#!/usr/bin/env bash
# Render an SVG (or HTML) file to PNG with headless Chrome.
#
# Two Chrome quirks are worked around here:
#  1. When a screenshot is taller than the rendered page, headless Chrome *tiles*
#     the page upward to fill the extra space, producing a bogus repeated band.
#     Fix: over-size the window, then crop back down.
#  2. A standalone SVG document gets scaled/centred by Chrome in ways that depend
#     on the viewport, so "render at 880x293" does NOT reliably give you the whole
#     artwork. Fix: wrap the SVG in an HTML page with an explicit <img width height>,
#     so it is laid out at exactly WxH in the page's top-left corner.
#
# usage: tools/render.sh <input.svg|input.html> <output.png> [width] [height]
set -u
IN="$1"; OUT="$2"; W="${3:-1200}"; H="${4:-400}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROF="$ROOT/.tmp/prof-$$"
SHOT="$ROOT/.tmp/_shot-$$.png"
PAGE="$ROOT/.tmp/_page-$$.html"
rm -f "$OUT" "$SHOT"; mkdir -p "$PROF"

case "$IN" in
  *.html|*.htm)
    TARGET="file://$IN" ;;
  *)
    cat > "$PAGE" <<HTML
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:#ff00ff}
img{display:block;width:${W}px;height:${H}px}
</style></head><body><img src="file://$IN"></body></html>
HTML
    TARGET="file://$PAGE" ;;
esac

HOME="$ROOT/.tmp/home" "$CHROME" \
  --headless=new --disable-gpu --no-sandbox --no-first-run --no-default-browser-check \
  --disable-background-networking --disable-sync --disable-extensions --disable-dev-shm-usage \
  --hide-scrollbars --force-device-scale-factor=1 \
  --user-data-dir="$PROF" --virtual-time-budget=2500 \
  --window-size="$W,$((H + 200))" --screenshot="$SHOT" "$TARGET" >/dev/null 2>&1 &
PID=$!

for _ in $(seq 1 60); do
  [ -s "$SHOT" ] && break
  sleep 0.5
done
sleep 1
kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
rm -rf "$PROF" "$PAGE"

if [ -s "$SHOT" ]; then
  python3 -c "from PIL import Image; Image.open('$SHOT').convert('RGB').crop((0,0,$W,$H)).save('$OUT')" \
    && rm -f "$SHOT" && echo "ok  $OUT" || { echo "crop failed"; exit 1; }
else
  echo "FAILED $OUT"; exit 1
fi
