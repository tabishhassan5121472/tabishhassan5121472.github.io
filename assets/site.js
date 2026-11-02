// tabishapps.com — small, dependency-free interactions.
(function () {
  document.documentElement.classList.add('js');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Sticky nav gets a background once you scroll.
  const nav = document.querySelector('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', window.scrollY > 10);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Reveal elements as they enter the viewport.
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      if (e.target.dataset.count) countUp(e.target);
      io.unobserve(e.target);
    });
  }, { threshold: 0.15 }) : null;
  const watch = (el) => (io ? io.observe(el) : show(el));
  const show = (el) => {
    if (el.classList.contains('in')) return;
    el.classList.add('in');
    if (el.dataset.count) countUp(el);
    if (io) io.unobserve(el);
  };
  const targets = document.querySelectorAll('.reveal, [data-count]');
  targets.forEach(watch);
  // Safety net: reveal anything already on screen, and everything if the
  // observer never reports (old browsers, unusual environments).
  const inView = () => targets.forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight && r.bottom > 0) show(el);
  });
  requestAnimationFrame(inView);
  window.addEventListener('scroll', inView, { passive: true });
  setTimeout(() => targets.forEach(show), 4000);

  // Count-up numbers.
  function countUp(el) {
    const end = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';
    if (reduce) { el.textContent = end + suffix; return; }
    const t0 = performance.now(), dur = 1400;
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / dur);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // Typing word rotator in the hero.
  const rot = document.querySelector('[data-words]');
  if (rot) {
    const words = rot.dataset.words.split('|');
    const text = rot.querySelector('.word');
    if (reduce) { text.textContent = words[0]; }
    else {
      let w = 0, i = 0, del = false;
      const step = () => {
        const word = words[w];
        i += del ? -1 : 1;
        text.textContent = word.slice(0, i);
        let wait = del ? 40 : 75;
        if (!del && i === word.length) { del = true; wait = 1800; }
        else if (del && i === 0) { del = false; w = (w + 1) % words.length; wait = 300; }
        setTimeout(step, wait);
      };
      step();
    }
  }

  // Spotlight that follows the mouse on cards, plus a soft page glow.
  document.addEventListener('pointermove', (e) => {
    const card = e.target.closest && e.target.closest('.card');
    if (card) {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', e.clientX - r.left + 'px');
      card.style.setProperty('--my', e.clientY - r.top + 'px');
    }
  }, { passive: true });
  const glow = document.querySelector('.cursor-glow');
  if (glow && !reduce && window.matchMedia('(pointer: fine)').matches) {
    document.addEventListener('pointermove', (e) => {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px';
    }, { passive: true });
  }

  // Gentle 3D tilt on elements marked .tilt (desktop only).
  if (!reduce && window.matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('.tilt').forEach((el) => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateX(${(-y * 5).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg) translateY(-3px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  // App Store grid with category filters (home page only).
  const grid = document.getElementById('apps');
  if (grid && window.APPS) {
    const chips = document.getElementById('chips');
    const moreBtn = document.getElementById('more');
    const cats = {};
    window.APPS.forEach((a) => { cats[a.cat] = (cats[a.cat] || 0) + 1; });
    const order = ['All', ...Object.keys(cats).sort((a, b) => cats[b] - cats[a])];
    let current = 'All', showAll = false;
    chips.innerHTML = order.map((c) =>
      `<button class="chip${c === 'All' ? ' on' : ''}" data-cat="${c}">${c}<small>${c === 'All' ? window.APPS.length : cats[c]}</small></button>`).join('');
    const render = () => {
      const list = window.APPS.filter((a) => current === 'All' || a.cat === current);
      const shown = showAll || current !== 'All' ? list : list.slice(0, 24);
      grid.innerHTML = shown.map((a, i) =>
        `<button class="app" data-app="${a.id}" style="animation-delay:${Math.min(i, 24) * 25}ms" title="${esc(a.full)}" aria-haspopup="dialog">
           <img src="${a.icon}" alt="" loading="lazy" width="72" height="72"><b>${esc(a.name)}</b><span>${esc(a.cat)}</span></button>`).join('');
      moreBtn.style.display = current === 'All' && !showAll && list.length > 24 ? '' : 'none';
    };
    chips.addEventListener('click', (e) => {
      const b = e.target.closest('.chip'); if (!b) return;
      current = b.dataset.cat;
      chips.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === b));
      render();
    });
    moreBtn.addEventListener('click', () => { showAll = true; render(); });
    render();
  }


  // ---------- helpers ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  const ROOT = window.ROOT || '';
  const url = (u) => (!u || /^(https?:|mailto:|#|\/)/.test(u) ? u : ROOT + u);

  // ---------- detail panel ----------
  const modal = document.getElementById('modal');
  const body = document.getElementById('m-body');
  let lastFocus = null;

  function factsHtml(f) {
    return f && f.length ? '<dl class="facts">' + f.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('') + '</dl>' : '';
  }
  function actionsHtml(a) {
    return a && a.length ? '<div class="m-actions">' + a.map(([label, href, kind]) =>
      `<a class="btn ${kind || ''}" href="${esc(url(href))}"${/^https?:/.test(href) ? ' target="_blank" rel="noopener"' : ''}>${esc(label)}</a>`).join('') + '</div>' : '';
  }
  function renderDetail(d) {
    let h = '';
    if (d.type === 'product') {
      const media = d.video
        ? `<video class="m-hero" src="${esc(url(d.video))}" poster="${esc(url(d.image))}" controls playsinline preload="none"></video>`
        : `<img class="m-hero" src="${esc(url(d.image))}" alt="">`;
      h += media;
    }
    h += `<div class="m-content"><p class="eyebrow">${esc({ product: 'Product', system: 'Business system', client: 'Client project', app: 'iOS app' }[d.type] || '')}</p>`;
    h += `<h2 id="m-title" class="m-title">${esc(d.title)}</h2>`;
    if (d.subtitle) h += `<p class="m-sub">${esc(d.subtitle)}</p>`;
    h += actionsHtml(d.actions);
    h += factsHtml(d.facts);
    if (d.html) h += `<div class="m-text">${d.html}</div>`;
    if (d.features && d.features.length) h += '<h3 class="m-h">Key features</h3><ul class="list two">' + d.features.map((f) => `<li>${esc(f)}</li>`).join('') + '</ul>';
    if (d.accounts && d.accounts.length) {
      h += '<h3 class="m-h">Try the demo</h3><p class="muted small">Shared demo logins with made-up data. Please don\'t enter real information.</p><div class="logins">' +
        d.accounts.map((a) => `<div class="login"><span class="role">${esc(a.role)}</span><code>${esc(a.user)}</code><code>${esc(a.password)}</code></div>`).join('') + '</div>';
    }
    if (d.gallery && d.gallery.length) h += '<h3 class="m-h">Gallery</h3><div class="gallery">' + d.gallery.map((g) => `<img src="${esc(url(g))}" alt="" loading="lazy">`).join('') + '</div>';
    if (d.shots && d.shots.length) h += '<h3 class="m-h">Screenshots</h3><div class="shots">' + d.shots.map((g) => `<img src="${esc(g)}" alt="" loading="lazy">`).join('') + '</div>';
    if (d.note) h += `<p class="note">${esc(d.note)}</p>`;
    h += '</div>';
    return h;
  }
  function appDetail(a) {
    return {
      type: 'app', title: a.full, subtitle: a.cat + (a.price ? ' · ' + a.price : '') + (a.min_os ? ' · iOS ' + a.min_os + '+' : ''),
      html: a.desc ? '<p>' + esc(a.desc).replace(/\n+/g, '</p><p>') + '</p>' : '', shots: a.shots,
      actions: [['View on the App Store ↗', a.url, 'primary']], icon: a.icon,
    };
  }
  function openDetail(key, push) {
    let d = null;
    if (key.startsWith('app:') && window.APPS) {
      const a = window.APPS.find((x) => String(x.id) === key.slice(4));
      if (a) d = appDetail(a);
    } else if (window.DETAILS) d = window.DETAILS[key];
    if (!d || !modal) return;
    body.innerHTML = renderDetail(d);
    if (d.icon) body.querySelector('.m-content').insertAdjacentHTML('afterbegin', `<img class="m-icon" src="${esc(url(d.icon))}" alt="">`);
    lastFocus = document.activeElement;
    modal.hidden = false;
    requestAnimationFrame(() => modal.classList.add('open'));
    document.documentElement.classList.add('modal-open');
    modal.querySelector('.modal-panel').scrollTop = 0;
    modal.querySelector('.modal-panel').focus();
    if (push !== false) history.replaceState(null, '', '#' + encodeURIComponent(key));
  }
  function closeDetail() {
    if (!modal || modal.hidden) return;
    modal.classList.remove('open');
    document.documentElement.classList.remove('modal-open');
    const v = modal.querySelector('video'); if (v) v.pause();
    setTimeout(() => { modal.hidden = true; body.innerHTML = ''; }, reduce ? 0 : 280);
    history.replaceState(null, '', location.pathname + location.search);
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-close]')) { closeDetail(); return; }
    if (e.target.closest('a, video') && !e.target.closest('[data-detail] .more-link')) return; // real links keep working
    const app = e.target.closest('[data-app]');
    if (app) { openDetail('app:' + app.dataset.app); return; }
    const card = e.target.closest('[data-detail]');
    if (card) openDetail(card.dataset.detail);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDetail();
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[data-detail]')) { e.preventDefault(); openDetail(e.target.dataset.detail); }
    if (e.key === 'Tab' && modal && !modal.hidden) {   // keep focus inside the panel
      const f = modal.querySelectorAll('a, button, video, [tabindex="0"]');
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  if (location.hash.length > 1) {
    const key = decodeURIComponent(location.hash.slice(1));
    if (key.includes(':')) setTimeout(() => openDetail(key, false), 300);
  }

  // ---------- extra motion ----------
  // Scroll progress bar.
  const bar = document.querySelector('.progress');
  const onProgress = () => {
    if (!bar) return;
    const h = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${h > 0 ? Math.min(1, scrollY / h) : 0})`;
  };
  onProgress(); window.addEventListener('scroll', onProgress, { passive: true });

  // Hero headline: words rise in one after another.
  document.querySelectorAll('.split .w').forEach((w, i) => { w.style.animationDelay = (0.1 + i * 0.08) + 's'; });

  if (!reduce) {
    // Background blobs drift with the scroll for depth.
    const blobs = document.querySelectorAll('.bg .blob');
    window.addEventListener('scroll', () => {
      const y = scrollY;
      blobs.forEach((b, i) => { b.style.translate = `0 ${(-y * (0.04 + i * 0.03)).toFixed(1)}px`; });
    }, { passive: true });

    // Magnetic buttons pull gently towards the pointer.
    if (window.matchMedia('(pointer: fine)').matches) {
      document.querySelectorAll('.btn.primary, .cta .btn').forEach((b) => {
        b.addEventListener('pointermove', (e) => {
          const r = b.getBoundingClientRect();
          b.style.translate = `${((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1)}px ${((e.clientY - r.top - r.height / 2) * 0.25).toFixed(1)}px`;
        });
        b.addEventListener('pointerleave', () => { b.style.translate = ''; });
      });
    }
  }

  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
