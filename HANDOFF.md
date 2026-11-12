# Handover: Jacana River Lodge rebuild

Branch: `claude/lucid-dijkstra-w1u0lu` (everything is committed and pushed).
Preview: https://jacana-river-lodge-mjejane.surge.sh (robots `Disallow: /`, never indexed).
Read `README.md` first ("URLs, SEO and shared parts").

## How the site is built
- Static HTML/CSS/JS. Every page is `folder/index.html` at the **live jacanariverlodge.com path**. Never change a URL.
- Shared parts are generated. After editing pages, run from the repo root, in order:
  ```bash
  python3 tools/header.py   # mega menu (Stay / Activities / Mjejane Reserve), News, Contact, Book Now
  python3 tools/footer.py   # footer + river divider
  python3 tools/silo.py     # breadcrumbs, BreadcrumbList schema, "more in this section" photo carousel
  python3 tools/seo.py      # titles/metas (live or approved overrides), canonicals, sitemaps
  python3 tools/audit.py    # report-only SEO scorecard
  ```
- `tools/silo_map.py` = the approved silo structure (page labels, parents, blurbs, menu). New page → one line there.
- `tools/seo.py` → `TITLE_OVERRIDES` / `META_OVERRIDES` hold every approved title/description change; everything else keeps the live value.
- Preview deploy: copy tracked files (not `seo/`, `tools/`) to a folder, add `robots.txt` with `Disallow: /`, then `surge <folder> jacana-river-lodge-mjejane.surge.sh` (needs your own Surge login/token).

## Rules the client (agency owner) set
- Accuracy over keywords. Jacana is in the **Mjejane Private Game Reserve**, a private reserve on the Kruger's southern boundary (fence removed, Big 5 roam freely, part of the Greater Kruger). It is **not** in the Kruger National Park and is **not** "Kruger Park Lodge" (another resort). Kruger access: SANParks gates (Malelane / Crocodile Bridge); the Mjejane bridge is temporarily closed.
- Reviews are quoted **word for word** (source: live Trustindex widget). Never tidy them.
- Copy prices exactly; report contradictions instead of guessing.
- Keep all live SEO text; organise it (accordions, homepage-style sections) rather than deleting it.
- Reuse homepage sections/patterns for inner pages. Flat photos, no shadows.
- Silo linking: hub ⇄ page, siblings only, no cross-silo links (hubs, Book Now, Contact are open).
- Short, precise replies. Don't ask the client obvious questions.

## Done
- All 33 live pages + new pages (61 total), live URLs, redirects plan, sitemap names as Yoast.
- SEO Spec Part 1 (Home & Stay) applied. Home targets "mpumalanga lodges" (title: "Jacana River Lodge | Safari Lodge in Mpumalanga near Kruger").
- Silo structure, mega menu with image cards, breadcrumbs, related-pages photo carousel, footer river divider.
- Accuracy review of all copy (three passes); bridge closure and Mjejane/Kruger wording fixed.
- The Lodge page rebuilt from homepage sections (intro, accommodation block, video, numbered reasons, clickable photo strip with lightbox, Life in the Mjejane, enquiry form).
- Technical: twitter cards, one `<main>`, LodgingBusiness schema (Home + Contact), canonical for `/activities/` → hub.
- Client photos swapped in (king suite, leopard, Special Khoza, bush walk, game drive).

## Next
1. Apply the Lodge-page treatment to the other Stay pages (Rates & Facilities first), then Activities and Reserve pages.
2. SEO spec Part 2 (Activities) and Part 3 (Mjejane Reserve + Plan pages), then blog migration, then the Lovable port.
3. At launch in Lovable: 301 `/activities/` → `/activities-near-mjejane/`; reinstall GTM-NG736RT, Google Ads AW-10868306513, Hotjar 3028515; forms → GHL, keep the thank-you page redirects (Ads conversions).

## Open questions for the client (live site contradicts itself)
1. Irving Knight weekend: R6 475,00 and R7 856,25 both labelled "for 8 people".
2. Bush walks: R550 "4–6 people" vs R500 "5–6 people".
3. Reservations email on the walks poster: `.co.za` vs `.com` in the text.
4. Domestic worker hours: Sat 07h30–11h45 (Rates) vs weekends 08:00–11:30 (Rules).
5. George Minnaar emergency number: +27 76 793 3497 (Contact) vs +27 76 762 3920 (Rules).
6. Packages page: "2nd night half price" vs "4th night 50% off"; which is current?
7. Packages say "4 nights" for Mon–Thu / Thu–Sun (3 nights).
8. Kruger day drives: ±12/±6 h (headings) vs 8/4 h (old text).
9. Special Khoza's name tag reads "SIBUSISO": full name wanted anywhere?

## Documents (in the other Claude account; share them to keep using them)
- Keyword research sheet (Keyword map tab): https://claude.ai/artifact/UURyY2qaQ1gu2jYVmGXXHk
- SEO Spec Part 1 doc: https://claude.ai/artifact/TrBHV7VAPkgj4h1yfEtXz9
- PDFs in `seo/`: site structure, SEO plan Part 1. Live content as Markdown in `seo/content/`.
