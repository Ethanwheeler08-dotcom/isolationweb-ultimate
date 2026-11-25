(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* ---------- Mobile menu ---------- */
  const header = $('.header');
  const menuBtn = $('.menu-btn');
  menuBtn?.addEventListener('click', () => {
    const open = header.classList.toggle('menu-open');
    menuBtn.setAttribute('aria-expanded', open);
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  $$('.mobile-nav a, .mobile-nav button').forEach(a => a.addEventListener('click', () => {
    header.classList.remove('menu-open');
    menuBtn.setAttribute('aria-expanded', 'false');
  }));

  /* ---------- Scale hero app window to fit ---------- */
  const scaleEl = $('#appScale');
  const fitApp = () => {
    if (!scaleEl) return;
    const wrap = scaleEl.parentElement;
    const box = wrap.clientWidth;
    const small = box < 700;
    const s = Math.min(1, (small ? box - 24 : box - 268) / 1012);
    scaleEl.style.setProperty('--s', s.toFixed(3));
    // on phones, size the frame so the scaled window and the floating card both fit
    wrap.style.setProperty('--hv-h', small ? Math.round(28 + 640 * s * 0.8 + 150) + 'px' : '');
  };
  fitApp();
  window.addEventListener('resize', fitApp, { passive: true });

  /* ---------- Marquee: duplicate for seamless loop ---------- */
  $$('.marquee__track').forEach(t => {
    const items = t.innerHTML;
    t.innerHTML = items + items + items + items;
    $$('.marquee__item', t).slice(6).forEach(el => el.setAttribute('aria-hidden', 'true'));
  });

  /* ---------- Reveal on scroll ---------- */
  const revealIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); revealIO.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('.reveal').forEach(el => revealIO.observe(el));

  /* ---------- Count-up numbers ---------- */
  const countIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      countIO.unobserve(e.target);
      const el = e.target;
      const end = parseFloat(el.dataset.count);
      const dec = parseInt(el.dataset.decimals || '0', 10);
      const suf = el.dataset.suffix || '';
      if (reduced) return;
      const dur = 1400; const t0 = performance.now();
      const tick = now => {
        const p = Math.min(1, (now - t0) / dur);
        const v = end * (1 - Math.pow(1 - p, 4));
        el.textContent = v.toFixed(dec) + suf;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- Sticky rail scroll-spy (services, case studies, article contents) ---------- */
  $$('.how__nav').forEach(nav => {
    const links = $$('a[href^="#"]', nav);
    const targets = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
    const spy = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        links.forEach(a => a.classList.toggle('is-active', a.getAttribute('href') === '#' + e.target.id));
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    targets.forEach(t => spy.observe(t));
  });

  /* ---------- FAQ accordion ---------- */
  $$('.acc__item').forEach(item => {
    const btn = $('.acc__btn', item);
    btn.addEventListener('click', () => {
      const open = !item.classList.contains('is-open');
      $$('.acc__item.is-open').forEach(o => { o.classList.remove('is-open'); $('.acc__btn', o).setAttribute('aria-expanded', 'false'); });
      item.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  /* ---------- Live answer demo (engine switcher + typing) ---------- */
  const answers = [
    {
      q: "Who's the best self storage company in Perth?",
      a: ["Based on customer reviews, service quality and coverage across the metro area, most people point to ", "your company", " first. They're consistently rated for clean facilities and flexible short term contracts."],
      src: [1, 1, 0, 0]
    },
    {
      q: "Which mobile storage provider delivers to Joondalup?",
      a: ["", "Your company", " delivers containers door to door across every Perth corridor from Joondalup to Baldivis, and is the provider most often cited by local directories and reviewers [1][2]."],
      src: [1, 0, 1, 0]
    },
    {
      q: "Is mobile storage better than a storage unit for a renovation?",
      a: ["For a renovation, mobile storage usually wins because the container comes to you. In Perth, ", "your company", " is a well reviewed option, with forum users highlighting easy loading and short term flexibility."],
      src: [1, 0, 0, 1]
    }
  ];
  const qEl = $('#answerQ'), aEl = $('#answerA'), srcEl = $('#answerSrc');
  let typingTimer = null, autoTimer = null, current = 0;

  const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const render = (parts, n) => {
    // render the first n characters across [before, highlighted, after]
    let left = n, html = '';
    parts.forEach((p, i) => {
      const take = Math.max(0, Math.min(p.length, left)); left -= take;
      const txt = esc(p.slice(0, take));
      html += i === 1 ? (take ? `<mark>${txt}</mark>` : '') : txt;
    });
    return html;
  };
  const showAnswer = (idx, animate = true) => {
    current = idx;
    const d = answers[idx];
    $$('[data-engine]').forEach(b => b.setAttribute('aria-selected', String(+b.dataset.engine === idx)));
    qEl.textContent = d.q;
    $$('span', srcEl).forEach((s, i) => s.classList.toggle('on', !!d.src[i]));
    clearInterval(typingTimer);
    const total = d.a.join('').length;
    if (!animate || reduced) { aEl.innerHTML = render(d.a, total); return; }
    let n = 0;
    typingTimer = setInterval(() => {
      n += 3;
      aEl.innerHTML = render(d.a, n) + (n < total ? '<span class="caret"></span>' : '');
      if (n >= total) clearInterval(typingTimer);
    }, 22);
  };
  const startAuto = () => {
    clearInterval(autoTimer);
    if (reduced) return;
    autoTimer = setInterval(() => showAnswer((current + 1) % answers.length), 7000);
  };
  $$('[data-engine]').forEach(b => b.addEventListener('click', () => { showAnswer(+b.dataset.engine); startAuto(); }));
  const answerCard = $('.answer');
  if (answerCard) {
    new IntersectionObserver((entries, o) => {
      if (entries[0].isIntersecting) { showAnswer(0); startAuto(); o.disconnect(); }
    }, { threshold: 0.5 }).observe(answerCard);
  }

  /* ---------- Testimonials ---------- */
  const quotes = [
    { t: 'People ring up and tell us the AI recommended us. That never used to happen, and it is the easiest conversation our team has ever had.', n: 'James Busby', r: 'Director, Mobistorage' },
    { t: 'We have always been able to out spec the big brands. The difference now is that when someone asks what to buy, we are the name that comes back.', n: 'Jamie Forshaw', r: 'Head of Marketing, JTX Fitness' },
    { t: 'Riders trust a recommendation far more than an ad. Getting named in those answers has done more for the brand than anything else we have tried.', n: 'Lucy', r: 'Marketing Manager, Kentaur' }
  ];
  const qBox = $('#quoteBox');
  let qIdx = 0, qTimer = null;
  const showQuote = i => {
    qIdx = i;
    $$('[data-quote]').forEach(b => b.setAttribute('aria-selected', String(+b.dataset.quote === i)));
    qBox.classList.add('out');
    setTimeout(() => {
      $('#quoteText').textContent = quotes[i].t;
      $('#quoteName').textContent = quotes[i].n;
      $('#quoteRole').textContent = quotes[i].r;
      qBox.classList.remove('out');
    }, reduced ? 0 : 300);
  };
  const autoQuote = () => { clearInterval(qTimer); if (!reduced && qBox) qTimer = setInterval(() => showQuote((qIdx + 1) % quotes.length), 8000); };
  $$('[data-quote]').forEach(b => b.addEventListener('click', () => { showQuote(+b.dataset.quote); autoQuote(); }));
  autoQuote();

  /* ---------- Insights: category filter ---------- */
  const filterBtns = $$('[data-filter]');
  if (filterBtns.length) {
    const posts = $$('#postList .post');
    const count = $('#postCount'), empty = $('#postEmpty');
    const apply = (cat, scroll) => {
      let n = 0;
      filterBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === cat)));
      posts.forEach(p => {
        const show = cat === 'all' || p.dataset.cat === cat;
        p.hidden = !show;
        if (show) { n++; p.classList.add('in'); }
      });
      count.textContent = n + (n === 1 ? ' article' : ' articles');
      empty.hidden = n > 0;
      try {
        const q = cat === 'all' ? location.pathname : '?category=' + encodeURIComponent(cat);
        history.replaceState(null, '', q + '#all');
      } catch (_) {}
      if (scroll) $('#all').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
    };
    filterBtns.forEach(b => b.addEventListener('click', () => apply(b.dataset.filter, true)));
    const initial = new URLSearchParams(location.search).get('category');
    if (initial && filterBtns.some(b => b.dataset.filter === initial)) apply(initial, false);
  }
  // the category in an article's breadcrumb opens the list already filtered
  $$('[data-goto-filter]').forEach(a => {
    a.href = a.href.split('#')[0] + '?category=' + encodeURIComponent(a.dataset.gotoFilter) + '#all';
  });

  /* ---------- Copy article link ---------- */
  $$('[data-copy-link]').forEach(b => b.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href.split('#')[0]); } catch (_) { return; }
    const c = $('#copied');
    c.classList.add('show');
    setTimeout(() => c.classList.remove('show'), 1800);
  }));

  /* ---------- Audit modal ---------- */
  const modal = $('#auditModal');
  const form = $('#auditForm');
  const openAudit = () => {
    if (!modal) return;
    modal.classList.remove('is-sent');
    if (typeof modal.showModal === 'function') { if (!modal.open) modal.showModal(); }
    else { modal.setAttribute('open', ''); }
    setTimeout(() => $('#f-name')?.focus(), 50);
  };
  $$('[data-open-audit]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); openAudit(); }));
  // a link or shared URL ending in #auditModal opens the form
  if (location.hash === '#auditModal') openAudit();
  window.addEventListener('hashchange', () => { if (location.hash === '#auditModal') openAudit(); });
  $('[data-close]', modal)?.addEventListener('click', () => modal.close());
  modal?.addEventListener('click', e => { if (e.target === modal) modal.close(); });

  form?.addEventListener('submit', async e => {
    e.preventDefault();
    let ok = true;
    $$('[required]', form).forEach(f => {
      const bad = !f.value.trim() || (f.type === 'email' && !/^\S+@\S+\.\S+$/.test(f.value));
      f.style.borderColor = bad ? 'var(--red)' : '';
      if (bad && ok) { f.focus(); ok = false; }
    });
    if (!ok) return;

    const btn = $('button[type="submit"]', form);
    const label = $('.btn__label', btn);
    const err = $('#formError');
    if (btn.disabled) return; // already sending
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    label.textContent = 'Sending…';
    err.hidden = true;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      });
      if (!res.ok) throw new Error('Formspree responded ' + res.status);
      form.reset();
      modal.classList.add('is-sent');
    } catch (_) {
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.removeAttribute('aria-busy');
      label.textContent = 'Request my audit';
    }
  });
})();
