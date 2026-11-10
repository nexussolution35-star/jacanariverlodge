#!/usr/bin/env python3
"""Report-only SEO scorecard for the built pages (Nexus SEO checklist, stage B2).
Run from the repo root:  python3 tools/audit.py  [--json]
Nothing is changed; it prints PASS/FAIL per check with the failing pages."""
import html, json, os, re, sys

DOMAIN = 'https://jacanariverlodge.com'
SKIP = {'.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules'}
NOINDEX_EXPECTED = {'/thank-you/', '/thank-you-for-your-booking-enquiry/'}


def pages():
    for root, dirs, files in os.walk('.'):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        if 'index.html' in files:
            yield os.path.join(root, 'index.html'), ('/' if root == '.' else '/' + root[2:] + '/')


def text(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())


sitemap = set(re.findall(r'<loc>' + re.escape(DOMAIN) + r'([^<]*)</loc>', open('page-sitemap.xml').read())) if os.path.exists('page-sitemap.xml') else set()
checks = {k: [] for k in [
    'title: present + unique', 'title: <=60 chars', 'meta: present + unique', 'meta: 120-160 chars',
    'one H1', 'heading levels sequential', 'canonical == served URL', 'og:url == canonical', 'og:image absolute',
    'twitter:card', 'one <main> landmark', 'img alt present', 'no bare "Read more" links',
    'form controls have accessible names', 'schema: LodgingBusiness/LocalBusiness on home + contact',
    'schema: BreadcrumbList on deep pages', 'FAQPage only where FAQ visible', 'no AggregateRating',
    'noindex where required', 'no stray noindex', 'sitemap lists every indexable page', 'favicon declared']}
titles, metas = {}, {}
for path, url in pages():
    h = open(path).read()
    head = h[:h.find('</head>')]
    body = h[h.find('<body'):]
    t = re.search(r'<title>(.*?)</title>', head, re.S)
    t = html.unescape(t.group(1)).strip() if t else ''
    m = re.search(r'<meta name="description" content="([^"]*)"', head)
    m = html.unescape(m.group(1)) if m else ''
    noindex = bool(re.search(r'<meta name="robots" content="[^"]*noindex', head))
    titles.setdefault(t, []).append(url); metas.setdefault(m, []).append(url)
    if not t: checks['title: present + unique'].append(url)
    if len(t) > 60: checks['title: <=60 chars'].append(f'{url} ({len(t)})')
    if not m: checks['meta: present + unique'].append(url)
    elif not 120 <= len(m) <= 160: checks['meta: 120-160 chars'].append(f'{url} ({len(m)})')
    hs = [int(x) for x in re.findall(r'<h([1-6])\b', body)]
    if hs.count(1) != 1: checks['one H1'].append(f'{url} ({hs.count(1)})')
    skips = [f'h{a}>h{b}' for a, b in zip(hs, hs[1:]) if b > a + 1]
    if skips: checks['heading levels sequential'].append(f'{url} ({", ".join(sorted(set(skips)))})')
    c = re.search(r'<link rel="canonical" href="([^"]*)"', head)
    c = c.group(1) if c else ''
    if c != DOMAIN + url: checks['canonical == served URL'].append(f'{url} ({c or "missing"})')
    o = re.search(r'<meta property="og:url" content="([^"]*)"', head)
    if not o or o.group(1) != c: checks['og:url == canonical'].append(url)
    oi = re.search(r'<meta property="og:image" content="([^"]*)"', head)
    if not oi or not oi.group(1).startswith('https://'): checks['og:image absolute'].append(url)
    if 'twitter:card' not in head: checks['twitter:card'].append(url)
    if len(re.findall(r'<main\b', body)) != 1: checks['one <main> landmark'].append(url)
    imgs = re.findall(r'<img\b[^>]*>', body)
    noalt = [i for i in imgs if not re.search(r'\salt="', i)]
    if noalt: checks['img alt present'].append(f'{url} ({len(noalt)}/{len(imgs)})')
    bare = [a for a in re.findall(r'<a\b[^>]*>(.*?)</a>', body, re.S) if re.fullmatch(r'(read more|more|click here|learn more)\W*', text(a), re.I)]
    if bare: checks['no bare "Read more" links'].append(f'{url} ({len(bare)})')
    unnamed = 0
    for ctl in re.findall(r'<(?:input|select|textarea)\b[^>]*>', body):
        if re.search(r'type="(hidden|submit|button)"', ctl): continue
        idm = re.search(r'\sid="([^"]+)"', ctl)
        named = 'aria-label=' in ctl or 'aria-labelledby=' in ctl or (idm and f'for="{idm.group(1)}"' in body)
        if not named:
            # wrapped in a <label>?
            i = body.find(ctl); pre = body[:i]
            named = pre.rfind('<label') > pre.rfind('</label>')
        if not named: unnamed += 1
    if unnamed: checks['form controls have accessible names'].append(f'{url} ({unnamed})')
    ld = ' '.join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S))
    if url in ('/', '/contact-us/') and not re.search(r'"(LodgingBusiness|LocalBusiness|Hotel|Resort)"', ld):
        checks['schema: LodgingBusiness/LocalBusiness on home + contact'].append(url)
    if url != '/' and 'BreadcrumbList' not in ld: checks['schema: BreadcrumbList on deep pages'].append(url)
    if 'FAQPage' in ld and 'faq' not in body.lower(): checks['FAQPage only where FAQ visible'].append(url)
    if 'AggregateRating' in ld: checks['no AggregateRating'].append(url)
    if url in NOINDEX_EXPECTED and not noindex: checks['noindex where required'].append(url)
    if noindex and url not in NOINDEX_EXPECTED: checks['no stray noindex'].append(url)
    if not noindex and url not in sitemap: checks['sitemap lists every indexable page'].append(url)
    if 'rel="icon"' not in head: checks['favicon declared'].append(url)
for t, us in titles.items():
    if t and len(us) > 1: checks['title: present + unique'] += [f'duplicate: {", ".join(us)}']
for m, us in metas.items():
    if m and len(us) > 1: checks['meta: present + unique'] += [f'duplicate: {", ".join(us)}']

n = sum(1 for _ in pages())
if '--json' in sys.argv:
    print(json.dumps({'pages': n, 'checks': checks}, indent=1))
else:
    print(f'{n} pages')
    for k, v in checks.items():
        print(('PASS ' if not v else f'FAIL ({len(v)}) ') + k + ('' if not v else ': ' + '; '.join(v[:12]) + (' …' if len(v) > 12 else '')))
