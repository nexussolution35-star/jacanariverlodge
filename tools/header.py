#!/usr/bin/env python3
"""Write the shared header (floating nav) into every page (run from the repo root).
Links are root-relative and match the live jacanariverlodge.com URLs."""
import html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from silo_map import PAGES, MENU, MENU_LINKS, silo_of

HUB_LABEL = {'Stay': 'The Lodge', 'Activities': 'All Activities', 'Mjejane Reserve': 'Mjejane Reserve Guide'}


def header(url):
    def link(u, label, indent):
        cur = ' aria-current="page"' if u == url else ''
        return f'{indent}<a href="{u}"{cur}>{label}</a>'

    items = []
    for label, hub, groups in MENU:
        silo = silo_of(hub)
        on = silo_of(url) == silo and url != '/'
        ind = ' ' * 10
        rows = []
        multi = len(groups) > 1
        if multi:   # "All Activities" sits above the columns
            rows.append(link(hub, f'<strong>{HUB_LABEL[label]}</strong>', ind))
        for heading, urls in groups:
            g = []
            for u in urls:
                name = html.escape(PAGES[u][0], quote=False)
                if u == hub: name = f'<strong>{HUB_LABEL[label]}</strong>'
                g.append(link(u, name, ind + ('  ' if multi else '')))
            if multi:
                rows.append(f'{ind}<div class="nav-dd__group"><span class="nav-dd__label">{heading}</span>\n' + "\n".join(g) + f'\n{ind}</div>')
            else:
                rows += g
        cls = 'nav-dd__menu' + (' nav-dd__menu--cols' if multi else '')
        items.append(f'''      <div class="nav-dd">
        <a href="{hub}" class="nav-dd__toggle{' active' if on else ''}" aria-haspopup="true" aria-expanded="false"{' aria-current="page"' if url == hub else ''}>{label} <span class="caret" aria-hidden="true">&#9662;</span></a>
        <div class="{cls}">
{chr(10).join(rows)}
        </div>
      </div>''')
    for label, u in MENU_LINKS:
        cur = ' class="active" aria-current="page"' if u == url else ''
        items.append(f'      <a href="{u}"{cur}>{label}</a>')
    nav = "\n".join(items)
    cur = lambda u: ' aria-current="page"' if u == url else ''
    return f'''<header class="site-header" id="siteHeader">
  <div class="nav-shell">
    <div class="nav-bg" aria-hidden="true"><span class="nav-bg__bar"></span><span class="nav-bg__tab"></span></div>
    <a class="brand" href="/" aria-label="Jacana River Lodge — home">
      <img src="/assets/images/logo-640.png" alt="Jacana River Lodge, 5-star graded" width="640" height="522">
    </a>
    <nav class="nav" id="nav" aria-label="Main">
{nav}
    </nav>
    <div class="header-cta">
      <a class="btn btn--book" href="/book-now/"{cur('/book-now/')}>Book Now</a>
      <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>'''

def pages():
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules')]
        if 'index.html' in files:
            p = os.path.join(root, 'index.html')
            url = '/' if root == '.' else '/' + root[2:] + '/'
            yield p, url

if __name__ == '__main__':
    n = 0
    for p, url in pages():
        t = open(p).read()
        if '<header class="site-header"' not in t: continue
        a = t.index('<header class="site-header"'); b = t.index('</header>', a) + len('</header>')
        t2 = t[:a] + header(url) + t[b:]
        if t2 != t: open(p, 'w').write(t2); n += 1
    print('headers written:', n)
