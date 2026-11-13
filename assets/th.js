/* tabishapps.com — v2 interactions. Data comes from window.APPS and window.DETAILS in index.html. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  /* nav */
  const nav = $(".nav");
  const onScroll = () => nav.classList.toggle("scrolled", scrollY > 30);
  onScroll();
  addEventListener("scroll", onScroll, { passive: true });
  const menu = $(".mobile-menu");
  $(".menu-btn")?.addEventListener("click", (e) => {
    const open = menu.classList.toggle("open");
    e.currentTarget.setAttribute("aria-expanded", open);
  });
  $$(".mobile-menu a").forEach((a) => a.addEventListener("click", () => menu.classList.remove("open")));
  $("#year").textContent = new Date().getFullYear();

  /* rotating role words */
  const rot = $(".rot");
  if (rot) {
    const words = $$("span", rot);
    let i = 0;
    words.forEach((w, k) => (w.style.transform = `translateY(${k ? 110 : 0}%)`));
    if (!reduce)
      setInterval(() => {
        const cur = words[i];
        i = (i + 1) % words.length;
        cur.style.transform = "translateY(-110%)";
        words[i].style.transition = "none";
        words[i].style.transform = "translateY(110%)";
        requestAnimationFrame(() => requestAnimationFrame(() => {
          words[i].style.transition = "";
          words[i].style.transform = "translateY(0)";
        }));
      }, 2200);
  }

  /* apps: river, chips and grid */
  const APPS = window.APPS || [];
  const lanes = $$(".river .lane");
  if (lanes.length) {
    const half = Math.ceil(APPS.length / 2);
    [APPS.slice(0, half), APPS.slice(half)].forEach((list, k) => {
      const html = list.map((a) => `<a href="${esc(a.url)}" target="_blank" rel="noopener" title="${esc(a.name)}"><img src="${esc(a.icon)}" alt="${esc(a.name)}" loading="lazy" width="76" height="76"></a>`).join("");
      lanes[k].innerHTML = html + html.replace(/alt="[^"]*"/g, 'alt="" aria-hidden="true"').replace(/<a /g, '<a tabindex="-1" aria-hidden="true" ');
    });
  }
  const grid = $("#app-grid");
  const chips = $("#chips");
  if (grid) {
    grid.innerHTML = APPS.map((a) => `<a class="app" href="${esc(a.url)}" target="_blank" rel="noopener" data-cat="${esc(a.cat)}"><img src="${esc(a.icon)}" alt="" loading="lazy" width="84" height="84"><b>${esc(a.name)}</b><span>${esc(a.cat)}</span></a>`).join("");
    const counts = APPS.reduce((m, a) => ((m[a.cat] = (m[a.cat] || 0) + 1), m), {});
    const cats = ["All", ...Object.keys(counts).sort((a, b) => counts[b] - counts[a])];
    chips.innerHTML = cats.map((c) => `<button type="button" aria-pressed="${c === "All"}" data-cat="${esc(c)}">${esc(c)}<span>${c === "All" ? APPS.length : counts[c]}</span></button>`).join("");
    let cat = "All";
    let all = false;
    const LIMIT = 24;
    const render = () => {
      let n = 0;
      $$(".app", grid).forEach((el) => {
        const match = cat === "All" || el.dataset.cat === cat;
        const show = match && (all || cat !== "All" || n < LIMIT);
        if (match) n++;
        el.classList.toggle("hide", !show);
      });
      $("#more").hidden = cat !== "All" || all;
    };
    chips.addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      cat = b.dataset.cat;
      $$("button", chips).forEach((x) => x.setAttribute("aria-pressed", x === b));
      render();
      window.ScrollTrigger?.refresh();
    });
    $("#more").addEventListener("click", () => { all = true; render(); window.ScrollTrigger?.refresh(); });
    render();
  }

  /* detail modal */
  const D = window.DETAILS || {};
  const modal = $("#modal");
  const body = $("#m-body");
  let last = null;
  const openModal = (key) => {
    const d = D[key];
    if (!d) return;
    last = document.activeElement;
    body.innerHTML = `
      <p class="mono muted">${esc(d.type === "system" ? "Business management system" : d.type === "client" ? "Client work" : "Product")}</p>
      <h3 id="m-title">${esc(d.title)}</h3>
      <p class="subtitle">${esc(d.subtitle || "")}</p>
      ${d.shot ? `<img class="shot" src="${esc(d.shot)}" alt="">` : ""}
      ${d.html || ""}
      ${d.features?.length ? `<ul>${d.features.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>` : ""}
      ${d.facts?.length ? `<dl>${d.facts.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>` : ""}
      ${d.accounts?.length ? `<p class="mono muted">Demo logins</p><dl>${d.accounts.map((a) => `<dt>${esc(a.role || "")}</dt><dd>${esc(a.user)} · ${esc(a.password)}</dd>`).join("")}</dl>` : ""}
      ${d.note ? `<p class="note">${esc(d.note)}</p>` : ""}
      ${d.actions?.length ? `<div class="acts">${d.actions.map(([t, u, k]) => `<a class="btn ${k === "primary" ? "primary" : ""}" href="${esc(u)}" ${/^http/.test(u) ? 'target="_blank" rel="noopener"' : ""}>${esc(t.replace(/\s*↗$/, ""))} <span class="arr">↗</span></a>`).join("")}</div>` : ""}`;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.documentElement.style.overflow = "hidden";
    window.__lenis?.stop();
    $(".x", modal).focus();
  };
  const closeModal = () => {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.documentElement.style.overflow = "";
    window.__lenis?.start();
    last?.focus();
  };
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-detail]");
    if (t) { e.preventDefault(); openModal(t.dataset.detail); }
  });
  $(".x", modal).addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
  addEventListener("keydown", (e) => { if (e.key === "Escape" && modal.classList.contains("open")) closeModal(); });

  /* work index hover preview (desktop pointers only) */
  const peek = $(".peek");
  if (peek && matchMedia("(hover: hover) and (pointer: fine)").matches) {
    let x = 0, y = 0, px = 0, py = 0;
    addEventListener("mousemove", (e) => { x = e.clientX; y = e.clientY; });
    const loop = () => {
      px += (x - px) * 0.18; py += (y - py) * 0.18;
      peek.style.left = px + 24 + "px"; peek.style.top = py + "px";
      requestAnimationFrame(loop);
    };
    loop();
    $$(".index [data-peek]").forEach((row) => {
      row.addEventListener("mouseenter", () => {
        const v = row.dataset.peek;
        peek.innerHTML = v.startsWith("type:") ? `<div class="type">${esc(v.slice(5))}</div>` : `<img src="${esc(v)}" alt="">`;
        peek.classList.add("on");
      });
      row.addEventListener("mouseleave", () => peek.classList.remove("on"));
    });
  }

  /* motion */
  if (reduce || !window.gsap) return;
  gsap.registerPlugin(ScrollTrigger, SplitText);
  const lenis = new Lenis({ duration: 1.1 });
  window.__lenis = lenis;
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((t) => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
  $$('a[href^="#"]').forEach((a) => a.addEventListener("click", (e) => {
    const id = a.getAttribute("href");
    if (id.length < 2) return;
    const el = $(id);
    if (!el) return;
    e.preventDefault();
    lenis.scrollTo(el, { offset: -70 });
  }));

  document.fonts.ready.then(() => {
    // the name rises letter by letter
    $$(".name .w").forEach((w, i) => {
      const s = SplitText.create(w, { type: "chars", mask: "chars" });
      gsap.from(s.chars, { yPercent: 110, duration: 1.2, ease: "expo.out", stagger: 0.035, delay: 0.15 + i * 0.12 });
    });
    $$("[data-split]").forEach((el) => {
      const s = SplitText.create(el, { type: "lines", mask: "lines" });
      gsap.from(s.lines, { yPercent: 105, duration: 1, ease: "expo.out", stagger: 0.08, scrollTrigger: { trigger: el, start: "top 85%" } });
    });
  });

  $$(".reveal").forEach((el) => gsap.from(el, { y: 30, autoAlpha: 0, duration: 0.9, ease: "power3.out", delay: Number(el.dataset.d || 0), scrollTrigger: { trigger: el, start: "top 90%" } }));

  $$("[data-count]").forEach((el) => {
    const end = Number(el.dataset.count);
    const o = { v: 0 };
    gsap.to(o, { v: end, duration: 1.8, ease: "power2.out", scrollTrigger: { trigger: el, start: "top 92%" }, onUpdate: () => (el.textContent = Math.round(o.v)) });
  });

  // systems: pinned horizontal gallery on wide screens
  const mm = gsap.matchMedia();
  mm.add("(min-width: 900px)", () => {
    const track = $(".sys-track");
    const wrap = $(".sys-wrap");
    if (!track) return;
    const dist = () => track.scrollWidth - innerWidth;
    gsap.to(track, {
      x: () => -dist(),
      ease: "none",
      scrollTrigger: { trigger: "#systems", start: "top top", end: () => "+=" + dist(), pin: "#systems", scrub: 0.6, invalidateOnRefresh: true, anticipatePin: 1 },
    });
  });

  // templates and products lift in a stagger
  ScrollTrigger.batch(".tpl, .prod a, .step, .svc", {
    start: "top 92%",
    onEnter: (els) => gsap.from(els, { y: 40, autoAlpha: 0, duration: 0.9, ease: "power3.out", stagger: 0.07 }),
  });
})();
