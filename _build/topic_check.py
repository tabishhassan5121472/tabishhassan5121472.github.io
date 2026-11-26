#!/usr/bin/env python3
"""Will this topic get views? A free, rough check before writing an article.

    python3 _build/topic_check.py "claude code vs cursor" ["other topic" ...] [--tag ai]

Uses only free public endpoints, and sends only the topic words:
  1. Google autocomplete: do people search this, and which phrasings? (search demand)
  2. Hacker News (Algolia API): how did similar stories do in the last 12 months? (share demand)
  3. dev.to API: how many articles already exist for the tag, and how they did. (competition, reach)
Prints a 0-10 score per signal, a total, and the best search phrasings to use in the title,
H2s and FAQ. It is a guide, not a promise: a strong test with a clear chart can still win
on a weak topic, and a weak article will lose on a strong one.
"""
import json, statistics, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "topic-check/1.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def autocomplete(q):
    data = get("https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q=" + urllib.parse.quote(q))
    return data[1] if len(data) > 1 else []


def search_signal(topic):
    phrasings = set()
    exact = 0
    for prefix in ["", "how to ", "best ", "why "]:
        s = autocomplete(prefix + topic)
        phrasings.update(s)
        exact += sum(1 for x in s if topic.lower() in x.lower())
        time.sleep(0.3)
    for suffix in [" vs", " cost", " 2026", " tutorial"]:
        s = autocomplete(topic + suffix)
        phrasings.update(s)
        time.sleep(0.3)
    words = [w for w in topic.lower().split() if len(w) > 2]
    on_topic = sorted((x for x in phrasings if all(w in x.lower() for w in words)), key=len)
    # Google only suggests phrasings that real people type often, so many on-topic
    # suggestions = real search demand.
    score = min(10, round(len(on_topic) / 2))
    return score, on_topic[:15]


def hn_signal(topic):
    since = int(time.time()) - 365 * 86400
    url = ("https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=50&restrictSearchableAttributes=title&typoTolerance=false&advancedSyntax=true&numericFilters=created_at_i>%d&query=%s"
           % (since, urllib.parse.quote(" ".join('"%s"' % w for w in topic.split()))))
    hits = get(url).get("hits", [])
    pts = sorted((h.get("points") or 0 for h in hits), reverse=True)
    top = [(h.get("points") or 0, h.get("title")) for h in sorted(hits, key=lambda h: -(h.get("points") or 0))[:5]]
    if not pts:
        return 0, 0, 0, top
    med = statistics.median(pts)
    big = sum(1 for p in pts if p >= 100)
    score = min(10, round(big * 1.5 + min(4, med / 25)))
    return score, len(pts), big, top


def devto_signal(topic, tag=None):
    tag = tag or "".join(ch for ch in topic.lower().split()[0] if ch.isalnum())
    arts = get(f"https://dev.to/api/articles?per_page=30&top=365&tag={urllib.parse.quote(tag)}")
    if not arts:
        return 0, tag, 0
    reacts = [a.get("public_reactions_count", 0) for a in arts]
    med = statistics.median(reacts)
    return min(10, round(med / 10)), tag, med


if __name__ == "__main__":
    args = sys.argv[1:] or ["claude code vs cursor"]
    tag = None
    if "--tag" in args:
        i = args.index("--tag"); tag = args[i + 1]; del args[i:i + 2]
    for t in args:
        s_score, phr = search_signal(t)
        h_score, n, big, top = hn_signal(t)
        try:
            d_score, used, med = devto_signal(t, tag)
        except Exception:
            d_score, used, med = 0, "-", 0
        total = round(s_score * 0.45 + h_score * 0.35 + d_score * 0.2, 1)
        verdict = "GO" if total >= 5 else ("MAYBE: needs a strong original result" if total >= 3 else "SKIP or rephrase")
        print(f"\n=== {t} ===")
        print(f"Search demand  {s_score}/10  ({len(phr)} Google phrasings)")
        print(f"Share demand   {h_score}/10  (HN, 12 months: {n} stories, {big} with 100+ points)")
        print(f"Dev.to reach   {d_score}/10  (tag '{used}', median {med} reactions on top posts)")
        print(f"TOTAL {total}/10 -> {verdict}")
        print("Use these phrasings in the title, H2s and FAQ:")
        for p in phr:
            print("  -", p)
        if top:
            print("Best similar HN stories (study their angle):")
            for p, title in top:
                print(f"  {p:>5}  {title}")
