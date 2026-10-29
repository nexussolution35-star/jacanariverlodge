#!/usr/bin/env python3
"""Polite crawl of every sitemap URL: status, redirect chain, on-page SEO, and raw HTML archive.
Usage: crawl.py <sitemap_urls.json> <out_dir>"""
import sys, os, json, re, time, ssl, urllib.request, urllib.error
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, "html"), exist_ok=True)
urls = json.load(open(src))
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx), NoRedirect)

def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    try:
        r = opener.open(req, timeout=40)
        return r.status, r.headers.get("Location"), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), ""
    except Exception as e:
        return 0, None, str(e)

def clean(t):
    return " ".join((t or "").split())

rows = []
for i, item in enumerate(urls):
    u = item["url"]
    chain, cur, html, status = [], u, "", 0
    for _ in range(5):
        status, loc, html = fetch(cur)
        chain.append(f"{status} {cur}")
        if status in (301, 302, 307, 308) and loc:
            cur = urllib.parse.urljoin(cur, loc)
            continue
        break
    row = {**item, "status": status, "final_url": cur, "redirect_chain": chain if len(chain) > 1 else []}
    if status == 200 and html:
        slug = re.sub(r"[^a-z0-9]+", "-", u.replace("https://jacanariverlodge.com", "").lower()).strip("-") or "home"
        open(os.path.join(out, "html", slug + ".html"), "w").write(html)
        soup = BeautifulSoup(html, "lxml")
        def meta(**kw):
            t = soup.find("meta", attrs=kw)
            return clean(t.get("content")) if t and t.get("content") else ""
        canon = soup.find("link", rel="canonical")
        schema = []
        for s in soup.find_all("script", type="application/ld+json"):
            for t in re.findall(r'"@type"\s*:\s*"([^"]+)"', s.string or ""):
                schema.append(t)
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        h1 = [clean(h.get_text()) for h in soup.find_all("h1")]
        h2 = [clean(h.get_text()) for h in soup.find_all("h2")][:10]
        body = soup.find("article") or soup.find("main") or soup.body
        for t in (body.find_all(["header", "footer", "nav", "aside"]) if body else []):
            t.decompose()
        words = len(clean(body.get_text(" ")).split()) if body else 0
        links = set()
        for a in (body.find_all("a", href=True) if body else []):
            h = a["href"].split("#")[0]
            if h.startswith("https://jacanariverlodge.com") and "/wp-content/" not in h:
                links.add(h)
        row.update({
            "title": clean(soup.title.string) if soup.title and soup.title.string else "",
            "meta_desc": meta(name="description"),
            "canonical": canon.get("href") if canon else "",
            "robots": meta(name="robots"),
            "published": meta(property="article:published_time")[:10],
            "modified": meta(property="article:modified_time")[:10],
            "h1": h1, "h2": h2, "words": words,
            "schema": sorted(set(schema)),
            "internal_links_out": sorted(links),
        })
    rows.append(row)
    print(f"[{i+1}/{len(urls)}] {status} {u}", flush=True)
    time.sleep(0.8)

json.dump(rows, open(os.path.join(out, "crawl.json"), "w"), indent=1, ensure_ascii=False)
print("DONE", len(rows))
