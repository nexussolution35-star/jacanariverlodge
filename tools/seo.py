#!/usr/bin/env python3
"""SEO pass over every page (run from the repo root, after header.py/footer.py).

For each folder/index.html page:
  * pages that replace a live URL get the live <title> and meta description
    (from seo/url-inventory.csv) so Google sees no change in the snippet;
  * every page gets a self-referencing canonical on https://jacanariverlodge.com
    plus og:url / og:title / og:description and an absolute og:image;
  * /activities/ (a live duplicate of /activities-near-mjejane/) is copied from the hub;
  * sitemap_index.xml + page-sitemap.xml list every page in this build (same names as Yoast).
"""
import csv, html, os, re, shutil

DOMAIN = 'https://jacanariverlodge.com'
SKIP = {'.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules'}
inv = {r['path']: r for r in csv.DictReader(open('seo/url-inventory.csv'))}

# live duplicate kept at its own URL until Search Console says it can be redirected
os.makedirs('activities', exist_ok=True)
shutil.copyfile('activities-near-mjejane/index.html', 'activities/index.html')


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
    if live and live['title']:
        head = re.sub(r'<title>.*?</title>', '<title>' + attr(live['title']) + '</title>', head, count=1, flags=re.S)
    if live and live['meta_description']:
        head = set_tag(head, r'<meta name="description" content="[^"]*">',
                       '<meta name="description" content="' + attr(live['meta_description']) + '">')
    title = html.unescape(re.search(r'<title>(.*?)</title>', head, re.S).group(1))
    m = re.search(r'<meta name="description" content="([^"]*)">', head)
    desc = html.unescape(m.group(1)) if m else ''
    head = set_tag(head, r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{DOMAIN}{url}">')
    head = set_tag(head, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{DOMAIN}{url}">')
    head = set_tag(head, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + attr(title) + '">')
    if desc:
        head = set_tag(head, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + attr(desc) + '">')
    head = re.sub(r'(<meta property="og:image" content=")/', r'\g<1>' + DOMAIN + '/', head)
    t2 = t[:a] + head + t[b:]
    if t2 != t:
        open(path, 'w').write(t2)
    noindex = re.search(r'<meta name="robots" content="[^"]*noindex', head)
    if not noindex:
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
print('pages:', len(urls), '| live titles kept:', sum(1 for u in urls if u in inv))
