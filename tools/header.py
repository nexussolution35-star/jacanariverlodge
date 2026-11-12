#!/usr/bin/env python3
"""Write the shared header (floating nav) into every page (run from the repo root).
Links are root-relative and match the live jacanariverlodge.com URLs."""
import html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from silo_map import PAGES, MENU, MENU_LINKS, silo_of

# Mega-menu feature card per dropdown: (title, one line, square image in assets/images)
FEATURE = {
    'Stay': ('Explore the Lodge',
             'Five en-suite king rooms, an infinity pool and the Crocodile River: the whole lodge is yours, for up to 10 guests.',
             'menu-lodge-suite.jpg'),
    'Activities': ('Explore All Activities',
                   'Game drives and bush walks in the Mjejane, plus day trips into the Kruger and along the Panorama Route.',
                   'menu-activities.jpg'),
    'Mjejane Reserve': ('Explore the Mjejane',
                        'A private Big 5 reserve on the Kruger\u2019s southern boundary, with the Crocodile River as its border.',
                        'menu-reserve-leopard.jpg'),
}


def header(url):
    def link(u, label, indent):
        cur = ' aria-current="page"' if u == url else ''
        return f'{indent}<a href="{u}"{cur}>{label}</a>'

    items = []
    for label, hub, groups in MENU:
        silo = silo_of(hub)
        on = silo_of(url) == silo and url != '/'
        ind = ' ' * 12
        f_title, f_text, f_img = FEATURE[label]
        cur_hub = ' aria-current="page"' if url == hub else ''
        # left: the hub as an image card (the page we most want clicked); right: the rest as plain links
        feature = (f'          <a class="nav-mega__feature" href="{hub}"{cur_hub}>'
                   f'<img src="/assets/images/{f_img}" alt="" width="560" height="560" loading="lazy">'
                   f'<span class="nav-mega__body"><span class="nav-mega__title">{f_title}</span>'
                   f'<span class="nav-mega__text">{f_text}</span></span></a>')
        cols = []
        for heading, urls in groups:
            g = [link(u, html.escape(PAGES[u][0], quote=False), ind + '  ') for u in urls if u != hub]
            lab = f'<span class="nav-dd__label">{heading}</span>' if heading else ''
            cols.append(f'{ind}<div class="nav-mega__group">{lab}\n' + "\n".join(g) + f'\n{ind}</div>')
        grp = ' nav-mega__links--groups' if len(groups) > 1 else ''
        items.append(f'''      <div class="nav-dd">
        <a href="{hub}" class="nav-dd__toggle{' active' if on else ''}" aria-haspopup="true" aria-expanded="false"{cur_hub}>{label} <span class="caret" aria-hidden="true">&#9662;</span></a>
        <div class="nav-dd__menu nav-mega">
{feature}
          <div class="nav-mega__links{grp}">
{chr(10).join(cols)}
          </div>
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
