"""Migrate the WordPress blog (WXR export) into the static site.
usage: python3 -I blog.py <export.xml> <repo root>
 - every published post at its live path /<slug>/index.html, original publish date, featured image hero
 - media (images, pdf, mp4) from /wp-content/uploads/ copied to /assets/blog/<yyyy>/<mm>/<file>
 - every link to jacanariverlodge.com (incl. /yyyy/mm/dd/slug/, old slugs, uploads) made internal
 - /news/ lists every post, newest first
 - _redirects + seo/redirects.csv: old slugs, date permalinks, tags, categories, author, feeds, uploads
"""
import sys, os, re, html, json, csv, subprocess, datetime, io
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup, Comment

SRC, ROOT = sys.argv[1], sys.argv[2]
NS = {'wp': 'http://wordpress.org/export/1.2/', 'content': 'http://purl.org/rss/1.0/modules/content/',
      'excerpt': 'http://wordpress.org/export/1.2/excerpt/', 'dc': 'http://purl.org/dc/elements/1.1/'}
DOM = re.compile(r'^https?://(?:www\.)?jacanariverlodge\.com', re.I)
ch = ET.parse(SRC).getroot().find('channel')
items = ch.findall('item')
T = lambda i, k: i.findtext(k, namespaces=NS) or ''
meta = lambda i: {m.findtext('wp:meta_key', namespaces=NS): m.findtext('wp:meta_value', namespaces=NS) or '' for m in i.findall('wp:postmeta', namespaces=NS)}
authors = {a.findtext('wp:author_login', namespaces=NS): a.findtext('wp:author_display_name', namespaces=NS) for a in ch.findall('wp:author', namespaces=NS)}
att = {T(i, 'wp:post_id'): T(i, 'wp:attachment_url') for i in items if T(i, 'wp:post_type') == 'attachment'}
allposts = [i for i in items if T(i, 'wp:post_type') == 'post']
posts = [i for i in allposts if T(i, 'wp:status') == 'publish']
skipped = [(T(i, 'wp:status'), T(i, 'wp:post_date'), T(i, 'title')) for i in allposts if T(i, 'wp:status') != 'publish']
slugs = {T(p, 'wp:post_name') for p in posts}
unpublished = {T(i, 'wp:post_name') for i in allposts if T(i, 'wp:status') != 'publish'}
# pages of the new site (tracked in git, not the generated posts): a post never overwrites one
site_paths = {('/' if os.path.dirname(f) == '' else '/' + os.path.dirname(f) + '/')
              for f in subprocess.run(['git', 'ls-files', '*index.html'], cwd=ROOT, capture_output=True, text=True).stdout.split()}
# posts migrated on an earlier run are tracked too: they are not pages
if os.path.exists(os.path.join(ROOT, 'seo/blog-posts.json')):
    site_paths -= {'/' + x['slug'] + '/' for x in json.load(open(os.path.join(ROOT, 'seo/blog-posts.json')))}
collide = [T(p, 'wp:post_name') for p in posts if '/' + T(p, 'wp:post_name') + '/' in site_paths]
posts = [p for p in posts if '/' + T(p, 'wp:post_name') + '/' not in site_paths]
slugs = {T(p, 'wp:post_name') for p in posts}

# ---------- old slug / date permalink redirects ----------
old_slug = {}
for p in posts:
    for m in p.findall('wp:postmeta', namespaces=NS):
        if m.findtext('wp:meta_key', namespaces=NS) == '_wp_old_slug':
            o = m.findtext('wp:meta_value', namespaces=NS)
            if o and o not in slugs and '/' + o + '/' not in site_paths:
                old_slug[o] = T(p, 'wp:post_name')

# ---------- media ----------
media = {}  # old absolute url -> local path

def local_media(u):
    u = DOM.sub('https://jacanariverlodge.com', u.split('?')[0])
    m = re.search(r'/wp-content/uploads/(\d{4})/(\d{2})/([^/]+)$', u)
    if not m: return None
    lp = f'/assets/blog/{m.group(1)}/{m.group(2)}/{m.group(3)}'
    media[u] = lp
    return lp

def fetch(item):
    u, lp = item
    dst = ROOT + lp
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return u, 'cached'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    r = subprocess.run(['curl', '-sSfL', '--max-time', '180', '-o', dst, u], capture_output=True)
    if r.returncode != 0:
        if os.path.exists(dst): os.remove(dst)
        return u, 'FAILED ' + r.stderr.decode()[:80]
    if dst.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        try:
            from PIL import Image
            im = Image.open(dst)
            if im.width > 1600:
                im = im.convert('RGB') if dst.lower().endswith(('.jpg', '.jpeg')) else im
                im.thumbnail((1600, 1600 * im.height // im.width))
                im.save(dst, quality=82, optimize=True, progressive=True) if dst.lower().endswith(('.jpg', '.jpeg')) else im.save(dst, optimize=True)
        except Exception as e:
            return u, 'saved (not resized: %s)' % e
    return u, 'ok'

# ---------- link rewriting ----------
def map_href(h):
    if not DOM.match(h): return h
    path = DOM.sub('', h) or '/'
    frag = ''
    if '#' in path: path, frag = path.split('#', 1); frag = '#' + frag
    path = path.split('?')[0]
    if path.startswith('/wp-content/uploads/'):
        return (local_media('https://jacanariverlodge.com' + path) or path) + frag
    if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]: path += '/'
    m = re.match(r'^/\d{4}/\d{2}/\d{2}/([^/]+)/$', path)
    if m: path = '/' + m.group(1) + '/'
    s = path.strip('/')
    if s in old_slug: path = '/' + old_slug[s] + '/'
    if s in unpublished: path = '/news/'
    if re.match(r'^/(tag|category|author)/', path) or re.match(r'^/news/page/', path): path = '/news/'
    return path + frag

def clean(content, title):
    content = re.sub(r'\[/?[a-z_]+[^\]]*\]', '', content)  # stray shortcodes
    # BeTheme builder settings that leak into the rendered copy as bare text (background, image size/align, image title)
    content = re.sub(r'(?m)^\s*no-repeat;[^\n<]*\n\s*(?:auto|cover|contain)?\s*$', '', content)
    content = re.sub(r'(?m)^\s*\d{2,4}\s*\n\s*\n?\s*\d{2,4}\s*\n\s*\n?\s*(?:center|left|right)\s*\n(?:\s*\n)?(?:(?!\s*Image)\s*[^\n<]{1,90}\n)?', '', content)
    content = re.sub(r'Image S[oO]urce:\s*(?=Image S[oO]urce:)', '', content)
    content = re.sub(r'(?:<center>)?\s*Image S[oO]urce:\s*(?:</center>)', '', content)
    content = re.sub(r'(?m)^\s*Image S[oO]urce:\s*$', '', content)
    content = re.sub(r'(?m)^\s*(?:center|left|right|auto|\d{2,4})\s*$', '', content)
    s = BeautifulSoup(content, 'html.parser')
    for c in s.find_all(string=lambda x: isinstance(x, Comment)): c.extract()
    for t in s.find_all(['script', 'style', 'noscript', 'form', 'input', 'button']): t.decompose()
    for t in s.find_all(['article', 'main', 'section', 'header', 'footer', 'aside', 'nav', 'center', 'html', 'body', 'span', 'font']): t.unwrap()
    norm = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    first = s.find(['h1', 'h2'])
    if first and norm(first.get_text()) and (norm(first.get_text()) in norm(title) or norm(title) in norm(first.get_text())):
        first.decompose()
    for h in s.find_all('h1'): h.name = 'h2'
    for img in s.find_all('img'):
        src = img.get('src', '')
        if DOM.match(src):
            lp = local_media(src)
            if lp: img['src'] = lp
        for a in ('srcset', 'sizes', 'class', 'style'): img.attrs.pop(a, None)
        img['loading'] = 'lazy'; img['decoding'] = 'async'
        if not img.get('alt'): img['alt'] = ''
    for v in s.find_all(['video', 'source']):
        if v.get('src') and DOM.match(v['src']):
            lp = local_media(v['src'])
            if lp: v['src'] = lp
    for a in s.find_all('a', href=True):
        a['href'] = map_href(a['href'])
        if a['href'].startswith('/'):
            a.attrs.pop('target', None)
            if a.get('rel'): a.attrs.pop('rel', None)
        elif a['href'].startswith('http'):
            a['target'] = '_blank'; a['rel'] = 'noopener'
    for f in s.find_all('iframe'):
        f['loading'] = 'lazy'
        w = s.new_tag('div', attrs={'class': 'post-embed'}); f.wrap(w)
    for p in s.find_all('p'):
        if not p.get_text(strip=True) and not p.find(['img', 'iframe', 'video']): p.decompose()
    for el in s.find_all(True):
        if el.name not in ('a', 'img', 'iframe', 'video', 'source', 'td', 'th', 'ol'):
            el.attrs.pop('style', None)
    return str(s).strip()

# ---------- build post data ----------
data = []
for p in posts:
    m = meta(p)
    slug = T(p, 'wp:post_name'); title = html.unescape(T(p, 'title'))
    d = datetime.datetime.strptime(T(p, 'wp:post_date'), '%Y-%m-%d %H:%M:%S')
    mod = T(p, 'wp:post_modified') or T(p, 'wp:post_date')
    thumb = att.get(m.get('_thumbnail_id', ''), '')
    hero = local_media(thumb) if thumb else None
    raw = T(p, 'content:encoded')
    if len(raw.strip()) < 200:  # BeTheme page-builder posts keep their rendered HTML here
        raw = m.get('mfn-page-items-seo', '') or raw
    body = clean(raw, title)
    desc = m.get('_yoast_wpseo_metadesc', '').strip() or html.unescape(T(p, 'excerpt:encoded')).strip()
    if not desc:
        txt = re.sub(r'\s+', ' ', BeautifulSoup(body, 'html.parser').get_text(' ')).strip()
        desc = txt[:155].rsplit(' ', 1)[0] + '…'
    cats = [c.get('nicename') for c in p.findall('category') if c.get('domain') == 'category']
    data.append(dict(slug=slug, title=title, date=d, modified=mod, hero=hero, body=body, desc=desc, cats=cats,
                     author=authors.get(T(p, 'dc:creator'), 'Jacana River Lodge')))
data.sort(key=lambda x: x['date'], reverse=True)

# ---------- download ----------
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(fetch, sorted(media.items())))
fails = [r for r in res if r[1].startswith('FAILED')]
print('media', len(media), 'failed', len(fails))
for f in fails: print('  ', f)
failed_urls = {u for u, _ in fails}
FALLBACK_HERO = '/assets/images/jacana-river-lodge-infinity-pool.jpg'
for x in data:
    if x['hero'] and not os.path.exists(ROOT + x['hero']): x['hero'] = None

# ---------- page shell ----------
news = open(os.path.join(ROOT, 'news/index.html')).read()
HEAD_END = news.index('</head>')
shell_head = news[:HEAD_END]
shell_mid = news[HEAD_END:news.index('<main id="main">')]
shell_tail = news[news.index('</main>'):]
home = open(os.path.join(ROOT, 'index.html')).read()
ENQ = re.search(r'<!-- ============ ENQUIRY.*?\n</section>', home, re.S).group(0)
E = lambda s: html.escape(s, quote=True)
fmt = lambda d: f'{d.day} {d.strftime("%B %Y")}'
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'
inv = {r['path']: r for r in csv.DictReader(open(os.path.join(ROOT, 'seo/url-inventory.csv')))}

def head_for(x):
    url = '/' + x['slug'] + '/'
    title = inv.get(url, {}).get('title') or f"{x['title']} - Jacana River Lodge"
    h = shell_head
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(x["desc"])}">', h)
    h = re.sub(r'<script type="application/ld\+json" id="ld-breadcrumb">.*?</script>\n?', '', h, flags=re.S)
    h = re.sub(r'<link rel="canonical"[^>]*>\n?', '', h)
    h = re.sub(r'<meta property="og:(url|image|title|description)"[^>]*>\n?', '', h)
    img = 'https://jacanariverlodge.com' + (x['hero'] or FALLBACK_HERO)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BlogPosting', 'headline': x['title'], 'description': x['desc'], 'image': img,
         'datePublished': x['date'].strftime('%Y-%m-%dT%H:%M:%S+02:00'),
         'dateModified': x['modified'].replace(' ', 'T') + '+02:00',
         'author': {'@type': 'Person', 'name': x['author']},
         'publisher': {'@type': 'Organization', 'name': 'Jacana River Lodge'},
         'mainEntityOfPage': 'https://jacanariverlodge.com' + url},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': 'https://jacanariverlodge.com/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'News', 'item': 'https://jacanariverlodge.com/news/'},
            {'@type': 'ListItem', 'position': 3, 'name': x['title'], 'item': 'https://jacanariverlodge.com' + url}]}]}
    h += (f'<meta property="og:type" content="article">\n'
          f'<meta property="og:image" content="{img}">\n'
          f'<meta property="article:published_time" content="{x["date"].strftime("%Y-%m-%dT%H:%M:%S+02:00")}">\n'
          f'<meta property="article:modified_time" content="{x["modified"].replace(" ", "T")}+02:00">\n'
          f'<script type="application/ld+json" id="ld-post">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    return h

def card(x, tag='article'):
    url = '/' + x['slug'] + '/'
    img = x['hero'] or FALLBACK_HERO
    return (f'''      <article class="story-card">
        <a class="story-card__img" href="{url}" tabindex="-1" aria-hidden="true"><img loading="lazy" decoding="async" src="{img}" alt=""></a>
        <div class="story-card__body">
          <span class="story-card__tag"><time datetime="{x['date']:%Y-%m-%d}">{fmt(x['date'])}</time></span>
          <h2><a href="{url}">{E(x['title'])}</a></h2>
          <p>{E(x['desc'])}</p>
          <a class="more" href="{url}">Read more &rarr;<span class="sr-only">: {E(x['title'])}</span></a>
        </div>
      </article>''')

def related(x):
    pool = [y for y in data if y is not x]
    same = [y for y in pool if set(y['cats']) & set(x['cats'])] or pool
    same.sort(key=lambda y: abs((y['date'] - x['date']).days))
    return same[:3]

for x in data:
    url = '/' + x['slug'] + '/'
    hero = x['hero'] or FALLBACK_HERO
    short = x['title'] if len(x['title']) < 60 else x['title'][:57].rsplit(' ', 1)[0] + '…'
    main = f'''<main id="main">
<section class="page-hero page-hero--post" style="background-image:url('{hero}')">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span>&rsaquo;</span> <a href="/news/">News</a> <span>&rsaquo;</span> <em aria-current="page">{E(short)}</em></nav>
    <span class="eyebrow"><time datetime="{x['date']:%Y-%m-%d}">{fmt(x['date'])}</time></span>
    <h1>{E(x['title'])}</h1>
  </div>
</section>

<section class="section section--cream post">
  <div class="container">
    <article class="post-body">
      <p class="post-meta">Published <time datetime="{x['date']:%Y-%m-%d}">{fmt(x['date'])}</time> &middot; {E(x['author'])}</p>
{x['body']}
    </article>
  </div>
</section>

<section class="section section--sand post-more" aria-labelledby="moreTitle">
  <div class="container">
    <div class="sec-head"><p class="sec-eyebrow">The Jacana Journal</p><h2 class="sec-title" id="moreTitle">Keep Reading</h2></div>
    <div class="stories__grid">
{chr(10).join(card(y) for y in related(x))}
    </div>
    <p class="center post-all"><a class="btn" href="/news/">All articles</a></p>
  </div>
</section>

{ENQ}
'''
    assert '/' + x['slug'] + '/' not in site_paths, x['slug']
    os.makedirs(os.path.join(ROOT, x['slug']), exist_ok=True)
    open(os.path.join(ROOT, x['slug'], 'index.html'), 'w').write(head_for(x) + shell_mid + main + shell_tail)

# ---------- news index ----------
cards = '\n'.join(card(x) for x in data)
a = re.search(r'<div class="stories__grid[^"]*"', news).start(); b = news.index('</section>', a)
grid = f'''<div class="stories__grid news-grid" id="newsGrid">
{cards}
    </div>
    <p class="center news-more-wrap"><button class="btn" type="button" id="newsMore">Show more articles</button></p>
  </div>
'''
news2 = news[:a] + grid + news[b:]
news2 = re.sub(r'\s*<a class="btn[^"]*"[^>]*>Older Articles</a>', '', news2)
open(os.path.join(ROOT, 'news/index.html'), 'w').write(news2)

# ---------- redirects ----------
rows = []
for o, n in sorted(old_slug.items()): rows.append((f'/{o}/', f'/{n}/', 'old post slug'))
for x in data: rows.append((f'/{x["date"]:%Y/%m/%d}/{x["slug"]}/', f'/{x["slug"]}/', 'old date permalink'))
for s in sorted(unpublished - slugs):
    if s: rows.append((f'/{s}/', '/news/', 'post not published'))
tags = sorted({c.get('nicename') for i in allposts for c in i.findall('category') if c.get('domain') == 'post_tag'})
cats = sorted({c.get('nicename') for i in allposts for c in i.findall('category') if c.get('domain') == 'category'})
for t in tags: rows.append((f'/tag/{t}/', '/news/', 'tag archive'))
for c in cats: rows.append((f'/category/{c}/', '/news/', 'category archive'))
for a_ in authors: rows.append((f"/author/{re.sub(r'[^a-z0-9]+', '-', a_.lower()).strip('-')}/", '/news/', 'author archive'))
for p in inv:
    if p.startswith('/author/') and (p, '/news/', 'author archive') not in rows: rows.append((p, '/news/', 'author archive'))
rows += [('/news/page/*', '/news/', 'blog pagination'), ('/feed/', '/news/', 'RSS feed'), ('/comments/feed/', '/news/', 'RSS feed'),
         ('/activities/', '/activities-near-mjejane/', 'duplicate of the Activities page')]
for u, lp in sorted(media.items()):
    if u not in failed_urls: rows.append((DOM.sub('', u), lp, 'blog media'))
seen, out = set(), []
for r in rows:
    if r[0] in seen or r[0] == r[1]: continue
    seen.add(r[0]); out.append(r)
with open(os.path.join(ROOT, '_redirects'), 'w') as f:
    f.write('# 301 redirects for the launch (old WordPress URLs -> new site). Format: from to status\n')
    for fr, to, _ in out: f.write(f'{fr} {to} 301\n')
with open(os.path.join(ROOT, 'seo/redirects.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['from', 'to', 'reason']); w.writerows(out)
json.dump([{'slug': x['slug'], 'date': x['date'].isoformat(), 'modified': x['modified']} for x in data],
          open(os.path.join(ROOT, 'seo/blog-posts.json'), 'w'), indent=1)
print('posts', len(data), 'redirects', len(out))
print('skipped (not published):', skipped)
print('skipped (a page of the new site uses this address):', collide)
