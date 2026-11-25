#!/usr/bin/env python3
"""Build the Isolation Media sub-pages.

Generates insights.html, results.html, one page per article in insights/,
sitemap.xml, and keeps the shared header, footer, audit form and latest
articles block in index.html in sync.

Content lives in content/articles.json (articles) and in CASES below.
Run from the repo root:  python3 tools/build.py
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://isolationmedia.com"
EMAIL = "admin@isolationmedia.com"
MAIL_Q = f"mailto:{EMAIL}?subject=GEO%20question"
FORMSPREE = "https://formspree.io/f/mqpqwowr"

ARTICLES = json.loads((ROOT / "content/articles.json").read_text())
CATEGORY_ORDER = ["Australia", "Fundamentals", "Industry", "Measurement", "Practical", "Strategy", "Technical"]
COVERS = {c: f"assets/img/covers/{c.lower()}.webp" for c in CATEGORY_ORDER}

e = html.escape


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# --------------------------------------------------------------------------
# Icons
# --------------------------------------------------------------------------
ARROW = '<svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW_L = '<svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M13 8H3M7 4L3 8l4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEVRON = '<svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECK = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8.5l3 3 7-7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SPARK = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 1.5l1.6 4.9 4.9 1.6-4.9 1.6L8 14.5l-1.6-4.9L1.5 8l4.9-1.6z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>'
MARK = '<span class="brand__mark" aria-hidden="true"><i></i><i></i></span>'


# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------
def head(p, title, desc, path, og_image="assets/img/hero-sky.webp", og_type="website", jsonld=None):
    ld = ""
    if jsonld:
        ld = '\n  <script type="application/ld+json">\n' + json.dumps(jsonld, indent=2, ensure_ascii=False) + "\n  </script>"
    return f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{SITE}/{path}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Isolation Media">
  <meta property="og:url" content="{SITE}/{path}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{SITE}/{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230B1E1A'/%3E%3Crect x='12' y='6' width='8' height='7' rx='1.5' fill='%232BE4AC'/%3E%3Crect x='12' y='15' width='8' height='11' rx='1.5' fill='%23fff'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..700&display=swap">
  <link rel="stylesheet" href="{p}assets/css/styles.css">{ld}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
"""


def header(p, current=None, home=False):
    """p = path prefix to site root; home = links point at on-page anchors."""
    h = "" if home else f"{p}index.html"

    def link(label, href, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    items = [
        link("Services", f"{h}#services", "services"),
        link("Results", f"{p}results.html", "results"),
        link("Process", f"{h}#process", "process"),
        link("Insights", f"{p}insights.html", "insights"),
        link("FAQ", f"{h}#faq", "faq"),
    ]
    top = "#top" if home else f"{p}index.html"
    return f"""<!-- BUILD:HEADER -->
  <header class="header" id="top">
    <div class="header__inner">
      <a href="{top}" class="brand" aria-label="Isolation Media home">
        {MARK}
        <span class="brand__word">isolation<b>.</b></span>
      </a>
      <nav class="nav" aria-label="Primary">
        {"\n        ".join(items)}
      </nav>
      <div class="header__actions">
        <a class="link" href="{MAIL_Q}">Talk to a specialist</a>
        <button class="btn btn--dark" data-open-audit>Book a free audit</button>
        <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav"><span></span></button>
      </div>
    </div>
    <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile">
      {"\n      ".join(items)}
      <a href="{MAIL_Q}">Talk to a specialist</a>
      <button class="btn btn--dark" data-open-audit>Book a free audit</button>
    </nav>
  </header>
  <!-- /BUILD:HEADER -->"""


def cta(p, title="Be the answer.", text="A free audit of what the engines say about your market today, and exactly what we would do about it."):
    return f"""
    <section class="section">
      <div class="frame cta-wrap">
        <div class="cta reveal">
          <h2>{title}</h2>
          <p>{text}</p>
          <div class="hero__cta">
            <a class="btn btn--light" href="{MAIL_Q}">Talk to a specialist</a>
            <button class="btn btn--dark" data-open-audit>Book a free audit</button>
          </div>
        </div>
      </div>
    </section>"""


def footer(p, home=False):
    h = "" if home else f"{p}index.html"
    top = "#top" if home else f"{p}index.html"
    return f"""<!-- BUILD:FOOTER -->
  <footer class="section footer">
    <div class="frame pad">
      <div class="footer__top">
        <div class="footer__about">
          <a href="{top}" class="brand" aria-label="Isolation Media home">
            {MARK}
            <span class="brand__word">isolation<b>.</b></span>
          </a>
          <p>The generative engine optimisation agency. A small, senior team that makes AI assistants recommend your company. Nothing else.</p>
          <span class="status-pill"><i></i>One company per market</span>
        </div>
        <div class="footer__col">
          <h4>Services</h4>
          <a href="{h}#svc-intel">Answer intelligence</a>
          <a href="{h}#svc-content">Content engines trust</a>
          <a href="{h}#svc-citations">Citations that count</a>
          <a href="{h}#svc-measure">Measurement</a>
        </div>
        <div class="footer__col">
          <h4>Company</h4>
          <a href="{p}results.html">Results</a>
          <a href="{p}insights.html">Insights</a>
          <a href="{h}#process">Process</a>
          <a href="{h}#faq">FAQ</a>
        </div>
        <div class="footer__col">
          <h4>Contact</h4>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <a href="#auditModal" data-open-audit>Book a free audit</a>
          <a href="{MAIL_Q}">Talk to a specialist</a>
        </div>
      </div>
      <div class="wordmark" aria-hidden="true">isolation.</div>
    </div>
    <div class="frame pad">
      <div class="footer__bottom">
        <span>© 2026 Isolation Media. All rights reserved.</span>
        <span>Be the answer. Nothing else.</span>
      </div>
    </div>
  </footer>
  <!-- /BUILD:FOOTER -->"""


MODAL = f"""<!-- BUILD:MODAL -->
  <dialog class="modal" id="auditModal" aria-labelledby="auditTitle">
    <div class="modal__inner">
      <button class="modal__close" data-close aria-label="Close"><svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
      <span class="eyebrow">Book a free audit</span>
      <h2 id="auditTitle">Let's make you the answer.</h2>
      <p class="modal__lede">Tell us what you want to be recommended for. We'll ask the engines your buyers' questions and show you who they name today. If we already work with a competitor, we'll tell you straight away.</p>
      <form class="form" id="auditForm" action="{FORMSPREE}" method="POST" novalidate>
        <input type="hidden" name="_subject" value="New audit request - Isolation Media">
        <div class="hp-field" aria-hidden="true"><label for="f-gotcha">Leave this field empty</label><input id="f-gotcha" type="text" name="_gotcha" tabindex="-1" autocomplete="off"></div>
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="f-company">Company and website</label><input id="f-company" name="company" autocomplete="organization" required></div>
        <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
        <div class="field field--full"><label for="f-message">What do you want to be the answer for?</label><textarea id="f-message" name="message" placeholder="e.g. Best mobile storage in Perth"></textarea></div>
        <p class="form__error" id="formError" role="alert" hidden>Sorry, your request didn't send. Please email us at <a href="mailto:{EMAIL}">{EMAIL}</a> instead.</p>
        <div class="form__foot">
          <small>We reply within one business day.</small>
          <button class="btn btn--dark" type="submit"><span class="btn__label">Request my audit</span> <svg class="arrow" width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        </div>
      </form>
      <div class="form__done" role="status">
        <div class="tick"><svg width="22" height="22" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8.5l3 3 7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <h3 class="h3">Thanks, we've got your request.</h3>
        <p class="lead" style="font-size:15px;margin-top:8px">We'll reply within one business day. Anything to add? Email <a href="mailto:{EMAIL}" style="color:var(--accent-ink)">{EMAIL}</a>.</p>
      </div>
    </div>
  </dialog>
  <!-- /BUILD:MODAL -->"""


def tail(p):
    return f"""
  {MODAL}

  <script src="{p}assets/js/main.js" defer></script>
</body>
</html>
"""


def page(p, current, head_html, main_html):
    return head_html + "\n  " + header(p, current) + '\n\n  <main id="main">' + main_html + "\n  </main>\n\n  " + footer(p) + "\n" + tail(p)


# --------------------------------------------------------------------------
# Article helpers
# --------------------------------------------------------------------------
def post_row(a, p, extra=""):
    return f"""
          <a class="post reveal" href="{p}insights/{a['slug']}.html" data-cat="{a['category']}"{extra}>
            <div class="post__date">{fmt_date(a['date'])}<br><span>{a['read']}</span></div>
            <div><span class="post__cat">{a['category']}</span><h3>{e(a['title'])}</h3><p>{e(a['description'])}</p></div>
            <div class="post__thumb"><img src="{p}{COVERS[a['category']]}" alt="" loading="lazy" width="480" height="252"></div>
          </a>"""


def article_card(a, p):
    return f"""
          <a class="acard reveal" href="{p}insights/{a['slug']}.html">
            <div class="acard__img" style="background-image:url('{p}{COVERS[a['category']]}')"></div>
            <div class="acard__body">
              <span class="post__cat">{a['category']}</span>
              <h3>{e(a['title'])}</h3>
              <div class="acard__meta"><span>{fmt_date(a['date'])}</span><span>{a['read']}</span></div>
            </div>
          </a>"""


def related(a, n=3, skip=()):
    skip = {a["slug"], *skip}
    same = [x for x in ARTICLES if x["category"] == a["category"] and x["slug"] not in skip]
    rest = [x for x in ARTICLES if x["category"] != a["category"] and x["slug"] not in skip]
    return (same[:2] + rest)[:n] if len(same) >= 2 else (same + rest)[:n]


# --------------------------------------------------------------------------
# insights.html
# --------------------------------------------------------------------------
def build_insights():
    p = ""
    feat, rest = ARTICLES[0], ARTICLES[1:]
    counts = {c: sum(1 for a in ARTICLES if a["category"] == c) for c in CATEGORY_ORDER}
    chips = [f'<button aria-pressed="true" data-filter="all">All<span>{len(ARTICLES)}</span></button>']
    chips += [f'<button aria-pressed="false" data-filter="{c}">{c}<span>{counts[c]}</span></button>' for c in CATEGORY_ORDER if counts[c]]
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Isolation Media Insights",
        "url": f"{SITE}/insights.html",
        "publisher": {"@type": "Organization", "name": "Isolation Media", "url": SITE + "/"},
        "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": f"{SITE}/insights/{a['slug']}.html", "datePublished": a["date"]} for a in ARTICLES],
    }
    main = f"""
    <section>
      <div class="frame pad page-hero">
        <span class="eyebrow reveal">Insights</span>
        <h1 class="reveal" data-d="1">Notes from inside the answers. <span class="dim">How AI assistants choose who to recommend.</span></h1>
        <p class="lead reveal" data-d="2">What we are learning about generative engine optimisation, written in plain English for the people who own the companies being chosen.</p>
        <div class="page-hero__meta reveal" data-d="3"><span><i></i>{len(ARTICLES)} articles</span><span>A new one every week</span><span>No jargon, no filler</span></div>
      </div>
    </section>

    <section class="section">
      <a class="frame featured" href="insights/{feat['slug']}.html">
        <div class="featured__img reveal" style="background-image:url('{COVERS[feat['category']]}')">
          <div class="float-card" aria-hidden="true">
            <div class="float-card__head">{SPARK}In this article<time>{feat['read']}</time></div>
            <ul class="float-card__list">{"".join(f"<li>{h}</li>" for h in re.findall(r"<h2>(.*?)</h2>", feat["body"])[:4])}</ul>
          </div>
        </div>
        <div class="featured__copy">
          <span class="post__cat reveal">{feat['category']} · Latest</span>
          <h2 class="reveal" data-d="1">{e(feat['title'])}</h2>
          <p class="reveal" data-d="1">{e(feat['description'])}</p>
          <div class="featured__meta reveal" data-d="2"><span>{fmt_date(feat['date'])}</span><span>{feat['read']}</span><span>By Isolation Media</span></div>
          <span class="btn btn--dark reveal" data-d="2">Read the article <span class="arrow">{ARROW}</span></span>
        </div>
      </a>
    </section>

    <div class="filters section" id="all">
      <div class="frame pad filters__inner" role="group" aria-label="Filter articles by category">
        {"\n        ".join(chips)}
        <span class="filters__count" id="postCount" aria-live="polite">{len(rest)} articles</span>
      </div>
    </div>

    <section>
      <div class="frame pad list-block">
        <div class="posts" id="postList">{"".join(post_row(a, p) for a in rest)}
        </div>
        <p class="empty" id="postEmpty" hidden>No other articles in this category yet. The latest one is featured above.</p>
      </div>
    </section>
{cta(p, "Rather we just did it?", "The free audit shows you what the engines say about your market today, and what we would do about it.")}"""
    head_html = head(p, "Insights · Isolation Media", "Plain English notes on generative engine optimisation (GEO) and answer engine optimisation (AEO): how ChatGPT, Perplexity, Gemini and AI Overviews choose who to recommend.", "insights.html", jsonld=jsonld)
    (ROOT / "insights.html").write_text(page(p, "insights", head_html, main))


# --------------------------------------------------------------------------
# insights/<slug>.html
# --------------------------------------------------------------------------
def build_article(i, a):
    p = "../"
    body = a["body"]
    toc = []

    def add_id(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = slugify(text)
        toc.append((sid, html.unescape(text)))
        return f'<h2 id="{sid}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)
    toc_links = "\n                ".join(
        f'<li><a href="#{sid}"{" class=\"is-active\"" if k == 0 else ""}>{e(t)}</a></li>' for k, (sid, t) in enumerate(toc)
    )
    newer = ARTICLES[i - 1] if i > 0 else None
    older = ARTICLES[i + 1] if i + 1 < len(ARTICLES) else None
    pager = ""
    if newer or older:
        left = f'<a href="{older["slug"]}.html"><small>{ARROW_L} Previous article</small><b>{e(older["title"])}</b></a>' if older else "<span></span>"
        right = f'<a href="{newer["slug"]}.html"><small>Next article {ARROW}</small><b>{e(newer["title"])}</b></a>' if newer else "<span></span>"
        pager = f"""
    <section class="section">
      <nav class="frame pager" aria-label="More articles">
        {left}
        {right}
      </nav>
    </section>"""
    url = f"{SITE}/insights/{a['slug']}.html"
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": a["title"],
                "description": a["description"],
                "datePublished": a["date"],
                "dateModified": a["date"],
                "articleSection": a["category"],
                "timeRequired": "PT" + a["read"].split()[0] + "M",
                "image": f"{SITE}/{COVERS[a['category']]}",
                "url": url,
                "mainEntityOfPage": url,
                "author": {"@type": "Organization", "name": "Isolation Media", "url": SITE + "/"},
                "publisher": {"@type": "Organization", "name": "Isolation Media", "url": SITE + "/"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{SITE}/insights.html"},
                    {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
                ],
            },
        ],
    }
    main = f"""
    <article>
      <section>
        <div class="frame pad article-hero">
          <nav class="crumbs reveal" aria-label="Breadcrumb"><a href="../insights.html">Insights</a>{CHEVRON}<a href="../insights.html#all" data-goto-filter="{a['category']}">{a['category']}</a></nav>
          <h1 class="reveal" data-d="1">{e(a['title'])}</h1>
          <p class="lead reveal" data-d="2">{e(a['description'])}</p>
          <div class="byline reveal" data-d="3">
            <span class="byline__avatar">{MARK}</span>
            <span><b>Isolation Media</b><small>GEO specialists</small></span>
            <span class="sep"></span>
            <span class="meta"><time datetime="{a['date']}">{fmt_date(a['date'])}</time> · {a['read']}</span>
          </div>
          <div class="article-cover reveal" data-d="2" style="background-image:url('{p}{COVERS[a['category']]}');margin-top:56px" role="img" aria-label="{a['category']} cover"></div>
        </div>
      </section>

      <section class="section">
        <div class="frame how">
          <aside class="how__nav">
            <div class="rail-wrap">
              <div class="rail-label">On this page</div>
              <ul class="rail" data-spy>
                {toc_links}
              </ul>
              <div class="rail-cta">
                <b>Want this done for you?</b>
                <p>See who the engines name in your market today.</p>
                <button class="btn btn--dark btn--block" data-open-audit>Book a free audit</button>
              </div>
            </div>
          </aside>
          <div class="how__content" style="display:block">
            <div class="prose">
{body}
            </div>

            <a class="chat-cta" href="{MAIL_Q}">
              <span class="chat-cta__avatar">{MARK}</span>
              <span class="chat-cta__text"><b>Chat with a GEO specialist now</b><small>Questions about your own market? Ask someone who does this every day.</small></span>
              <span class="btn btn--light">Start the conversation</span>
            </a>

            <div class="article-foot">
              <a class="text-link" href="../insights.html">{ARROW_L} Back to all articles</a>
              <div class="article-foot__share">
                <span class="copied" id="copied">Link copied</span>
                <button class="icon-btn" data-copy-link aria-label="Copy link to this article"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6.5 9.5l3-3M5.5 7.5l-1.5 1.5a2.1 2.1 0 003 3l1.5-1.5M10.5 8.5L12 7a2.1 2.1 0 00-3-3L7.5 5.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg></button>
                <a class="icon-btn" href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" rel="noopener" aria-label="Share on LinkedIn"><svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M3.6 5.6h-2.4V14h2.4V5.6zM2.4 4.5a1.4 1.4 0 100-2.8 1.4 1.4 0 000 2.8zM14.8 9.3c0-2.3-1.2-3.9-3.4-3.9-1.1 0-1.9.6-2.2 1.2V5.6H6.9V14h2.4V9.8c0-1.1.4-1.9 1.4-1.9s1.6.8 1.6 1.9V14h2.5V9.3z"/></svg></a>
                <a class="icon-btn" href="mailto:?subject={e(a['title'])}&amp;body={url}" aria-label="Share by email"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="2" y="3.5" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.4"/><path d="M2.5 4.5L8 9l5.5-4.5" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg></a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </article>
{pager}

    <section class="section">
      <div class="frame pad block">
        <div class="block__head">
          <div>
            <span class="eyebrow reveal">Keep reading</span>
            <h2 class="display reveal" data-d="1">More from inside the answers.</h2>
          </div>
          <a class="text-link reveal" href="../insights.html">All articles {ARROW}</a>
        </div>
        <div class="acards">{"".join(article_card(r, p) for r in related(a, skip=[x["slug"] for x in (newer, older) if x]))}
        </div>
      </div>
    </section>
{cta(p)}"""
    head_html = head(p, f"{a['title']} · Isolation Media", a["description"], f"insights/{a['slug']}.html",
                     og_image=COVERS[a["category"]], og_type="article", jsonld=jsonld)
    (ROOT / "insights" / f"{a['slug']}.html").write_text(page(p, "insights", head_html, main))


# --------------------------------------------------------------------------
# results.html
# --------------------------------------------------------------------------
CASES = [
    {
        "id": "mobistorage", "no": "01", "name": "Mobistorage", "sector": "Mobile storage", "place": "Perth, WA",
        "question": "Best mobile storage in Perth", "subhead": "Teaching the engines the difference between mobile and self storage.", "image": "assets/img/hero-sky.webp",
        "gap": "Engines named national self storage chains instead",
        "challenge": "Mobistorage is WA owned and delivers the container to your door rather than making you hire a truck, which is a genuinely different product to traditional self storage. The trouble was that assistants answering Perth storage questions did not know the difference, so they named national self storage chains instead.",
        "approach": "We rebuilt the entity around the mobile model, gave every metro corridor from Joondalup to Baldivis a page with real specifics, and made their five star review base legible to the engines.",
        "built": ["Entity rebuilt around the mobile model", "A page for every metro corridor, Joondalup to Baldivis", "Five star review base made legible to the engines"],
        "facts": [("WA owned", "Independent operator"), ("Metro wide", "Door to door service"), ("5 star", "Google review rating")],
        "quote": "People ring up and tell us the AI recommended us. That never used to happen, and it is the easiest conversation our team has ever had.",
        "who": "James Busby", "role": "Director, Mobistorage",
    },
    {
        "id": "jtx-fitness", "no": "02", "name": "JTX Fitness", "sector": "Home fitness", "place": "United Kingdom",
        "question": "Best treadmill for a home gym", "subhead": "Making a family maker's specification advantage visible to AI.", "image": "assets/img/texture-sand.webp",
        "gap": "Engines defaulted to the household names",
        "challenge": "JTX Fitness has manufactured and sold its own equipment from West Sussex since 2009, which is why its specification beats brands several times its size. That advantage was invisible to answer engines, which defaulted to the household names when asked what to buy.",
        "approach": "We built comparison content that states plainly where JTX wins and where it does not, put full specifications into readable text rather than images, and made the home service warranty and refurbished range part of the evidence engines cite.",
        "built": ["Honest comparison content, wins and losses stated plainly", "Full specifications moved out of images into readable text", "Home service warranty and refurbished range made citable"],
        "facts": [("Est. 2009", "Family run"), ("Direct", "Maker and retailer"), ("West Sussex", "UK based")],
        "quote": "We have always been able to out spec the big brands. The difference now is that when someone asks what to buy, we are the name that comes back.",
        "who": "Jamie Forshaw", "role": "Head of Marketing, JTX Fitness",
    },
    {
        "id": "kentaur", "no": "03", "name": "Kentaur", "sector": "Equestrian", "place": "Global",
        "question": "Which brand makes the best jumping saddles", "subhead": "Turning 35 years of saddle making into evidence engines quote.", "image": "assets/img/texture-clouds.webp",
        "gap": "Their provenance existed in almost no readable form",
        "challenge": "Kentaur has made saddles, boots and bridles in Prostějov since 1991 and tests every model at the stable attached to its own factory before release. In a category where riders ask assistants which brand to trust, that provenance is exactly the kind of evidence a model wants to quote, and almost none of it existed in a readable form.",
        "approach": "We built the testing and craft story into citable content, went after the discipline specific questions rather than generic ones, and earned presence in the rider communities and retailer sites the engines actually read.",
        "built": ["Testing and craft story turned into citable content", "Discipline specific questions targeted, not generic ones", "Presence earned in rider communities and retailer sites"],
        "facts": [("Est. 1991", "Czech made"), ("40+", "Countries sold in"), ("In house", "Tested at their own stable")],
        "quote": "Riders trust a recommendation far more than an ad. Getting named in those answers has done more for the brand than anything else we have tried.",
        "who": "Lucy", "role": "Marketing Manager, Kentaur",
    },
]


def build_results():
    p = ""
    rail = "\n                ".join(
        f'<li><a href="#{c["id"]}"{" class=\"is-active\"" if k == 0 else ""}>{c["name"]}<span class="rail-sub">{c["sector"]} · {c["place"]}</span></a></li>'
        for k, c in enumerate(CASES))
    blocks = []
    for c in CASES:
        facts = "".join(f"<div><b>{e(v)}</b><span>{e(l)}</span></div>" for v, l in c["facts"])
        built = "".join(f"<li>{CHECK}{e(b)}</li>" for b in c["built"])
        blocks.append(f"""
            <article class="feature case-detail" id="{c['id']}">
              <div class="feature__icon reveal"><span>{c['no']}</span>{c['name']} · {c['sector']} · {c['place']}</div>
              <h3 class="h3 reveal">“{e(c['question'])}.” <span class="dim">{e(c['subhead'])}</span></h3>
              <div class="feature__visual reveal" data-d="1" style="background:var(--panel) url('{c['image']}') center / cover">
                <div class="mock brief">
                  <div class="brief__q"><small><i></i>The question worth owning</small><b>“{e(c['question'])}”</b></div>
                  <dl>
                    <dt>Client</dt><dd>{c['name']}</dd>
                    <dt>Market</dt><dd>{c['sector']} · {c['place']}</dd>
                    <dt>Engines tracked</dt><dd>ChatGPT, Perplexity, Gemini, Claude, AI Overviews, Copilot</dd>
                    <dt>The gap</dt><dd>{e(c['gap'])}</dd>
                  </dl>
                  <ul class="brief__built">{built}</ul>
                </div>
              </div>
              <div class="story">
                <div class="reveal"><h4 style="--c:var(--red)">The challenge</h4><p>{e(c['challenge'])}</p></div>
                <div class="reveal" data-d="1"><h4>What we did</h4><p>{e(c['approach'])}</p></div>
              </div>
              <div class="facts reveal">{facts}</div>
              <div class="roi reveal">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.5" stroke="currentColor" stroke-width="1.4"/><path d="M5.5 7V5a2.5 2.5 0 015 0v2" stroke="currentColor" stroke-width="1.4"/></svg>
                <div><b>Commercial results released on request</b>We walk through the full numbers for this engagement on the audit call, with the client's permission.</div>
              </div>
              <blockquote class="case-quote reveal">
                <p>“{e(c['quote'])}”</p>
                <footer><b>{e(c['who'])}</b> · {e(c['role'])}</footer>
              </blockquote>
            </article>""")
    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Results · Isolation Media",
        "url": f"{SITE}/results.html",
        "about": "Generative engine optimisation case studies",
        "hasPart": [{"@type": "Article", "headline": f"{c['name']}: “{c['question']}”", "url": f"{SITE}/results.html#{c['id']}"} for c in CASES],
    }
    main = f"""
    <section>
      <div class="frame pad page-hero">
        <span class="eyebrow reveal">Results</span>
        <h1 class="reveal" data-d="1">Proof that the answer pays. <span class="dim">Measured on revenue, not screenshots.</span></h1>
        <p class="lead reveal" data-d="2">We measure one thing: whether being the recommendation produces revenue. Every case leads with the question that client set out to own, because owning it is what makes the rest of the numbers move.</p>
        <div class="hero__cta reveal" data-d="3" style="margin-top:32px">
          <a class="btn btn--light" href="#cases">Read the case studies</a>
          <button class="btn btn--dark" data-open-audit>Book a free audit</button>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="frame stats">
        <div class="stat reveal"><div class="stat__num" data-count="12.3" data-decimals="1" data-suffix="×">12.3×</div><p>average return on every dollar invested with us</p></div>
        <div class="stat reveal" data-d="1"><div class="stat__num" data-count="68" data-suffix="%">68%</div><p>average share of AI answers won in our clients' categories</p></div>
        <div class="stat reveal" data-d="2"><div class="stat__num" data-count="40" data-suffix="+">40+</div><p>companies made the default recommendation in their market</p></div>
        <div class="stat reveal" data-d="3"><div class="stat__num">9/10</div><p>clients that stay with us past the first year</p></div>
      </div>
    </section>

    <section class="section" id="cases">
      <div class="frame">
        <div class="pad how-intro">
          <span class="eyebrow reveal">Case studies</span>
          <h2 class="display reveal" data-d="1">The work, and what it changed. <span class="dim">Real clients who agreed to be named, each competing to own a single question.</span></h2>
        </div>
        <div class="how">
          <aside class="how__nav">
            <div class="rail-wrap">
              <div class="rail-label">Case studies</div>
              <ul class="rail" data-spy>
                {rail}
              </ul>
              <div class="rail-cta">
                <b>Want the same for your market?</b>
                <p>Start with the free audit. One company per market.</p>
                <button class="btn btn--dark btn--block" data-open-audit>Book a free audit</button>
              </div>
            </div>
          </aside>
          <div class="how__content">{"".join(blocks)}
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="frame stats">
        <div class="stat promise reveal"><div class="promise__num">1 of 1</div><h3>One company per market</h3><p>We never chase the same answers for two competitors. While you're with us, your rivals can't hire us.</p></div>
        <div class="stat promise reveal" data-d="1"><div class="promise__num">90 days</div><h3>To see your share move</h3><p>Tracked from day one, so you watch it happen rather than take our word for it.</p></div>
        <div class="stat promise reveal" data-d="2"><div class="promise__num">Senior</div><h3>People only</h3><p>The person who audits your market does the work. No juniors, no account managers relaying messages.</p></div>
        <div class="stat promise reveal" data-d="3"><div class="promise__num">No lock in</div><h3>Month to month after 90 days</h3><p>We'd rather earn the renewal than enforce a contract. Reporting stays honest, including what didn't work.</p></div>
      </div>
    </section>

    <section class="section">
      <div class="frame pad block">
        <div class="block__head">
          <div>
            <span class="eyebrow reveal">Insights</span>
            <h2 class="display reveal" data-d="1">How we think about the work. <span class="dim">Plain English, from the same people.</span></h2>
          </div>
          <a class="text-link reveal" href="insights.html">Read every article {ARROW}</a>
        </div>
        <div class="acards">{"".join(article_card(a, p) for a in ARTICLES[:3])}
        </div>
      </div>
    </section>
{cta(p, "Is the answer you?", "We will show you exactly who the engines name in your market today, free, on one call.")}"""
    head_html = head(p, "Results · Isolation Media", "GEO case studies: how Mobistorage, JTX Fitness and Kentaur became the answer AI assistants give in their markets. 12.3× average return, 68% average share of AI answers.", "results.html", jsonld=jsonld)
    (ROOT / "results.html").write_text(page(p, "results", head_html, main))


# --------------------------------------------------------------------------
# index.html: keep shared chrome and latest articles in sync
# --------------------------------------------------------------------------
def sync_index():
    path = ROOT / "index.html"
    s = path.read_text()

    def swap(s, name, new):
        pat = re.compile(rf"<!-- BUILD:{name} -->.*?<!-- /BUILD:{name} -->", re.S)
        assert pat.search(s), f"marker {name} missing in index.html"
        return pat.sub(lambda m: new, s)

    s = swap(s, "HEADER", header("", None, home=True))
    s = swap(s, "FOOTER", footer("", home=True))
    s = swap(s, "MODAL", MODAL)
    s = swap(s, "POSTS", "<!-- BUILD:POSTS -->" + "".join(post_row(a, "") for a in ARTICLES[:4]) + "\n          <!-- /BUILD:POSTS -->")
    path.write_text(s)


def build_sitemap():
    urls = [("", "1.0"), ("results.html", "0.8"), ("insights.html", "0.8")] + [(f"insights/{a['slug']}.html", "0.6") for a in ARTICLES]
    items = "\n".join(f"  <url><loc>{SITE}/{u}</loc><priority>{pr}</priority></url>" for u, pr in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    (ROOT / "insights").mkdir(exist_ok=True)
    build_insights()
    for i, a in enumerate(ARTICLES):
        build_article(i, a)
    build_results()
    sync_index()
    build_sitemap()
    print(f"Built insights.html, results.html, {len(ARTICLES)} articles, sitemap.xml; synced index.html")
