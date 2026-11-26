#!/usr/bin/env python3
"""Make a 1200x630 share card (og:image) with headless Chrome.

    python3 _build/og_card.py <slug> "Big line" "Small line" [label]

Writes blog/<slug>/card.jpg and sets og:image / twitter:image on blog/<slug>/index.html
if the page has none. For test articles, prefer a real result card with a chart;
this is for guides and any article that lacks an image.
"""
import html, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def card(slug, big, small, label="tabishapps.com/blog"):
    out_dir = ROOT / "blog" / slug
    page = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:B;src:url('{ROOT}/assets/fonts/bricolage.woff2')}}
html,body{{margin:0;width:1200px;height:630px;background:#f5f4ef;font-family:B,system-ui,sans-serif;color:#141414}}
.c{{box-sizing:border-box;width:1200px;height:630px;padding:70px 80px;display:flex;flex-direction:column;justify-content:space-between;border-left:24px solid #2b4cff}}
.k{{font:600 24px ui-monospace,Menlo,monospace;color:#2b4cff;letter-spacing:.04em;text-transform:uppercase}}
h1{{margin:0;font-size:{64 if len(big) < 60 else 54}px;line-height:1.02;letter-spacing:-.035em;font-weight:700}}
p{{margin:18px 0 0;font-size:30px;line-height:1.3;color:#444}}
.f{{display:flex;justify-content:space-between;font:500 24px ui-monospace,Menlo,monospace;color:#666}}
</style><div class="c"><div class="k">{html.escape(label)}</div><div><h1>{html.escape(big)}</h1><p>{html.escape(small)}</p></div>
<div class="f"><span>Tabish Hassan</span><span>tabishapps.com</span></div></div>"""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "card.html"
        src.write_text(page)
        png = Path(tmp) / "card.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--blink-settings=preferredColorScheme=1", "--window-size=1200,630",
                        f"--screenshot={png}", f"file://{src}"], check=True, capture_output=True)
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png),
                        "--out", str(out_dir / "card.jpg")], check=True, capture_output=True)
    idx = out_dir / "index.html"
    h = idx.read_text()
    if 'property="og:image"' not in h:
        url = f"https://tabishapps.com/blog/{slug}/card.jpg"
        tags = (f'<meta property="og:image" content="{url}">\n<meta property="og:image:width" content="1200">\n'
                f'<meta property="og:image:height" content="630">\n<meta name="twitter:image" content="{url}">\n')
        h = re.sub(r'<meta name="twitter:card" content="[^"]*">\n?', "", h)
        tags += '<meta name="twitter:card" content="summary_large_image">\n'
        h = re.sub(r'(<meta property="og:url"[^>]*>\n)', lambda m: m.group(1) + tags, h, count=1)
        if url not in h:
            h = h.replace("</head>", tags + "</head>", 1)
        idx.write_text(h)
    print("wrote", out_dir / "card.jpg")


if __name__ == "__main__":
    card(*sys.argv[1:])
