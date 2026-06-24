# Jacana River Lodge — Website

A luxury marketing website for **Jacana River Lodge**, a 5-star exclusive self-catering
safari lodge on the Crocodile River in the Mjejane Private Game Reserve (Greater Kruger,
Mpumalanga, South Africa).

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
