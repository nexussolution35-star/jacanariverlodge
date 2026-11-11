#!/usr/bin/env python3
"""SEO pass over every page (run from the repo root, after header.py/footer.py).

For each folder/index.html page:
  * pages that replace a live URL get the live <title> and meta description
    (from seo/url-inventory.csv), except where TITLE_/META_OVERRIDES carry an
    approved SEO-spec change; new pages keep the title/description in their own <head>;
  * every page gets a self-referencing canonical on https://jacanariverlodge.com
    plus og:url / og:title / og:description and an absolute og:image;
  * /activities/ (a live duplicate of /activities-near-mjejane/) is copied from the hub;
  * absolute links to live URLs that exist in this build are made root-relative;
  * sitemap_index.xml + page-sitemap.xml list every page in this build (same names as Yoast);
  * twitter:card on every page, one <main> landmark per page, LodgingBusiness schema on Home + Contact;
  * /activities/ keeps working but canonicals to the Activities hub (CANONICAL_TO).
"""
import csv, html, json, os, re, shutil

DOMAIN = 'https://jacanariverlodge.com'
SKIP = {'.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules'}
inv = {r['path']: r for r in csv.DictReader(open('seo/url-inventory.csv'))}

# SEO decisions that deliberately replace a live value.
# Approved in "SEO Spec, Part 1: Home & Stay" (seo/Jacana-SEO-Plan-Part-1-Home-and-Stay.pdf).
# Pages not listed here keep their live title and description word for word.
TITLE_OVERRIDES = {
    '/': 'Jacana River Lodge | Kruger Park Lodge in Mpumalanga',
    '/luxury-self-catering-lodge-accommodation-in-mpumalanga/': 'Self-Catering Lodge in Mpumalanga | Jacana River Lodge',
    '/self-catering-getaway-in-mpumalanga/': 'Bush Getaway in Mpumalanga | Jacana River Lodge',
    '/mjejane-accommodation-specials/': 'Mjejane Accommodation Specials | Jacana River Lodge',
}
META_OVERRIDES = {
    '/': 'Exclusive-use, 5-star self-catering safari lodge on the Crocodile River in the Mjejane Game Reserve, Greater Kruger. Sleeps 10. Book direct.',
    '/luxury-self-catering-lodge-accommodation-in-mpumalanga/': 'A private 5-star self-catering lodge in the Mjejane Game Reserve, Mpumalanga, with 5 king en-suite rooms, an infinity pool and Crocodile River views.',
    '/facilities/': '2026 rates for Jacana River Lodge, a self-catering lodge near the Kruger National Park: from R11 950 a night for the whole lodge, up to 10 guests.',
    '/self-catering-getaway-in-mpumalanga/': 'Plan a bush getaway in Mpumalanga at Jacana River Lodge: a private self-catering lodge for up to 10 on the Crocodile River, 4 hours from Johannesburg.',
    # live page reused /book-now/'s description word for word
    '/mjejane-accommodation-specials/': 'Low-season special at Jacana River Lodge: stay 3 nights and get the 4th night at 50% off at our 5-star self-catering lodge in the Mjejane Game Reserve.',
}
for _d in (TITLE_OVERRIDES, META_OVERRIDES):
    for _u, _v in _d.items():
        assert len(_v) <= (60 if _d is TITLE_OVERRIDES else 160), (_u, len(_v))

# /activities/ is the live site's older copy of the Activities hub (5 internal links point at it,
# last edited 2021). The URL keeps working, but its canonical points at the hub so Google ranks one
# page, and it leaves the sitemap. At the Lovable launch it becomes a 301 to the hub.
CANONICAL_TO = {'/activities/': '/activities-near-mjejane/'}
os.makedirs('activities', exist_ok=True)
shutil.copyfile('activities-near-mjejane/index.html', 'activities/index.html')


# LodgingBusiness schema for Home and Contact. Facts only from the site; no review stars
# (Google ignores self-published ratings and can penalise them). Geo left out until we have the
# exact pin from the Google Business Profile, not the map embed's centre.
LODGE_SCHEMA_ON = {'/', '/contact-us/'}
LODGE = {
    '@context': 'https://schema.org', '@type': 'LodgingBusiness', '@id': DOMAIN + '/#lodge',
    'name': 'Jacana River Lodge', 'url': DOMAIN + '/',
    'description': 'Exclusive-use, 5-star self-catering lodge for up to 10 guests in five en-suite king rooms, '
                   'on the Crocodile River in the Mjejane Private Game Reserve on the Kruger National Park\'s southern boundary.',
    'logo': DOMAIN + '/assets/images/logo-640.png',
    'image': DOMAIN + '/assets/images/Jacana-River-Lodge-c6d2d807.jpg',
    'telephone': '+27 66 293 7100', 'email': 'info@jacanariverlodge.com',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Hectorspruit', 'addressRegion': 'Mpumalanga',
                'streetAddress': 'Mjejane Private Game Reserve', 'addressCountry': 'ZA'},
    'hasMap': 'https://g.page/jacana-river-lodge?share',
    'priceRange': 'From R11 950 per night for the whole lodge',
    'currenciesAccepted': 'ZAR',
    'numberOfRooms': 5,
    'starRating': {'@type': 'Rating', 'ratingValue': '5', 'author': {'@type': 'Organization', 'name': 'Tourism Grading Council of South Africa'}},
    'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': n, 'value': True} for n in
                       ['Infinity pool', 'Self-catering kitchen', 'Air-conditioning', 'Wheelchair-friendly room', 'Braai area', 'Boma']],
    'sameAs': ['https://www.facebook.com/jacanariverlodge/', 'https://www.instagram.com/jacana_river_lodge/',
               'https://www.youtube.com/@jacanariverlodge9550',
               'https://www.tripadvisor.co.za/VacationRentalReview-g657276-d19114871-Jacana_River_Lodge-Hectorspruit_Mpumalanga.html',
               'https://g.page/jacana-river-lodge?share'],
}


def pages():
    for root, dirs, files in os.walk('.'):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        if 'index.html' in files:
            yield os.path.join(root, 'index.html'), ('/' if root == '.' else '/' + root[2:] + '/')


def attr(s):
    return html.escape(html.unescape(s), quote=True)


def set_tag(head, pattern, tag):
    """Replace the first tag matching pattern, or append it before </head>."""
    if re.search(pattern, head):
        return re.sub(pattern, lambda m: tag, head, count=1)
    return head.replace('</head>', tag + '\n</head>', 1)


urls = []
for path, url in pages():
    t = open(path).read()
    a = t.index('<head>'); b = t.index('</head>') + len('</head>')
    head = t[a:b]
    live = inv.get(url)
    new_title = TITLE_OVERRIDES.get(url) or (live and live['title'])
    if new_title:
        head = re.sub(r'<title>.*?</title>', '<title>' + attr(new_title) + '</title>', head, count=1, flags=re.S)
    if url in META_OVERRIDES:
        head = set_tag(head, r'<meta name="description" content="[^"]*">',
                       '<meta name="description" content="' + attr(META_OVERRIDES[url]) + '">')
    elif live and live['meta_description']:
        head = set_tag(head, r'<meta name="description" content="[^"]*">',
                       '<meta name="description" content="' + attr(live['meta_description']) + '">')
    title = html.unescape(re.search(r'<title>(.*?)</title>', head, re.S).group(1))
    m = re.search(r'<meta name="description" content="([^"]*)">', head)
    desc = html.unescape(m.group(1)) if m else ''
    canon = CANONICAL_TO.get(url, url)
    head = set_tag(head, r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{DOMAIN}{canon}">')
    head = set_tag(head, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{DOMAIN}{canon}">')
    head = set_tag(head, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + attr(title) + '">')
    if desc:
        head = set_tag(head, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + attr(desc) + '">')
    head = re.sub(r'(<meta property="og:image" content=")/', r'\g<1>' + DOMAIN + '/', head)
    # X/Twitter reads the og: tags for title, description and image; it only needs the card type
    head = set_tag(head, r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary_large_image">')
    if url in LODGE_SCHEMA_ON:
        ld = '<script type="application/ld+json" id="ld-lodge">' + json.dumps(LODGE, ensure_ascii=False) + '</script>'
        head = (re.sub(r'<script type="application/ld\+json" id="ld-lodge">.*?</script>', lambda m: ld, head, count=1, flags=re.S)
                if 'id="ld-lodge"' in head else head.replace('</head>', ld + '\n</head>', 1))
    # body links to live URLs that now exist in this build become root-relative
    rest = re.sub(r'href="' + re.escape(DOMAIN) + r'(/[^"#?]*)([^"]*)"',
                  lambda m: f'href="{m.group(1)}{m.group(2)}"' if os.path.exists('.' + m.group(1).rstrip('/') + '/index.html') else m.group(0),
                  t[b:])
    # one <main> landmark: everything between the site header and the footer
    if '<main' not in rest and '</header>' in rest and '<footer class="footer"' in rest:
        rest = rest.replace('</header>', '</header>\n<main id="main">', 1)
        rest = rest.replace('<footer class="footer"', '</main>\n<footer class="footer"', 1)
    t2 = t[:a] + head + rest
    if t2 != t:
        open(path, 'w').write(t2)
    noindex = re.search(r'<meta name="robots" content="[^"]*noindex', head)
    if not noindex and url not in CANONICAL_TO:
        urls.append(url)

# same file names as the live Yoast setup, so Search Console's registered sitemap keeps working
with open('page-sitemap.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in sorted(urls, key=lambda u: (u != '/', u)):
        f.write(f'  <url><loc>{DOMAIN}{u}</loc></url>\n')
    f.write('</urlset>\n')
with open('sitemap_index.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'  <sitemap><loc>{DOMAIN}/page-sitemap.xml</loc></sitemap>\n</sitemapindex>\n')
print('pages:', len(urls), '| live titles kept:', sum(1 for u in urls if u in inv and u not in TITLE_OVERRIDES), '| spec titles:', len(TITLE_OVERRIDES))
