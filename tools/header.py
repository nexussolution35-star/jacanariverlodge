#!/usr/bin/env python3
"""Write the shared header (floating nav) into every page (run from the repo root).
Links are root-relative and match the live jacanariverlodge.com URLs."""
import os

NAV = [
    ('Home', '/'),
    ('About', '/luxury-self-catering-lodge-accommodation-in-mpumalanga/'),
    ('Activities', '/activities-near-mjejane/'),          # dropdown
    ('Mjejane Reserve', '/mjejane-game-reserve-accommodation-guide/'),
    ('Gallery', '/gallery/'),
    ('Rates', '/facilities/'),
    ('Contact Us', '/contact-us/'),
]
ACTIVITIES = [
    ('All Activities', '/activities-near-mjejane/'),
    ('Private Game Drives', '/game-drive-mjejane-game-reserve/'),
    ('Kruger Drives with Ranger Special Khoza', '/kruger-private-drives-special-khoza/'),
    ('Kruger Safaris with Irving Knight', '/kruger-full-day-safari-with-irving-knight-safaris/'),
    ('Mjejane Bush Walks', '/guided-bush-walks-kruger-national-park/'),
    ('Mjejane Bush Spa', '/mjejane-mobile-bush-spa/'),
    ('Birding on the Mjejane', '/mjejane-game-reserve-birding-guide/'),
    ('Kingsland Recreational Area', '/kingsland-recreational-area/'),
    ('Wildlife &amp; Sightings', '/wildlife-and-sightings/'),
]
ACT_PATHS = {u for _, u in ACTIVITIES} | {'/activities/'}

def header(url):
    def cur(u):
        return ' class="active" aria-current="page"' if u == url else ''
    items = []
    for label, u in NAV:
        if label == 'Activities':
            on = url in ACT_PATHS
            here = ' aria-current="page"'
            sub = "\n".join(
                f'          <a href="{au}"{here if au == url else ""}>'
                + (f'<strong>{al}</strong>' if al == 'All Activities' else al) + '</a>'
                for al, au in ACTIVITIES)
            items.append(f'''      <div class="nav-dd" id="navDd">
        <a href="{u}" class="nav-dd__toggle{' active' if on else ''}"{' aria-current="page"' if url == u else ''}>Activities <span class="caret" aria-hidden="true">&#9662;</span></a>
        <div class="nav-dd__menu">
{sub}
        </div>
      </div>''')
        else:
            items.append(f'      <a href="{u}"{cur(u)}>{label}</a>')
    nav = "\n".join(items)
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
      <a class="btn btn--book" href="/book-now/"{cur('/book-now/').replace(' class="active"', '')}>Book Now</a>
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
