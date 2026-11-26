#!/usr/bin/env python3
"""Pre-publish quality gate for one blog article.

    python3 _build/article_check.py blog/<slug>/index.html [--keyword "claude code vs cursor"]

Checks the SEO and readability basics and prints PASS/FIX lines plus a score.
The daily task must fix every FIX line before publishing (score 100 = all pass).
"""
import html, json, re, sys
from pathlib import Path

args = sys.argv[1:]
kw = ""
if "--keyword" in args:
    i = args.index("--keyword"); kw = args[i + 1].lower(); del args[i:i + 2]
path = Path(args[0])
h = path.read_text()
head, body = h.split("</head>", 1)
main = body.split("<main", 1)[-1].split("</main>", 1)[0]
text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", main, flags=re.S)))
words = re.findall(r"[A-Za-z0-9$%][\w'.,%$-]*", text)
sentences = [s for s in re.split(r"[.!?]\s", text) if len(s.split()) > 3]


def g(p, s=head):
    m = re.search(p, s, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


title = g(r"<title>(.*?)</title>")
desc = g(r'<meta name="description" content="([^"]*)"')
h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", main, re.S)
h2s = [html.unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", main, re.S)]
imgs = re.findall(r"<img[^>]*>", main)
links = re.findall(r'href="([^"#]+)"', main)
internal = {l for l in links if (l.startswith("/") or "tabishapps.com" in l) and "/blog/" in l}
external = {l for l in links if l.startswith("http") and "tabishapps.com" not in l}
first_para = text[:900].lower()

checks = []
def c(ok, name, fix):
    checks.append((ok, name, fix))

c(20 <= len(title) <= 60, f"<title> length {len(title)}", "keep it 20-60 characters, main keyword first")
c(110 <= len(desc) <= 160, f"meta description length {len(desc)}", "110-160 characters, with the result or answer")
c(len(h1s) == 1, f"{len(h1s)} H1", "exactly one H1")
c(len(h2s) >= 4, f"{len(h2s)} H2 sections", "at least 4 H2s; phrase some as the questions people search")
c('rel="canonical"' in head, "canonical link", "add <link rel=canonical>")
c('property="og:image"' in head and 'twitter:card' in head, "share image (og:image + twitter card)", "make a 1200x630 card (_build/og_card.py or a result card)")
c('"BlogPosting"' in head and '"BreadcrumbList"' in head, "Article + Breadcrumb schema", "run _build/blog_seo.py")
c(all("alt=" in i and 'alt=""' not in i for i in imgs), f"alt text on {len(imgs)} images", "describe each image in alt text")
c(len(imgs) >= 1, f"{len(imgs)} images", "at least 1 in the article (the result card); tests should also show a real screenshot or chart")
c(len(internal) >= 3, f"{len(internal)} links to other articles", "run _build/blog_seo.py (adds Read next) and link 1-2 inline")
c(len(external) >= 2, f"{len(external)} source links", "link the source post and official docs")
c(any(w in first_para for w in ("result", "answer", "short", "test", "tl;dr")) or 'class="summary"' in main,
  "answer or result in the first lines", "put the 3-line summary with the result first at the top")
c('<section class="faq">' in main, "FAQ section (FAQPage schema)", "add <section class=faq> with an H2 and 3-5 <h3>question</h3><p>answer</p> pairs from real searches")
c(len(words) >= 900, f"{len(words)} words", "aim for 900+ words of real substance (no padding)")
avg = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
c(avg <= 20, f"average sentence {avg:.0f} words", "shorter sentences (readers are often non-native)")
if kw:
    k = kw.lower()
    c(k in title.lower() or all(w in title.lower() for w in k.split()), f"keyword in title", "put the main keyword in <title>")
    c(k in (h1s[0].lower() if h1s else ""), "keyword in H1", "use the keyword naturally in the H1")
    c(k in first_para, "keyword in the first paragraph", "mention it in the first 100 words")
    c(any(all(w in x.lower() for w in k.split()) for x in h2s), "keyword in an H2", "use it in at least one H2")
for m in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', head, re.S):
    try:
        json.loads(m)
    except Exception:
        c(False, "JSON-LD parses", "fix the JSON-LD")

passed = sum(1 for ok, _, _ in checks if ok)
for ok, name, fix in checks:
    print(("PASS " if ok else "FIX  ") + name + ("" if ok else f"  ->  {fix}"))
print(f"\nSCORE {round(100 * passed / len(checks))}/100  ({passed} of {len(checks)} checks)")
