"""Build index.html (v2 design) from the site data.

Usage: python3 _build/build_home.py
Reads _build/data/*.json and writes index.html. Folders starting with "_" are not published by GitHub Pages.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "_build" / "data"
APPS = json.loads((D / "apps.json").read_text())
DETAILS = json.loads((D / "details.json").read_text())
WORK = json.loads((D / "work.json").read_text())
E = lambda s: html.escape(str(s), quote=True)
MAIL = "mailto:tabishhassan01998@gmail.com?subject=Project%20enquiry"
STORE = "sass-products-hub/"

SYS_ORDER = ["GymWren", "ClinArbor", "Passwell", "Binwright", "Keyfold", "SlateOne", "StaffCairn", "PipeCore", "Sumwright",
             "LessonMoor", "Lettrove", "ChairTime", "RouteBase", "DispatchDesk", "GatherOps", "ShelfMark", "BillPath"]
SYS_CAT = {"GymWren": "Gym & fitness", "ClinArbor": "Clinic & healthcare", "Passwell": "Restaurant POS", "Binwright": "Inventory & warehouse",
           "Keyfold": "Hotel management", "SlateOne": "School management", "StaffCairn": "HR management", "PipeCore": "CRM & sales",
           "Sumwright": "Accounting & invoicing", "LessonMoor": "E-learning / LMS", "Lettrove": "Real estate & rentals", "ChairTime": "Salon & spa",
           "RouteBase": "Fleet & logistics", "DispatchDesk": "Field service", "GatherOps": "Events & ticketing", "ShelfMark": "Library management",
           "BillPath": "Retail & wholesale billing"}

for name in SYS_ORDER:
    DETAILS[f"system:{name}"]["shot"] = WORK["systems"][name]


def demo(name):
    acts = [a for a in DETAILS[f"system:{name}"].get("actions") or [] if "demo" in a[0].lower()]
    return acts[0][1] if acts else None


services = [
    ("iOS apps", "Native SwiftUI apps with StoreKit 2 subscriptions, SwiftData and widgets, designed to pass App Review the first time.", ["SwiftUI", "StoreKit 2", "SwiftData"]),
    ("SaaS & web apps", "Multi-tenant products with sign-in, two-factor, billing, dashboards and APIs, deployed and monitored.", ["Next.js", "React", "Node.js"]),
    ("Business systems", "ERP, POS, HR, inventory and billing systems with roles, approvals, audit logs and offline-ready phone apps.", ["MongoDB", "Expo", "PWA"]),
    ("Websites & AI", "Animated marketing sites that convert, and practical AI inside your product: Claude, OpenAI and private on-device models.", ["GSAP", "Claude API", "MLX"]),
]
process = [
    ("Scope", "We turn your idea or requirements into a written spec, so we agree on what gets built before any code."),
    ("Build", "I build in small steps and share a working demo you can click through, so there are no surprises."),
    ("Launch", "Deployment, App Store submission, data migration and handover documentation."),
    ("Support", "Fixes, updates and new features after launch, as your business grows."),
]
stack = ["Swift", "SwiftUI", "StoreKit 2", "TypeScript", "React", "Next.js", "Node.js", "Express", "MongoDB", "PostgreSQL",
         "Expo / React Native", "Python", "MLX", "Claude API", "Tailwind CSS", "GSAP", "Render", "GitHub Actions"]

index_rows = [
    ("client:Manufacturing ERP + company website", "Manufacturing ERP + company website", "Client · AC-parts manufacturer, Pakistan", "Next.js · Express · MongoDB", "type:Private client system"),
    ("client:Sales & distribution management", "Sales & distribution management", "Client · distribution business, Pakistan", "React · Node.js · PWA", "type:Private client system"),
    ("client:Volunteer matchmaking platform", "Volunteer matchmaking platform", "Client · non-profit, United States", "React · Express · Render", "type:Private client system"),
    ("product:mlx-caption", "MLX Caption", "Mac app · AI subtitles in 100 languages", "Python · MLX · Whisper", "sass-products-hub/images/mlx-caption.jpg"),
    ("#systems", "17 business management systems", "Multi-tenant SaaS with live demos", "MERN · Expo", WORK["systems"]["GymWren"]),
    ("#templates", "Website templates", "18 animated Next.js sites", "Next.js · GSAP · Lenis", "assets/work/templates/aurelo.jpg"),
    ("#apps", "71 iOS apps", "Live on the App Store", "SwiftUI · StoreKit 2", "type:71 apps · 15 categories"),
]


def index_html():
    out = []
    for i, (key, title, cat, kit, peek) in enumerate(index_rows, 1):
        attrs = f'href="{E(key)}"' if key.startswith("#") else f'href="#" data-detail="{E(key)}"'
        tag = "a"
        out.append(f'<{tag} {attrs} data-peek="{E(peek)}"><span class="n mono">{i:02d}</span><span class="t">{E(title)}</span>'
                   f'<span class="c">{E(cat)}</span><span class="k mono">{E(kit)}</span><span class="go" aria-hidden="true">↗</span></{tag}>')
    return "\n".join(out)


def systems_html():
    out = []
    for name in SYS_ORDER:
        d = DETAILS[f"system:{name}"]
        link = demo(name)
        out.append(f'''<article class="sys"><div class="shot"><img src="{E(WORK["systems"][name])}" alt="{E(name)} dashboard" loading="lazy"></div>
<div class="body"><span class="cat mono">{E(SYS_CAT[name])}</span><h3>{E(name)}</h3><p>{E(d["subtitle"])}</p>
<div class="acts"><button type="button" data-detail="system:{E(name)}">Details &amp; demo logins</button>{f'<a href="{E(link)}" target="_blank" rel="noopener">Live demo ↗</a>' if link else ""}{f'<a class="buy" href="{E(d["buy"])}" target="_blank" rel="noopener">Buy · $99 ↗</a>' if d.get("buy") else ""}</div></div></article>''')
    return "\n".join(out)


def templates_html():
    t = WORK["templates"]
    out = [f'''<a class="tpl featured" href="{E(WORK["aurelo"]["url"])}" target="_blank" rel="noopener"><div class="img"><img src="assets/work/templates/aurelo.jpg" alt="Aurelo AI SaaS landing page" loading="lazy"><span class="badge">NEW · PREMIUM</span></div>
<div class="row"><h3>Aurelo — AI SaaS landing page with a live agent console</h3><span class="price">$49</span></div></a>''']
    for x in t:
        name = E(x["name"].replace(" (Next.js)", ""))
        img = f'<img src="{E(x["img"])}" alt="{E(x["name"])}" loading="lazy">'
        row = f'<div class="row"><h3>{name}</h3><span class="price">${E(x["price"])}</span></div>'
        if x.get("demo"):   # built by _build/build_template_demos.sh
            out.append(f'''<article class="tpl"><a class="img" href="{E(x["demo"])}" target="_blank" rel="noopener" aria-label="Open the live demo: {name}">{img}</a>
{row}
<div class="tpl-acts"><a href="{E(x["demo"])}" target="_blank" rel="noopener">Live demo ↗</a><a href="{E(x["url"])}" target="_blank" rel="noopener">Buy on Gumroad ↗</a></div></article>''')
        else:
            out.append(f'''<a class="tpl" href="{E(x["url"])}" target="_blank" rel="noopener"><div class="img">{img}</div>
{row}</a>''')
    return "\n".join(out)


def products_html():
    keys = ["product:mlx-caption", "product:shipkit-for-ios", "product:plinth", "product:ai-automation-templates"]
    out = []
    for k in keys:
        d = DETAILS[k]
        img = d.get("image") or ""
        out.append(f'''<a href="#" data-detail="{E(k)}"><img src="{E(img)}" alt="" loading="lazy"><div><p class="mono muted">{E(dict(d["facts"]).get("Price", ""))}</p><h3>{E(d["title"].split(" — ")[0].split(":")[0])}</h3><p>{E(d["subtitle"])}</p></div></a>''')
    return "\n".join(out)


page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tabish Hassan — iOS apps, SaaS, business systems and websites</title>
<meta name="description" content="Independent developer in Pakistan: 71 iOS apps on the App Store, 17 business management systems with live demos, client systems in production, and animated website templates. Available for new projects.">
<meta name="theme-color" content="#f5f4ef">
<meta property="og:title" content="Tabish Hassan — iOS apps, SaaS, business systems and websites">
<meta property="og:description" content="71 iOS apps on the App Store, 17 business systems with live demos, and production systems for clients. Available for new projects.">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/work/templates/aurelo.jpg">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/th.css">
</head>
<body>
<header class="nav"><div class="bar">
  <a class="logo" href="#top" aria-label="Tabish Hassan, home"><span class="mark">TH</span>Tabish Hassan</a>
  <ul>
    <li><a href="#work">Work</a></li><li><a href="#systems">Systems</a></li><li><a href="#templates">Templates</a></li>
    <li><a href="#apps">Apps</a></li><li><a href="{STORE}">Store</a></li><li><a href="#contact">Contact</a></li>
  </ul>
  <div class="right"><span class="avail"><span class="dot"></span>Available for projects</span>
  <a class="btn primary hire" href="{MAIL}">Hire me <span class="arr">↗</span></a>
  <button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false"><span></span><span></span></button></div>
</div></header>
<nav class="mobile-menu" aria-label="Mobile">
  <a href="#work">Work</a><a href="#systems">Systems</a><a href="#templates">Templates</a><a href="#apps">Apps</a><a href="{STORE}">Store</a><a href="#contact">Contact</a>
  <a class="btn primary" href="{MAIL}">Hire me ↗</a>
</nav>

<main id="top">
<section class="hero"><div class="wrap">
  <div class="meta mono reveal"><span>Independent developer</span><span>Rawalpindi, Pakistan</span><span>Working worldwide, remote</span></div>
  <h1 class="name" aria-label="Tabish Hassan">
    <span class="row"><span class="w">Tabish</span>
      <span class="role reveal" data-d=".6">designs and builds<br><span class="rot"><span>iOS apps</span><span>SaaS platforms</span><span>business systems</span><span>websites that move</span></span></span></span>
    <span class="row"><span class="w">Hassan</span></span>
  </h1>
  <div class="lower">
    <p class="sub reveal" data-d=".4">I work on the whole thing: product decisions, design, code, deployment, and the boring parts that make software trustworthy, like roles, audit trails, backups and tests.</p>
    <div class="cta reveal" data-d=".5"><a class="btn primary" href="{MAIL}">Start a project <span class="arr">↗</span></a><a class="btn" href="#work">See the work</a></div>
  </div>
  <div class="ledger">
    <div><b data-count="71">71</b><span>iOS apps live on the App Store</span></div>
    <div><b data-count="17">17</b><span>business systems with live demos</span></div>
    <div><b data-count="18">18</b><span>animated website templates</span></div>
    <div><b data-count="3">3</b><span>client systems in production</span></div>
  </div>
</div>
<div class="river" aria-label="Some of my App Store apps"><div class="lane"></div><div class="lane rev"></div></div>
</section>

<section class="block" id="work"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">Selected work</p><h2 class="title" data-split>Software running <em>real businesses.</em></h2></div>
  <p class="lead reveal">Client systems built requirement by requirement and tested end to end before handover, plus the products and platforms I ship on my own.</p></div>
  <div class="index">
{index_html()}
  </div>
</div></section>

<section class="block" id="services" style="padding-top:40px"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">What I build</p><h2 class="title" data-split>From idea to the App Store, <em>or to your team's daily workflow.</em></h2></div>
  <p class="lead reveal">One person from first sketch to production, so nothing gets lost between a designer, a developer and an ops team.</p></div>
  <div class="services">
{"".join(f'<div class="svc"><div class="num">{i:02d}</div><h3>{E(t)}</h3><p>{E(p)}</p><div class="tags">{"".join(f"<span>{E(x)}</span>" for x in tags)}</div></div>' for i, (t, p, tags) in enumerate(services, 1))}
  </div>
  <div class="process">
{"".join(f'<div class="step"><b>0{i} · {E(t)}</b><h4>{E(t)}</h4><p>{E(p)}</p></div>' for i, (t, p) in enumerate(process, 1))}
  </div>
</div></section>

<section class="block dark" id="systems"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">Business management systems</p><h2 class="title" data-split>17 complete platforms, <em>each with a live demo.</em></h2></div>
  <p class="lead reveal">Multi-tenant SaaS with sign-in, two-factor, roles, billing plans and audit logs. Many come with phone apps for staff or customers. Open any one and click around with the demo logins. Each is sold as full source code for $99, paid once.</p></div>
</div>
<div class="sys-wrap"><div class="sys-track">
{systems_html()}
</div></div>
<div class="wrap"><p class="sys-note">Demos run on free hosting, so the first visit can take up to a minute to wake up. All demo data is made up.</p></div>
</section>

<section class="block" id="templates"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">Website templates</p><h2 class="title" data-split>Sites that move, <em>ready to make yours.</em></h2></div>
  <p class="lead reveal">Next.js templates with cinematic photo motion, built for real businesses: cafes, clinics, schools, gyms, restaurants and more. Every one is editable from a single content file, and every one has a live demo you can open.</p></div>
  <div class="tpl-grid">
{templates_html()}
  </div>
</div></section>

<section class="block" id="apps" style="padding-top:40px"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">On the App Store</p><h2 class="title" data-split>71 iOS apps, <em>shipped in six months.</em></h2></div>
  <p class="lead reveal">Native SwiftUI apps across 15 categories, from finance and health to education and sport. Tap any app to open it on the App Store.</p></div>
  <div class="chips" id="chips"></div>
  <div class="apps" id="app-grid"></div>
  <div class="apps-more"><button class="btn" id="more" type="button">Show all 71 apps</button><a class="btn" href="https://apps.apple.com/us/developer/tabish-hassan/id1885918100" target="_blank" rel="noopener">View on the App Store <span class="arr">↗</span></a></div>
</div></section>

<section class="block" id="products" style="padding-top:40px"><div class="wrap">
  <div class="head"><div><p class="eyebrow mono">Products</p><h2 class="title" data-split>Tools I build <em>and sell.</em></h2></div>
  <p class="lead reveal">The kits and apps that came out of shipping everything above. <a href="{STORE}" style="text-decoration:underline">See all in the Sass Products Hub store →</a></p></div>
  <div class="prod">
{products_html()}
  </div>
</div></section>

<div class="stack" aria-label="Tools I use"><div class="lane">{"".join(f"<span>{E(s)}</span>" for s in stack * 2)}</div></div>
</main>

<section class="contact" id="contact"><div class="wrap">
  <p class="mono" style="color:var(--lime)">Let's talk</p>
  <h2 class="big">Have a project<br>in <em>mind?</em></h2>
  <div class="row">
    <p>Tell me what you want to build. I reply within two business days with questions, a plan and a quote.</p>
    <div><div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn primary" href="{MAIL}">Email me <span class="arr">↗</span></a><a class="btn" href="https://apps.apple.com/us/developer/tabish-hassan/id1885918100" target="_blank" rel="noopener">My App Store page <span class="arr">↗</span></a></div>
    <a class="mail" href="{MAIL}">tabishhassan01998@gmail.com</a></div>
  </div>
  <footer>
    <span>© <span id="year">2026</span> Tabish Hassan</span>
    <nav aria-label="Footer"><a href="{STORE}">Sass Products Hub</a><a href="privacy-policy.html">App privacy</a><a href="terms-of-service.html">App terms</a><a href="support.html">App support</a></nav>
  </footer>
</div></section>

<div class="peek" aria-hidden="true"></div>
<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="m-title" aria-hidden="true"><div class="box"><button class="x" type="button" aria-label="Close">×</button><div id="m-body"></div></div></div>

<script>window.APPS = {json.dumps(APPS, ensure_ascii=False)};</script>
<script>window.DETAILS = {json.dumps(DETAILS, ensure_ascii=False)};</script>
<script src="assets/vendor/gsap.min.js" defer></script>
<script src="assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="assets/vendor/SplitText.min.js" defer></script>
<script src="assets/vendor/lenis.min.js" defer></script>
<script src="assets/th.js" defer></script>
</body>
</html>
'''
(ROOT / "index.html").write_text(page)
print("wrote index.html", len(page) // 1024, "KB")
