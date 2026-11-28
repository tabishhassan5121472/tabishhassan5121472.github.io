#!/usr/bin/env python3
"""SEO pass for every blog article. Safe to run again and again.

Run after adding or editing an article:
    cd tabishapps-site && python3 _build/blog_seo.py

For each blog/<slug>/index.html it:
  - replaces the head JSON-LD with an Article + BreadcrumbList graph
    (datePublished, dateModified from git, author linked to /about/, image, publisher);
  - adds an RSS <link rel="alternate">;
  - adds a visible breadcrumb under the article header;
  - replaces the closing "Written by" line with an author box and 3 related articles
    (same topic cluster first), so every article links to others;
  - writes blog/feed.xml (RSS) and keeps sitemap.xml lastmod in step.
Articles are read from the pages themselves; add a slug to CLUSTER for a new topic.
"""
import html, json, re, subprocess, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
SITE = "https://tabishapps.com"
PERSON = {
    "@type": "Person", "@id": SITE + "/#me", "name": "Tabish Hassan",
    "url": SITE + "/about/", "jobTitle": "Software developer",
    "sameAs": ["https://github.com/tabishhassan5121472", "https://x.com/TabishHassanDev",
               "https://dev.to/tabishhassan5121472", "https://tabishhassan.hashnode.dev",
               "https://apps.apple.com/us/developer/tabish-hassan/id1885918100"],
}
# Topic clusters, for related links. Unknown slugs fall back to "ai-coding".
CLUSTER = {
    "prompt-caching-coding-agents": "ai-coding", "code-mode-tool-calls-test": "ai-coding",
    "ai-slop-design-skills-test": "ai-coding", "ai-agents-business-apps-test": "ai-coding",
    "claude-code-token-usage-small-edits": "ai-coding",
    "add-subtitles-to-video-offline-mac": "local-ai",
    "small-business-website-cost": "business",
}
CLUSTER_NAME = {"ai-coding": "AI coding agents", "local-ai": "Local AI on the Mac",
                "build-with-ai": "Building apps with AI", "business": "Guides for businesses"}


def git_date(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    return out or datetime.date.today().isoformat()


def grab(pattern, text, default=""):
    m = re.search(pattern, text, re.S)
    return html.unescape(m.group(1)).strip() if m else default


def read_posts():
    posts = []
    for page in sorted(BLOG.glob("*/index.html")):
        h = page.read_text()
        slug = page.parent.name
        h1 = re.sub(r"<[^>]+>", "", grab(r"<h1[^>]*>(.*?)</h1>", h))
        posts.append({
            "slug": slug, "path": page, "url": f"{SITE}/blog/{slug}/",
            "h1": h1, "title": grab(r"<title>(.*?)</title>", h, h1),
            "desc": grab(r'<meta name="description" content="([^"]*)"', h),
            "image": grab(r'<meta property="og:image" content="([^"]*)"', h),
            "kind": grab(r'<div class="meta mono"><span>([^<]+)</span>', h, "Article"),
            "published": grab(r'"datePublished":\s*"([^"]+)"', h) or git_date(page),
            "modified": git_date(page),
            "cluster": CLUSTER.get(slug, "ai-coding"),
        })
    posts.sort(key=lambda p: p["published"], reverse=True)
    return posts


def related(post, posts, n=3):
    others = [p for p in posts if p["slug"] != post["slug"]]
    same = [p for p in others if p["cluster"] == post["cluster"]]
    rest = [p for p in others if p["cluster"] != post["cluster"]]
    return (same + rest)[:n]


def faq_items(h):
    """Q&A pairs from <section class="faq"><h3>Question?</h3><p>Answer</p>... for FAQPage schema."""
    m = re.search(r'<section class="faq">(.*?)</section>', h, re.S)
    if not m:
        return []
    pairs = re.findall(r"<h3[^>]*>(.*?)</h3>\s*(.*?)(?=<h3|$)", m.group(1), re.S)
    clean = lambda x: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))).strip()
    return [{"@type": "Question", "name": clean(q), "acceptedAnswer": {"@type": "Answer", "text": clean(a)}}
            for q, a in pairs if clean(q) and clean(a)]


def graph(p):
    art = {
        "@type": "BlogPosting", "@id": p["url"] + "#article", "headline": p["h1"][:110],
        "description": p["desc"], "datePublished": p["published"],
        "dateModified": max(p["modified"], p["published"]), "author": {"@id": SITE + "/#me"},
        "publisher": {"@id": SITE + "/#me"}, "mainEntityOfPage": p["url"], "inLanguage": "en",
        "articleSection": CLUSTER_NAME[p["cluster"]],
    }
    if p["image"]:
        art["image"] = p["image"]
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
        {"@type": "ListItem", "position": 3, "name": p["h1"][:80], "item": p["url"]}]}
    nodes = [art, crumbs, PERSON]
    faqs = faq_items(p["path"].read_text())
    if faqs:
        nodes.append({"@type": "FAQPage", "mainEntity": faqs})
    return {"@context": "https://schema.org", "@graph": nodes}


def esc(s):
    return html.escape(s, quote=True)


def apply(p, posts):
    h = p["path"].read_text()
    head_block = ("<!--seo:head-->\n<link rel=\"alternate\" type=\"application/rss+xml\" title=\"Tabish Hassan's blog\" href=\"/blog/feed.xml\">\n"
                  "<style>.crumbs{display:flex;gap:8px;flex-wrap:wrap;font-size:14px;color:var(--muted);margin-bottom:14px}.crumbs a{color:var(--muted);text-decoration:none}"
                  ".author-box{display:flex;gap:16px;align-items:flex-start;margin:50px 0 0;padding:22px;border:1px solid var(--line);border-radius:18px;background:var(--card)}"
                  ".author-box .av{flex:0 0 52px;height:52px;border-radius:50%;display:grid;place-items:center;background:var(--ink);color:var(--bone);font:700 18px var(--display)}"
                  ".author-box p{margin:0 0 6px;font-size:16px}.related{margin:34px 0 0}.related h2{font-size:24px;margin:0 0 12px}"
                  ".related a.r{display:block;padding:14px 0;border-top:1px solid var(--line);text-decoration:none;color:inherit}.related a.r b{display:block;font-size:17px}"
                  ".related a.r span{font-size:14px;color:var(--muted)}</style>\n"
                  "<script type=\"application/ld+json\">\n" + json.dumps(graph(p), ensure_ascii=False) + "\n</script>\n<!--/seo:head-->")
    if "<!--seo:head-->" in h:
        h = re.sub(r"<!--seo:head-->.*?<!--/seo:head-->", lambda m: head_block, h, flags=re.S)
    else:
        h, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: head_block, h, count=1, flags=re.S)
        if not n:
            h = h.replace("</head>", head_block + "\n</head>", 1)

    crumb = (f'<!--seo:crumb--><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>›</span>'
             f'<a href="/blog/">Blog</a><span>›</span><span>{esc(CLUSTER_NAME[p["cluster"]])}</span></nav><!--/seo:crumb-->')
    if "<!--seo:crumb-->" in h:
        h = re.sub(r"<!--seo:crumb-->.*?<!--/seo:crumb-->", lambda m: crumb, h, flags=re.S)
    else:
        h = h.replace('<main class="article"><div class="wrap">', '<main class="article"><div class="wrap">\n  ' + crumb, 1)

    rel = "".join(f'<a class="r" href="/blog/{r["slug"]}/"><b>{esc(r["h1"])}</b><span>{esc(r["kind"])} · {esc(CLUSTER_NAME[r["cluster"]])}</span></a>'
                  for r in related(p, posts))
    foot = ('<!--seo:foot--><div class="author-box"><div class="av">TH</div><div>'
            '<p><b>Written by <a href="/about/">Tabish Hassan</a></b>, a software developer in Pakistan. '
            '4+ years of production React and TypeScript, 75 iOS apps on the App Store. The tests on this blog run on my own Mac, with the method and limits shown.</p>'
            '<p>Found a mistake or got different numbers? Email <a href="mailto:hello@tabishapps.com">hello@tabishapps.com</a>. '
            f'Published {p["published"]}' + (f', updated {p["modified"]}' if p["modified"] > p["published"] else "") + '.</p></div></div>'
            f'<section class="related"><h2>Read next</h2>{rel}</section><!--/seo:foot-->')
    if "<!--seo:foot-->" in h:
        h = re.sub(r"<!--seo:foot-->.*?<!--/seo:foot-->", lambda m: foot, h, flags=re.S)
    else:
        h, n = re.subn(r'\s*<p style="margin-top:40px;color:var\(--muted,#666\)">Written by.*?</p>', lambda m: "\n  " + foot, h, count=1, flags=re.S)
        if not n:
            h = h.replace("</div></main>", "  " + foot + "\n</div></main>", 1)
    p["path"].write_text(h)


def feed(posts):
    items = "".join(
        f"<item><title>{esc(p['h1'])}</title><link>{p['url']}</link><guid>{p['url']}</guid>"
        f"<pubDate>{datetime.date.fromisoformat(p['published']).strftime('%a, %d %b %Y')} 12:00:00 +0500</pubDate>"
        f"<description>{esc(p['desc'])}</description></item>\n" for p in posts)
    (BLOG / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>Tabish Hassan's blog</title><link>{SITE}/blog/</link>"
        "<description>Hands-on tests of AI coding tools, local AI and software building.</description>"
        "<language>en</language>\n" + items + "</channel></rss>\n")


def sitemap(posts):
    sm = ROOT / "sitemap.xml"
    s = sm.read_text()
    for p in posts:
        loc = f"<loc>{p['url']}</loc>"
        mod = max(p["modified"], p["published"])
        if loc in s:
            s = re.sub(re.escape(loc) + r"<lastmod>[^<]*</lastmod>", f"{loc}<lastmod>{mod}</lastmod>", s)
        else:
            s = s.replace("</urlset>", f"  <url>{loc}<lastmod>{mod}</lastmod></url>\n</urlset>")
    if f"<loc>{SITE}/about/</loc>" not in s:
        s = s.replace("</urlset>", f"  <url><loc>{SITE}/about/</loc><lastmod>{datetime.date.today()}</lastmod></url>\n</urlset>")
    sm.write_text(s)


if __name__ == "__main__":
    posts = read_posts()
    for p in posts:
        apply(p, posts)
    feed(posts)
    sitemap(posts)
    missing = [p["slug"] for p in posts if not p["image"]]
    print(f"{len(posts)} articles updated; feed.xml and sitemap written.")
    if missing:
        print("No og:image (make a 1200x630 card):", ", ".join(missing))
