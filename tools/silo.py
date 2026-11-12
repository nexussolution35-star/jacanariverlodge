#!/usr/bin/env python3
"""Silo pass (run from the repo root, after header.py/footer.py, before seo.py).

From tools/silo_map.py, for every page:
  * the hero breadcrumb (<nav class="crumbs">) becomes Home > hub > ... > page;
  * a BreadcrumbList JSON-LD that mirrors the visible breadcrumb;
  * a "more in this section" block before the footer: the page's children,
    its siblings and the way up to its hub. Links never cross silos.
    Plan-your-stay pages (Book Now, Contact, Directions, FAQ) link each other.
The block sits between <!-- SILO --> and <!-- /SILO --> so reruns replace it.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from silo_map import PAGES, SILOS, PLAN, chain, children

DOMAIN = 'https://jacanariverlodge.com'
SKIP = {'.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules'}
NO_BLOCK = {'/', '/news/', '/backlinks/', '/cookies-and-privacy-policy/', '/thank-you/',
            '/thank-you-for-your-booking-enquiry/', '/activities/'}
HEADS = {'stay': ('More about your stay', 'Explore the lodge'),
         'act': ('More things to do', 'Explore the activities'),
         'res': ('More about the reserve', 'Explore the Mjejane'),
         None: ('Plan your stay', 'Everything you need to book')}
E = lambda s: html.escape(s, quote=False)


def pages():
    for root, dirs, files in os.walk('.'):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        if 'index.html' in files:
            yield os.path.join(root, 'index.html'), ('/' if root == '.' else '/' + root[2:] + '/')


def built(u):
    return os.path.exists('.' + u + 'index.html')


def crumbs(url):
    trail = ['/'] + list(reversed(chain(url))) if url != '/' else ['/']
    if url == '/activities/':
        trail = ['/', '/activities/']
    return [u for u in trail if u == url or built(u)]


def crumb_html(trail):
    parts = []
    for u in trail[:-1]:
        parts.append(f'<a href="{u}">{E(PAGES[u][0])}</a>')
    parts.append(f'<em aria-current="page">{E(PAGES[trail[-1]][0])}</em>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span>&rsaquo;</span> '.join(parts) + '</nav>'


def crumb_ld(trail):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': PAGES[u][0], 'item': DOMAIN + u}
        for i, u in enumerate(trail)]}


def related(url):
    """The way up (hub, sub-hub), then children, then siblings. Same silo only."""
    label, parent, silo, _ = PAGES[url]
    if silo is None:
        return [u for u in PLAN if u != url]
    out = [u for u in reversed(chain(parent))] if parent else []   # the way up first: hub, then sub-hub
    out += children(url)
    if parent and not url.startswith('/testimonial-item/'):   # the 8 review pages link up, not to each other
        out += [u for u in children(parent) if u != url]
    seen, res = set(), []
    for u in out:
        if u in seen or u == url or not built(u) or PAGES[u][2] != silo:
            continue
        seen.add(u); res.append(u)
    return res[:12]


def block(url):
    links = related(url)
    if not links:
        return ''
    silo = PAGES[url][2]
    eyebrow, h2 = HEADS[silo]
    ups = set(chain(PAGES[url][1])) if PAGES[url][1] else set()
    cards = []
    for u in links:
        name, _, _, blurb = PAGES[u]
        tag = ''
        if u in ups:
            tag = '<span class="silo__tag">Overview</span>'
        text = f'<span class="silo__text">{E(blurb)}</span>' if blurb else ''
        cards.append(f'      <li><a class="silo__card" href="{u}">{tag}<span class="silo__title">{E(name)}</span>{text}</a></li>')
    return f'''<!-- SILO -->
<section class="section section--sand silo" aria-labelledby="silo-h">
  <div class="container">
    <div class="silo__head"><span class="eyebrow">{eyebrow}</span><h2 id="silo-h">{h2}</h2></div>
    <ul class="silo__grid">
{chr(10).join(cards)}
    </ul>
  </div>
</section>
<!-- /SILO -->
'''


missing_crumbs, unmapped, n = [], [], 0
for path, url in pages():
    if url not in PAGES:
        unmapped.append(url); continue
    t = open(path).read()
    t0 = t
    # 1. visible breadcrumb
    if url != '/':
        trail = crumbs(url)
        if re.search(r'<nav class="crumbs"[^>]*>.*?</nav>', t, re.S):
            t = re.sub(r'<nav class="crumbs"[^>]*>.*?</nav>', lambda m: crumb_html(trail), t, count=1, flags=re.S)
        else:
            missing_crumbs.append(url)
        # 2. BreadcrumbList JSON-LD mirroring it
        ld = '<script type="application/ld+json" id="ld-breadcrumb">' + json.dumps(crumb_ld(trail), ensure_ascii=False) + '</script>'
        if 'id="ld-breadcrumb"' in t:
            t = re.sub(r'<script type="application/ld\+json" id="ld-breadcrumb">.*?</script>', lambda m: ld, t, count=1, flags=re.S)
        else:
            t = t.replace('</head>', ld + '\n</head>', 1)
    # 3. "more in this section"
    b = '' if url in NO_BLOCK else block(url)
    if '<!-- SILO -->' in t:
        a0 = t.index('<!-- SILO -->')
        if '<!-- /SILO -->' in t:   # first opening marker to the LAST closing one, so a doubled block heals
            z = t.rindex('<!-- /SILO -->') + len('<!-- /SILO -->')
            z += 1 if t[z:z + 1] == '\n' else 0
        else:                       # bare marker left by a page author
            z = a0 + len('<!-- SILO -->')
            z += 1 if t[z:z + 1] == '\n' else 0
        t = t[:a0] + (b or '<!-- SILO -->\n') + t[z:]
    elif b:
        t = t.replace('<footer class="footer"', b + '<footer class="footer"', 1)
    if t != t0:
        open(path, 'w').write(t); n += 1

print('silo pass: pages updated', n)
if unmapped: print('NOT IN silo_map (no crumbs/block):', ', '.join(unmapped))
if missing_crumbs: print('no <nav class="crumbs"> to update:', ', '.join(missing_crumbs))
