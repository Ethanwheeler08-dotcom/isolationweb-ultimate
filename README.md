# Isolation Media website

Static site for Isolation Media, the GEO / AEO agency. Plain HTML, CSS and JS: no framework.

## Pages

- `index.html`: homepage
- `results.html`: case studies (Mobistorage, JTX Fitness, Kentaur)
- `insights.html`: all articles, with category filters
- `insights/*.html`: one page per article
- `sitemap.xml`, `robots.txt`: for search engines and AI crawlers

## Editing content

Articles live in `content/articles.json` and case studies in `CASES` inside `tools/build.py`.
After changing either, run:

    python3 tools/build.py

That regenerates the Results, Insights and article pages, refreshes the sitemap, and updates
the shared header, footer, audit form and "latest articles" list on the homepage (the parts of
`index.html` between `<!-- BUILD:... -->` markers). Everything else in `index.html` is edited by hand.

- `assets/css/styles.css`: design tokens and layout (brand colours are in `:root`)
- `assets/js/main.js`: menu, reveals, demos, testimonials, FAQ, article filters, audit form
- `assets/img`: images (WebP); `assets/img/covers` holds one cover per article category

## Run locally

    python3 -m http.server 8080

Then open http://localhost:8080.

## Audit form

"Book a free audit" opens a pop-up form (on every page) that posts to Formspree
(https://formspree.io/f/mqpqwowr) in the background, so visitors stay on the page.
Submissions arrive at the email address set in your Formspree dashboard. The form includes
a hidden `_gotcha` spam trap and a `_subject` of "New audit request - Isolation Media".
The form markup is in `MODAL` in `tools/build.py`; the submit code is in `assets/js/main.js`.
Linking to any page with `#auditModal` on the end opens the form.
