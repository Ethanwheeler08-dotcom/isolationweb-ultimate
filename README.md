# Isolation Media website

Single-page site for Isolation Media, the GEO / AEO agency. Plain HTML, CSS and JS: no build step.

- `index.html`: page content, SEO meta and JSON-LD (Organization, WebSite, FAQPage)
- `assets/css/styles.css`: design tokens and layout (brand colours are in `:root`)
- `assets/js/main.js`: menu, scroll reveals, live answer demo, testimonials, FAQ, audit form
- `assets/img`, `assets/fonts`: local images (WebP) and the Montreal logo font

## Run locally

    python3 -m http.server 8080

Then open http://localhost:8080.

## Audit form

"Book a free audit" opens a form that writes an email to admin@isolationmedia.com in the visitor's mail app.
To collect submissions without relying on the visitor's mail app, point the form at a form service
(Formspree, Netlify Forms, etc.) in `assets/js/main.js`.
