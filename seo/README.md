# SEO baseline — jacanariverlodge.com (live site, crawled 2026-10-29)

This folder preserves the current site's indexed URLs, on-page SEO and content **before** the redesign,
so the migration keeps existing rankings. Nothing here changes the live site.

## What's in here

| Path | Contents |
|---|---|
| `url-inventory.csv` | Every URL in the Yoast sitemaps (292): status, redirects, lastmod/published, title, meta description, H1, canonical, robots, word count, inbound internal links, schema types |
| `url-map.csv` | **Draft** preservation plan: per old URL → action (`KEEP` / `KEEP (review)` / `PROPOSED 301`), new path, role in the new site, notes |
| `content/<type>/<slug>.md` | Main content of every page, post, category, testimonial and portfolio item as Markdown, with SEO metadata in front matter (185 files) |
| `source/` | Live `robots.txt`, `sitemap_index.xml` and all sub-sitemaps |
| `archive/live-html-2026-10-29.tar.gz` | Raw HTML of all 292 URLs + `crawl.json` (full-fidelity backup) |
| `tools/` | `crawl.py` and `build_inventory.py` used to produce the above (re-runnable) |

## Baseline facts

- **Platform:** WordPress, BeTheme + WPBakery/Muffin Builder, Yoast SEO. Booking engine: NightsBridge (`book.nightsbridge.com/29205`).
- **Indexed URLs (sitemaps):** 292 — 33 pages, 137 posts, 106 tags, 8 testimonials, 3 portfolio items, 4 categories, 1 author.
- **Health:** all 292 return `200`, no existing redirect chains, every URL self-canonical, none `noindex` (tags included).
- **Active content programme:** 24 posts last modified in 2026, latest 2026-10-11, author `mjejane-game-reserve-expert`.
- **Strongest content pages:** `/mjejane-game-reserve-accommodation-guide/` (pillar, ~6.8k words), `/mjejane-game-reserve-birding-guide/`, `/rules-and-safety/`.

## Issues found (not yet fixed — for the rebuild)

- **Keyword cannibalisation:** homepage title targets "Best Game Lodges Mpumalanga"; ~17 posts target "game lodges in Mpumalanga", ~35 "self-catering", ~29 "near Kruger".
- **Duplicates:** `/activities/` = `/activities-near-mjejane/` (same title + meta); `/mjejane-accommodation-specials/` reuses `/book-now/`'s meta and H1; 3 duplicate post-title pairs and 2 duplicate post-meta pairs (see `url-map.csv` notes).
- **Metadata:** 17 pages/posts missing a meta description; 135 of 170 titles over 60 chars; 93 meta descriptions over 160 chars.
- **Thin pages (<300 words):** 26, mostly testimonials, portfolio items, thank-you pages, `/gallery/`, `/contact-us/`.
- **H1s:** 62 URLs show 0 or 2+ H1s in raw server HTML. Parts of the theme render via JavaScript (homepage shows 0 raw / 2 rendered), so **verify with a rendered crawl** before treating these as faults.
- **Internal linking:** link equity flows mainly through a "recent posts" widget (newest posts get 75–87 links); money pages get few contextual links (`/facilities/` 5, home 10).
- **Footer outbound links:** three site-wide **followed** links to bluecabinseo.co.za with commercial anchors ("SEO Packages South Africa", "Google Ads South Africa"). Recommend nofollow or removal. (`/backlinks/` itself is just a harmless "useful links" page.)
- **Schema:** only Yoast's generic `Organization`/`WebPage`/`BreadcrumbList`. No `LodgingBusiness`, ratings, FAQ or offers.
- **Time-bound posts:** month/year slugs (e.g. June/July 2026 availability) will go stale — keep URLs, refresh or consolidate later.

## Business facts captured (from `/facilities/`)

2026 rates for the whole lodge (max 10 guests): low season Mon–Thu **R11 950/night**, Fri–Sun **R14 550/night**; peak season (long weekends & school holidays) **R14 550/night**. R5 000 refundable breakage deposit; 50% deposit within 24h, balance 60 days before arrival. Game drive **R2 000 per drive** for up to 10 people (book 3 days ahead; 07:00 or 16:00, ~3 h). Mjejane conservation fee R350/vehicle + R60/guest/night (card only).

## Migration rules

1. Every `KEEP` URL is rebuilt at the **identical path, trailing slash included**. No redirect needed.
2. `PROPOSED 301` / `KEEP (review)` items are only redirected or noindexed **after** Google Search Console confirms they carry no meaningful traffic or links.
3. Carry over any existing redirect rules (Yoast Premium / Redirection plugin) — not visible from outside; request an export.
4. Launch with the same `robots.txt` behaviour and an XML sitemap listing the same URLs.

## Still needed

- Google Search Console Performance export (12 months, queries + pages) to confirm which URLs earn traffic.
- Export of any existing WordPress redirect rules.
- Decision on platform (WordPress theme rebuild vs static) — determines how the 137 posts migrate.
