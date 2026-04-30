# Encoding Recipes — the 5 most common decoding pitfalls

If your output has any of these symptoms, the matching recipe below fixes it.
Check them in order — earlier layers cause damage that looks like later-layer bugs.

| Symptom | Likely cause | Recipe |
|---|---|---|
| All Chinese is garbage (`Â¥`, `ä¸­`) | HTTP encoding wrong | §1 |
| Numbers are `□` or salaries look like `□□-□□/天` | Font-glyph anti-bot | §2 |
| Random `&amp;`, `&#x6587;`, `&nbsp;` in output | HTML entities not decoded | §3 |
| Page works in browser, returns blank/`<div id="app"></div>` to `requests` | JS-rendered SPA | §4 |
| Field looks like `eyJjb21wYW55Ijoi...` (long base64) | Base64-encoded payload | §5 |

---

## §1. HTTP response encoding (the 30-second bug that wastes 3 hours)

`requests` defaults to `ISO-8859-1` when the server sends no `charset` in the Content-Type header. Many older CN sites (政府网站、学校就业网、部分招聘站) do exactly this. Result: every Chinese character is silently mangled, and `BeautifulSoup` happily parses the garbage.

```python
r = session.get(url, ...)
# ALWAYS set this explicitly. Don't trust r.apparent_encoding either — it's a guess.
r.encoding = "utf-8"      # 95% of CN sites
# r.encoding = "gbk"      # some older sites (.gov.cn, school career sites)
soup = BeautifulSoup(r.text, "html.parser")
```

**How to verify**: print `r.text[:200]` after setting encoding. If you see readable Chinese, you're good. If you see `Â¥` or `ä¸­`, switch encoding.

---

## §2. Font-glyph anti-bot (实习僧, 58同城, 大众点评, 猫眼...)

The site renders certain characters (digits in salaries, key chars in titles, sometimes addresses) using **private-use Unicode codepoints** (U+E000 to U+F8FF). A custom WOFF font maps those codepoints to glyph shapes that look like real digits/chars — but `r.text` only sees the codepoint.

You see `-/天` in raw HTML; the browser shows `200-300/天`.

### Building the font_map (one-time per site, refresh every few days)

```python
# pip install fonttools
from fontTools.ttLib import TTFont
import requests, io

# 1. Get the .woff URL from DevTools → Network → filter "woff"
woff_url = "https://www.shixiseng.com/interns/iconfonts/file?rand=...woff"
font = TTFont(io.BytesIO(requests.get(woff_url).content))

# 2. Inspect glyph names. Site authors usually name them after what they render:
#    "uniE001" → renders as "0", "uniE002" → "1", etc.
#    For confusing cases, render the glyph to PNG and OCR it (or eyeball).
cmap = font.getBestCmap()  # {codepoint: glyph_name}

# 3. Build the substitution map. Manual mapping is fine — there are usually ≤30 glyphs.
font_map = {
    "": "0", "": "1", "": "2", "": "3", "": "4",
    "": "5", "": "6", "": "7", "": "8", "": "9",
    # plus any 汉字 swaps the site uses for titles
}
```

### Rotation handling

Most sites rotate the font daily (codepoint→glyph mapping changes; same glyph might be `` today and `` tomorrow). Two strategies:

- **Cache + refresh**: store the font_map keyed by woff URL hash. When you see `\u` chars in output, re-extract.
- **Glyph-shape OCR**: render each glyph to a small PNG, run a tiny image hash, compare against a fixed reference set of digit/char shapes. Slower to set up, but survives rotation forever.

Start with manual mapping. Only build the OCR pipeline if you're crawling regularly.

---

## §3. HTML entities

`&amp;`, `&nbsp;`, `&#x6587;`, `&#25991;` all need to be decoded. `BeautifulSoup` decodes most automatically when you call `.get_text()`, but **not** when you read `.text` from the response or extract via regex.

```python
import html
clean = html.unescape(raw_text)   # handles &amp;, &#x6587;, &#25991; all at once
```

The `clean_text()` helper in `template_crawler.py` calls this for you. Always route field extraction through it.

---

## §4. JS-rendered SPA (BOSS直聘, 拉勾, 猎聘 detail pages)

If `r.text` is short and contains `<div id="app"></div>` or similar, the page is rendered client-side. `requests` will never see the data — switch to Playwright:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 ...",
        locale="zh-CN", timezone_id="Asia/Shanghai",
    )
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(2000)        # let JS settle
    cards = page.eval_on_selector_all("a[href*='/job/']", """
        els => els.map(a => ({href: a.href, text: a.innerText}))
    """)
    browser.close()
```

The 5 disciplines still apply — just substitute `page.goto` for `request_with_retry` and `eval_on_selector_all` for `soup.select`.

**Stealth**: `--disable-blink-features=AutomationControlled` removes the most obvious bot signal. For BOSS直聘 you may need `playwright-stealth` plugin.

---

## §5. Base64 / encrypted field bodies

Some sites (less common in jobs vertical) ship the actual content as base64 in a JS variable, decoded client-side. Symptom: a long alphanumeric string in the HTML where you expected text.

```python
import base64, json
raw = re.search(r'window\.__DATA__\s*=\s*"([^"]+)"', html_text).group(1)
decoded = base64.b64decode(raw).decode("utf-8")
data = json.loads(decoded)
```

If it's encrypted (AES/DES with a key embedded in JS), the fastest path is usually a Playwright RPC: load the page in a headless browser, evaluate the site's own decode function with `page.evaluate(...)`, return the result. See the ResuMiner `crypto_engine` pattern in this user's repo for a worked RPC server example.

---

## Decoding sanity check

After every crawl, run this quick QC on the output CSV:

```python
import pandas as pd
df = pd.read_csv("raw/output.csv")
for col in df.select_dtypes(include="object"):
    sus = df[col].astype(str).str.contains(r"[-]|&#x|&amp;|□", regex=True)
    if sus.any():
        print(f"  {col}: {sus.sum()} rows still have decoding artifacts")
```

If anything prints, you skipped a layer. Don't proceed to analysis.
