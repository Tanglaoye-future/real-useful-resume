"""
Extracts the active anti-bot font and prepares a font_map for manual filling.

Key correctness step: a page often loads multiple .woff files (UI icon fonts +
the actual anti-bot font). We pick the right one by:
  1. Finding all PUA (U+E000–U+F8FF) codepoints that actually appear in the
     page's response text — these are the chars being substituted
  2. Downloading every .woff/.woff2 URL referenced in the HTML
  3. Picking the font whose cmap covers the most of those used codepoints
  4. Rendering only those used codepoints to PNG (not all glyphs in the font)

Result: ~30 PNGs to label, not ~300.

Output:
  font_extract/
    font.woff               raw bytes of winning font
    font.ttf                converted for rendering
    glyphs/U+E001.png       one PNG per codepoint actually used in salaries/titles
    font_map.json           {"<char>": "", ...}  ← you fill in the values
    candidates.txt          diagnostic: all woffs tried + match counts
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from urllib.parse import urljoin

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LIST_URL = "https://www.shixiseng.com/interns"
LIST_PARAMS = {"city": "上海", "page": 1}
OUT_DIR = "font_extract"

PUA_RE = re.compile(r"[-]")
# Capture every src: url(...) inside @font-face — extension may be missing
# (e.g. shixiseng's /interns/iconfonts/file?rand=... has no .woff suffix)
FONTFACE_RE = re.compile(r"@font-face\s*\{[^}]*\}", re.IGNORECASE | re.DOTALL)
SRC_URL_RE = re.compile(r'url\(["\']?([^)\'"]+)["\']?\)', re.IGNORECASE)


def find_pua_codepoints(text: str) -> set[int]:
    return {ord(c) for c in PUA_RE.findall(text)}


def find_woff_urls(html: str, base_url: str) -> list[str]:
    """Find every URL referenced inside an @font-face block, regardless of extension.
    Some sites (e.g. shixiseng) serve the font from an extension-less endpoint."""
    urls = []
    for face in FONTFACE_RE.finditer(html):
        for m in SRC_URL_RE.finditer(face.group(0)):
            u = m.group(1).strip()
            if u.startswith("data:"):
                urls.append(u)  # base64 inline — handle separately below
            elif u.startswith("http"):
                urls.append(u)
            elif u.startswith("//"):
                urls.append("https:" + u)
            else:
                urls.append(urljoin(base_url, u))
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def fetch_font_bytes(url: str, referer: str) -> bytes:
    if url.startswith("data:"):
        import base64
        # data:font/woff;base64,XXXX or data:application/octet-stream;base64,XXXX
        _, payload = url.split(",", 1)
        return base64.b64decode(payload)
    r = requests.get(url, headers={"User-Agent": UA, "Referer": referer}, timeout=15)
    return r.content


def woff_to_ttfont(woff_bytes: bytes):
    from fontTools.ttLib import TTFont
    return TTFont(io.BytesIO(woff_bytes))


def main():
    os.makedirs(f"{OUT_DIR}/glyphs", exist_ok=True)

    print("[1/5] Fetching list page...")
    r = requests.get(
        LIST_URL,
        params=LIST_PARAMS,
        headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"},
        timeout=15,
    )
    r.encoding = "utf-8"
    print(f"   OK    HTTP {r.status_code}, {len(r.text) // 1024} KB")

    print(f"[2/5] Scanning page for PUA chars actually used in salaries/titles...")
    # Use BeautifulSoup so &#xEA74; numeric entities decode to real chars before scanning
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    used = find_pua_codepoints(soup.get_text())
    print(f"   OK    {len(used)} unique PUA codepoints in rendered text")
    if not used:
        print("   NOTE  no PUA chars in page — site may have dropped font anti-bot")
        print("         OR content is JS-rendered (font swap happens client-side too)")
        # write empty map and continue
        with open(f"{OUT_DIR}/font_map.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        sys.exit(0)

    print("[3/5] Discovering @font-face URLs in HTML...")
    woff_urls = find_woff_urls(r.text, LIST_URL)
    print(f"   OK    {len(woff_urls)} candidate URL(s)")
    for u in woff_urls:
        short = u[:80] + "..." if len(u) > 80 else u
        print(f"          {short}")
    if not woff_urls:
        print("   FAIL  no @font-face URLs found.")
        sys.exit(1)

    print("[4/5] Picking the font whose cmap covers the most used codepoints...")
    candidates = []
    for u in woff_urls:
        try:
            wb = fetch_font_bytes(u, LIST_URL)
            font = woff_to_ttfont(wb)
            cmap_keys = set(font.getBestCmap().keys())
            match = used & cmap_keys
            label = u.rsplit("/", 1)[-1][:50] if not u.startswith("data:") else "data:..."
            print(f"   {label:50s}  {len(cmap_keys)} glyphs total, {len(match)} match used PUA")
            candidates.append((u, wb, font, len(match)))
        except Exception as e:
            print(f"   skip {u[:60]}: {e}")
            candidates.append((u, None, None, -1))

    candidates.sort(key=lambda x: x[3], reverse=True)
    winner_url, winner_bytes, winner_font, winner_match = candidates[0]
    if winner_match == 0:
        print("   FAIL  no font's cmap matches the PUA codepoints found in page text.")
        print("         The actual anti-bot font is probably loaded via JS (base64 inline).")
        print(f"         Used codepoints (sample): {sorted(used)[:10]}")
        sys.exit(1)
    print(f"   WIN   {winner_url}  ({winner_match}/{len(used)} codepoints covered)")

    with open(f"{OUT_DIR}/font.woff", "wb") as f:
        f.write(winner_bytes)
    winner_font.flavor = None
    ttf_path = f"{OUT_DIR}/font.ttf"
    winner_font.save(ttf_path)

    with open(f"{OUT_DIR}/candidates.txt", "w", encoding="utf-8") as f:
        for u, _, _, m in candidates:
            f.write(f"{m:4d}  {u}\n")

    print("[5/5] Rendering only the used codepoints to PNG...")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("   FAIL  install Pillow:  pip install Pillow")
        sys.exit(1)

    pil_font = ImageFont.truetype(ttf_path, size=64)
    cmap_keys = set(winner_font.getBestCmap().keys())
    to_render = sorted(used & cmap_keys)
    starter = {}
    for cp in to_render:
        ch = chr(cp)
        img = Image.new("RGB", (80, 80), "white")
        draw = ImageDraw.Draw(img)
        try:
            draw.text((8, 4), ch, font=pil_font, fill="black")
        except Exception:
            pass
        img.save(f"{OUT_DIR}/glyphs/U+{cp:04X}.png")
        starter[ch] = ""

    map_path = f"{OUT_DIR}/font_map.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(starter, f, ensure_ascii=True, indent=2)

    print(f"   OK    {len(starter)} glyphs rendered, {map_path} written")
    print()
    print("=" * 60)
    print("MANUAL STEP — about 5 minutes:")
    print()
    print(f"  1. Open folder:  {os.path.abspath(OUT_DIR + '/glyphs')}")
    print(f"  2. Open file:    {os.path.abspath(map_path)}")
    print(f"  3. For each PNG: look at the glyph, fill the matching JSON value:")
    print(r'        "": "0"')
    print(r'        "": "招"')
    print(f"  4. Save the JSON. shixiseng_adapter.py loads it automatically.")
    print()
    print(f"You only need to label {len(starter)} glyphs (not the whole font).")
    print("=" * 60)


if __name__ == "__main__":
    main()
