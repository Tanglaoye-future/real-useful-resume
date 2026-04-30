"""
Pre-flight check. Run this FIRST. If any step fails, fix it before continuing.

  python verify_setup.py
"""
import sys
import importlib
import random

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REQUIRED = [
    ("requests", "requests"),
    ("bs4", "beautifulsoup4"),
    ("pandas", "pandas"),
    ("fontTools", "fonttools"),
    ("PIL", "Pillow"),
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def step(n, label):
    print(f"\n[{n}] {label}")


def main():
    step(1, "Checking Python packages...")
    missing = []
    for mod, pkg in REQUIRED:
        try:
            importlib.import_module(mod)
            print(f"   OK    {mod}")
        except ImportError:
            print(f"   MISS  {mod}  (pip package: {pkg})")
            missing.append(pkg)
    if missing:
        print(f"\nFix:  pip install {' '.join(missing)}")
        print(f"  or:  pip install -r requirements.txt")
        sys.exit(1)

    step(2, "Checking network reach to shixiseng.com...")
    import requests
    try:
        r = requests.get(
            "https://www.shixiseng.com/interns",
            params={"city": "上海", "page": 1},
            headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"},
            timeout=15,
        )
        r.encoding = "utf-8"
        size_kb = len(r.text) // 1024
        print(f"   OK    HTTP {r.status_code}, {size_kb} KB returned")
        if r.status_code != 200:
            print(f"   WARN  non-200 status. Site may be blocking; try later or rotate UA.")
            sys.exit(1)
        if size_kb < 20:
            print(f"   WARN  response unusually small. Likely a block / captcha page.")
            sys.exit(1)
    except Exception as e:
        print(f"   FAIL  {type(e).__name__}: {e}")
        print(f"\nCheck: are you on a network that can reach shixiseng.com?")
        sys.exit(1)

    step(3, "Checking list-page selector still matches...")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")

    candidates = [
        ".intern-wrap",
        ".intern-item",
        ".intern-detail",
        ".job-list-box",
        "li[class*='intern']",
        "div[class*='intern-wrap']",
    ]
    found_any = False
    for sel in candidates:
        n = len(soup.select(sel))
        flag = "OK   " if n >= 5 else ("low  " if n > 0 else "miss ")
        print(f"   {flag} {sel!r:40s} -> {n} matches")
        if n >= 5:
            found_any = True

    if not found_any:
        print(f"\n   STALE  No selector matched ≥5 cards. Likely the page is JS-rendered now,")
        print(f"          or class names changed. Open the page in your browser, View Source,")
        print(f"          and search for the company names you see — note the wrapping element's")
        print(f"          class. Update shixiseng_adapter.py:list_selector accordingly.")
        print(f"\n          If View Source shows no company names but the rendered page does,")
        print(f"          the site went JS-rendered. You'll need Playwright instead of requests.")
        sys.exit(1)

    step(4, "Looking for font anti-bot signal...")
    import re
    woffs = re.findall(r'url\(["\']?([^)\'"]+\.woff[^)\'"]*)["\']?\)', r.text)
    if woffs:
        print(f"   FOUND {len(woffs)} .woff reference(s). Site uses font anti-bot — you MUST")
        print(f"          run extract_font_map.py before crawling, or salaries/digits will be garbled.")
        for w in woffs[:3]:
            print(f"          {w}")
    else:
        print(f"   NONE  No .woff in page HTML. Either site dropped font anti-bot, or it's loaded")
        print(f"          via JS. Do a dry-run; if you see □ in salaries, investigate.")

    print(f"\nAll core checks passed.")
    print(f"\nNext steps:")
    print(f"  1.  python extract_font_map.py        # builds font_extract/font_map.json")
    print(f"  2.  python shixiseng_adapter.py --pages 3 --dry-run")
    print(f"  3.  python shixiseng_adapter.py --pages 200    # the real run")


if __name__ == "__main__":
    main()
