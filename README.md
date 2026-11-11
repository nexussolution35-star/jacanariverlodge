# Jacana River Lodge — Website

A luxury marketing website for **Jacana River Lodge**, a 5-star exclusive self-catering
safari lodge on the Crocodile River in the Mjejane Private Game Reserve (Greater Kruger,
Mpumalanga, South Africa).

## URLs, SEO and shared parts (read this first)

Every page lives at the **same path as on the live jacanariverlodge.com**, as `folder/index.html`
(e.g. Rates & Facilities is `/facilities/`), with root-relative links. Keep it that way: the live
URLs carry the site's Google rankings. The preservation plan is in `seo/` (`seo/README.md`, `url-map.csv`).

After editing pages, regenerate the shared parts from the repo root, in this order:

```bash
python3 tools/header.py   # floating nav: Stay / Activities / Mjejane Reserve dropdowns, News, Contact Us, Book Now
python3 tools/footer.py   # site footer (Explore, Plan your stay, awards)
python3 tools/silo.py     # breadcrumbs + BreadcrumbList schema + "more in this section" block
python3 tools/seo.py      # titles/meta (live, or the approved spec overrides), canonicals, /activities/ copy, sitemaps
python3 tools/audit.py    # report-only SEO scorecard
```

**Silo structure.** `tools/silo_map.py` holds the approved structure (`seo/Jacana-Site-Structure.pdf`):
every page's label, parent, silo and one-line blurb, plus the menu. The menu, breadcrumbs and the
"more in this section" block all come from it, so a new page needs one line there (pick its parent
in the same silo) and then the commands above. Links run hub ⇄ page and between siblings, never
across silos; Book Now and Contact Us are open to every page. The block sits between
`<!-- SILO -->` and `<!-- /SILO -->` before the footer; don't edit it by hand.

**Titles and descriptions.** Pages that exist on the live site keep their live title and description
(`seo/url-inventory.csv`) unless `TITLE_OVERRIDES` / `META_OVERRIDES` in `tools/seo.py` carry an
approved change (SEO Spec Part 1: Home & Stay). New pages keep what is in their own `<head>`.

`robots.txt` is the live site's file. Preview deploys must replace it with `Disallow: /`
so the preview never competes with the live site in Google.

## How this was built

This site was produced from two reference inputs:

- **Website A — Newmark Hotels (conversion framework).** The full section sequence and
  every conversion element of the Newmark homepage was replicated: hero, brand statement,
  destinations grid, featured experiences, inspiring stories, newsletter sign-up,
  testimonials, awards & associations, the "Join & Enjoy More" book-direct loyalty block,
  and the call/email/reserve contact block — in the same order, nothing removed, merged or
  reordered.
- **Website B — Jacana River Lodge (visual language + content).** Typography (Roboto Slab
  display / Roboto body), the cream / rust (`#954635`) / charcoal (`#323132`) palette drawn
  from the logo, image treatments, overlays, parallax, section dividers and card styling all
  follow Jacana's own visual identity. All copy, testimonials, journal entries and imagery
  are Jacana's own.

The result keeps Newmark's conversion architecture while rendering everything in Jacana's
brand world.

## Section map (Newmark architecture → Jacana content)

| # | Newmark section | Jacana rendering |
|---|-----------------|------------------|
| 1 | Hero property slider | Rotating banner of the lodge & reserve + booking CTAs |
| 2 | "World-class management company" | "Welcome Home" brand statement |
| 3 | Destinations | Explore the Mjejane (About / Wildlife / Big 5 / Accommodation) |
| 4 | Featured experiences | Game drives, pool, boma, birding, stargazing, family |
| 5 | Inspiring stories | The Jacana Journal (blog cards) |
| 6 | Newsletter sign-up | "Bush inspiration in your inbox" |
| 7 | What our clients say | Real guest reviews carousel |
| 8 | Awards & associations | 5-star grading & tourism memberships |
| 9 | Join & Enjoy More | Book Direct & Enjoy More |
| 10 | Call / Email / Reserve | Contact cards + map |

## Structure

```
index.html            # the homepage (full conversion architecture)
css/styles.css        # design system & responsive layout
js/main.js            # hero slider, nav, testimonials, scroll reveal, newsletter
assets/images/        # Jacana's own photography + recreated SVG logo
```

## Running locally

It is a static site — open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Notes

- `assets/images/logo.svg` is a clean SVG recreation of the Jacana brand mark
  (the original logo is referenced on the live site as a raster file).
- The newsletter form performs front-end validation only; wire it to your email
  provider/CRM endpoint for production.
- The contact map uses an embedded Google Map of the Mjejane Game Reserve.
