#!/usr/bin/env python3
"""Builds /apps/ (index) and /apps/<slug>/ (one page per live iOS app) from the App Store.

Data comes from Apple's public iTunes lookup for developer id 1885918100, so the pages
always match what is live. Re-run after new apps go live:  python3 _build/build_app_pages.py
It also adds any missing app URLs to sitemap.xml.
"""
import html
import json
import re
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_ID = 1885918100
DEV_URL = "https://apps.apple.com/us/developer/tabish-hassan/id1885918100"
SITE = "https://tabishapps.com"
BEACON = """<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "baa3382c2e8f47f09e2a5a5f8474ebf0"}'></script><!-- End Cloudflare Web Analytics -->"""
TODAY = date.today().isoformat()
e = html.escape
LANGS = {"EN": "English", "UR": "Urdu", "AR": "Arabic", "ES": "Spanish", "FR": "French", "DE": "German", "HI": "Hindi", "ZH": "Chinese", "JA": "Japanese", "PT": "Portuguese", "IT": "Italian", "RU": "Russian", "TR": "Turkish", "KO": "Korean", "NL": "Dutch"}


def fetch():
    apps = {}
    for country in ("us", "gb"):
        url = f"https://itunes.apple.com/lookup?id={DEV_ID}&entity=software&limit=200&country={country}"
        with urllib.request.urlopen(url, timeout=30) as r:
            for a in json.load(r)["results"]:
                if a.get("wrapperType") == "software":
                    apps.setdefault(a["trackId"], a)
    return list(apps.values())


def split_name(name):
    """'CycleNote: Period Tracker' -> ('CycleNote', 'Period Tracker')."""
    m = re.split(r"\s*(?::|\s[-–—]\s)\s*", name, maxsplit=1)
    return (m[0].strip(), m[1].strip()) if len(m) == 2 else (name.strip(), "")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def linkify(text):
    return re.sub(r"(https?://[^\s)]+)", r'<a href="\1" rel="nofollow noopener">\1</a>', text)


def is_heading(line):
    letters = re.sub(r"[^A-Za-z]", "", line)
    return len(letters) >= 3 and letters.isupper() and len(line) < 90


def heading_text(line):
    t = line.strip().rstrip(":")
    # keep prices and product names readable: title-case words, but leave $ amounts alone
    return " ".join(w if re.search(r"[\d$€£]", w) else w.capitalize() for w in t.lower().split())


def render_description(desc):
    """App Store description -> (intro paragraph, HTML body)."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", desc.replace("\r", "")) if b.strip()]
    intro = blocks[0] if blocks else ""
    out = []
    for b in blocks[1:]:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if lines and is_heading(lines[0]):
            out.append(f"<h2>{e(heading_text(lines[0]))}</h2>")
            lines = lines[1:]
        items, para = [], []
        for l in lines:
            if re.match(r"^[-•*]\s+", l):
                if para:
                    out.append(f"<p>{linkify(e(' '.join(para)))}</p>")
                    para = []
                items.append(re.sub(r"^[-•*]\s+", "", l))
            else:
                if items:
                    out.append("<ul>" + "".join(f"<li>{linkify(e(i))}</li>" for i in items) + "</ul>")
                    items = []
                para.append(l)
        if items:
            out.append("<ul>" + "".join(f"<li>{linkify(e(i))}</li>" for i in items) + "</ul>")
        if para:
            out.append(f"<p>{linkify(e(' '.join(para)))}</p>")
    return intro, "\n  ".join(out)


def meta_desc(intro, limit=155):
    s = re.sub(r"\s+", " ", intro).strip()
    if len(s) <= limit:
        return s
    cut = s[:limit]
    dot = cut.rfind(". ")
    return cut[: dot + 1] if dot > 80 else cut.rsplit(" ", 1)[0] + "…"


def page_title(short, tagline):
    for t in (f"{short}: {tagline} app for iPhone" if tagline else f"{short} app for iPhone",
              f"{short}: {tagline} for iPhone" if tagline else f"{short} for iPhone",
              f"{short}: {tagline}" if tagline else short):
        if len(t) <= 60:
            return t
    return short


def size_mb(a):
    try:
        return f"{int(a['fileSizeBytes']) / 1_000_000:.0f} MB"
    except (KeyError, ValueError):
        return ""


def ipad(a):
    return any("ipad" in d.lower() for d in a.get("supportedDevices", []))


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f5f4ef">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{up}assets/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{up}assets/th.css">
<link rel="stylesheet" href="{up}blog/blog.css">
<link rel="stylesheet" href="{up}apps/apps.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header class="nav"><div class="bar">
  <a class="logo" href="{up}" aria-label="Tabish Hassan, home"><span class="mark">TH</span>Tabish Hassan</a>
  <ul><li><a href="{up}apps/">Apps</a></li><li><a href="{up}blog/">Blog</a></li><li><a href="{up}">Home</a></li></ul>
</div></header>
"""

FOOT = """<footer class="b-foot"><div class="wrap">
  <span>© 2026 Tabish Hassan · tabishapps.com</span>
  <span><a href="{up}apps/">All apps</a> · <a href="{up}support.html">App support</a> · <a href="{up}privacy-policy.html">App privacy</a> · <a href="{up}">Main site</a></span>
</div></footer>
""" + BEACON + """
</body>
</html>
"""


def app_page(a, slug, related):
    short, tagline = split_name(a["trackName"])
    intro, body = render_description(a.get("description", ""))
    url = f"{SITE}/apps/{slug}/"
    title = page_title(short, tagline)
    # Short slogan intros ("Tip smarter.") make weak search snippets: add the next plain sentences.
    plain = [l.strip() for l in a.get("description", "").split("\n")
             if l.strip() and not is_heading(l.strip()) and not re.match(r"^[-•*]\s+", l.strip())]
    desc = meta_desc(intro if len(intro) >= 90 else " ".join(plain[:4]))
    store = a["trackViewUrl"].split("?")[0]
    icon = a.get("artworkUrl512") or a.get("artworkUrl100")
    shots = (a.get("screenshotUrls") or [])[:6]
    premium = bool(re.search(r"premium|pro\b|subscription|lifetime|in-app", a.get("description", ""), re.I))
    no_account = bool(re.search(r"no (account|sign[- ]?in|sign[- ]?up)", a.get("description", ""), re.I))
    devices = "iPhone and iPad" if ipad(a) else "iPhone"
    ios = a.get("minimumOsVersion", "")
    genre = a.get("primaryGenreName", "")

    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": a["trackName"],
          "operatingSystem": f"iOS {ios}+" if ios else "iOS", "applicationCategory": genre,
          "url": url, "image": icon, "downloadUrl": store,
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
          "author": {"@type": "Person", "name": "Tabish Hassan", "url": SITE + "/"}}
    if a.get("userRatingCount"):
        ld["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": round(a["averageUserRating"], 1),
                                 "ratingCount": a["userRatingCount"]}

    faq = [(f"Is {short} free?",
            f"Yes, {short} is free to download." + (" Some extra features are part of an optional Premium upgrade, described above." if premium else ""))]
    if no_account:
        faq.append((f"Do I need an account to use {short}?", f"No. {short} works without an account or sign-in."))
    faq.append((f"Which devices does {short} work on?",
                f"{short} runs on {devices}" + (f" with iOS {ios} or newer." if ios else ".")))
    faq.append((f"Who made {short}?",
                f'{short} is made by Tabish Hassan, an independent developer. Questions or problems: <a href="../../support.html">app support</a>.'))

    glance = [("Category", e(genre)), ("Price", "Free" + (", optional Premium" if premium else "")),
              ("Works on", f"{devices}, iOS {e(ios)}+" if ios else devices), ("Size", size_mb(a)),
              ("Age rating", e(a.get("contentAdvisoryRating", ""))),
              ("Languages", e(", ".join(LANGS.get(c, c) for c in a.get("languageCodesISO2A", [])))),]
    glance = [g for g in glance if g[1]]

    rel = "".join(
        f'<a class="app-mini" href="../{s}/"><img src="{e(r.get("artworkUrl100", ""))}" alt="" width="56" height="56" loading="lazy"><span><b>{e(split_name(r["trackName"])[0])}</b>{e(split_name(r["trackName"])[1])}</span></a>'
        for r, s in related)

    shots_html = "".join(
        f'<img src="{e(u)}" alt="{e(short)} screenshot {i + 1}" loading="lazy" width="392" height="696">' for i, u in enumerate(shots))

    head = HEAD.format(title=e(title), desc=e(desc), url=url, image=e(icon), up="../../",
                       ld=json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))
    return head + f"""
<main class="article app-page"><div class="wrap">
  <div class="meta mono"><a href="../">Apps</a><span>{e(genre)}</span><span>Free on the App Store</span></div>
  <div class="app-hero">
    <img class="app-icon" src="{e(icon)}" alt="{e(short)} app icon" width="120" height="120">
    <div><h1>{e(short)}</h1>{f'<p class="app-tag">{e(tagline)}</p>' if tagline else ''}</div>
  </div>
  <p class="lede">{linkify(e(intro))}</p>
  <div class="cta-row"><a class="btn primary" href="{e(store)}" rel="noopener">Download on the App Store <span class="arr">↗</span></a></div>

  {f'<div class="app-shots" aria-label="Screenshots">{shots_html}</div>' if shots else ''}

  <div class="table-scroll"><table class="glance"><tbody>
    {''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in glance)}
  </tbody></table></div>

  {body}

  <h2>Questions</h2>
  {''.join(f'<h3>{e(q)}</h3><p>{a_}</p>' for q, a_ in faq)}

  <div class="cta-row"><a class="btn primary" href="{e(store)}" rel="noopener">Get {e(short)} free <span class="arr">↗</span></a><a class="btn" href="../">See all apps <span class="arr">→</span></a></div>

  {f'<h2>More {e(genre.lower())} apps</h2><div class="app-grid small">{rel}</div>' if rel else ''}
</div></main>

""" + FOOT.replace("{up}", "../../")


CSS = """/* App pages. Builds on assets/th.css and blog/blog.css. Generated by _build/build_app_pages.py */
.app-hero { display: flex; align-items: center; gap: 22px; margin-top: 22px; }
.app-icon { width: 120px; height: 120px; border-radius: 27px; border: 1px solid var(--line); flex: none; }
.app-page h1 { margin: 0; }
.app-tag { margin: 8px 0 0; font-size: 20px; color: var(--ink-2); }
.app-page .btn, .apps-index .btn { text-decoration: none; }
.app-page .btn:not(.primary) { color: var(--ink); }
.app-page .btn.primary { color: var(--bone); }
.cta-row { display: flex; flex-wrap: wrap; gap: 12px; margin: 26px 0 8px; }
.app-shots { display: flex; gap: 14px; overflow-x: auto; margin: 34px 0; padding-bottom: 8px; scroll-snap-type: x mandatory; }
.app-shots img { height: 460px; width: auto; border-radius: 22px; border: 1px solid var(--line); scroll-snap-align: start; flex: none; }
.glance th { text-align: left; color: var(--muted); font-weight: 500; width: 140px; }
.app-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin: 18px 0 10px; }
.app-mini { display: flex; align-items: center; gap: 14px; padding: 14px; border-radius: 18px; background: var(--card); border: 1px solid var(--line); text-decoration: none !important; color: var(--ink) !important; transition: border-color .2s ease; }
.app-mini:hover { border-color: var(--ink); }
.app-mini img { width: 56px; height: 56px; border-radius: 13px; border: 1px solid var(--line); flex: none; }
.app-mini span { display: flex; flex-direction: column; font-size: 15px; line-height: 1.3; color: var(--ink-2); }
.app-mini b { font-size: 16.5px; color: var(--ink); }
.apps-index h2 { scroll-margin-top: 100px; }
.cat-links { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 20px; }
.cat-links a { padding: 7px 14px; border-radius: 999px; border: 1px solid var(--line); font-size: 14px; text-decoration: none !important; color: var(--ink) !important; }
.cat-links a:hover { border-color: var(--ink); }
@media (max-width: 600px) {
  .app-icon { width: 84px; height: 84px; border-radius: 19px; }
  .app-shots img { height: 380px; }
}
"""


def index_page(entries):
    by_genre = defaultdict(list)
    for a, slug in entries:
        by_genre[a.get("primaryGenreName", "Other")].append((a, slug))
    genres = sorted(by_genre, key=lambda g: (-len(by_genre[g]), g))
    n = len(entries)
    title = f"{n} free iPhone apps by Tabish Hassan"
    desc = f"All {n} of my iPhone apps in one place: trackers, timers, finance, health, education and games. Free on the App Store, many work without an account."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": f"{SITE}/apps/",
          "about": {"@type": "Person", "name": "Tabish Hassan", "url": SITE + "/"}}
    sections = []
    for g in genres:
        cards = "".join(
            f'<a class="app-mini" href="{s}/"><img src="{e(a.get("artworkUrl100", ""))}" alt="" width="56" height="56" loading="lazy"><span><b>{e(split_name(a["trackName"])[0])}</b>{e(split_name(a["trackName"])[1] or g)}</span></a>'
            for a, s in sorted(by_genre[g], key=lambda x: x[0]["trackName"].lower()))
        sections.append(f'<h2 id="{slugify(g)}">{e(g)} <span class="mono" style="color:var(--muted)">{len(by_genre[g])}</span></h2><div class="app-grid">{cards}</div>')
    head = HEAD.format(title=e(title), desc=e(desc), url=f"{SITE}/apps/", image=e(entries[0][0].get("artworkUrl512", "")),
                       up="../", ld=json.dumps(ld, ensure_ascii=False))
    return head + f"""
<main class="article apps-index"><div class="wrap" style="max-width:1100px">
  <div class="meta mono"><span>iPhone apps</span><span>{n} apps</span><span>Updated {date.today().strftime('%-d %B %Y')}</span></div>
  <h1>{n} iPhone apps, all free to download</h1>
  <p class="lede">Small, focused apps for everyday jobs: tracking money, health and habits, learning, family life and sport. Each page shows what the app does, screenshots and the App Store link.</p>
  <div class="cat-links">{''.join(f'<a href="#{slugify(g)}">{e(g)}</a>' for g in genres)}</div>
  {''.join(sections)}
  <p style="margin-top:40px"><a href="{DEV_URL}" rel="noopener">See them all on the App Store ↗</a></p>
</div></main>

""" + FOOT.replace("{up}", "../")


def main():
    apps = fetch()
    apps.sort(key=lambda a: a["trackName"].lower())
    used, entries = set(), []
    for a in apps:
        slug = slugify(split_name(a["trackName"])[0]) or str(a["trackId"])
        if slug in used:
            slug = f"{slug}-{a['trackId']}"
        used.add(slug)
        entries.append((a, slug))

    out = ROOT / "apps"
    out.mkdir(exist_ok=True)
    (out / "apps.css").write_text(CSS)
    by_genre = defaultdict(list)
    for a, s in entries:
        by_genre[a.get("primaryGenreName")].append((a, s))
    for a, slug in entries:
        related = [x for x in by_genre[a.get("primaryGenreName")] if x[1] != slug][:6]
        (out / slug).mkdir(exist_ok=True)
        (out / slug / "index.html").write_text(app_page(a, slug, related))
    (out / "index.html").write_text(index_page(entries))

    sm = ROOT / "sitemap.xml"
    x = sm.read_text()
    urls = [f"{SITE}/apps/"] + [f"{SITE}/apps/{s}/" for _, s in entries]
    add = "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls if f"<loc>{u}</loc>" not in x)
    if add:
        sm.write_text(x.replace("</urlset>", add + "</urlset>"))
    print(f"{len(entries)} app pages + index written; {add.count('<url>')} sitemap entries added")


if __name__ == "__main__":
    main()
