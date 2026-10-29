#!/usr/bin/env python3
"""Turn the live crawl into repo deliverables.
Usage: build_inventory.py <live_dir> <seo_out_dir>
Writes: url-inventory.csv, url-map.csv, content/<type>/<slug>.md, source/ (robots + sitemaps)."""
import sys, os, json, re, csv, shutil, collections
from bs4 import BeautifulSoup
from markdownify import markdownify as md

live, out = sys.argv[1], sys.argv[2]
crawl = json.load(open(os.path.join(live, "crawl.json")))
SITE = "https://jacanariverlodge.com"
os.makedirs(os.path.join(out, "source"), exist_ok=True)
for f in os.listdir(live):
    if f.endswith(".xml") or f == "robots.txt":
        shutil.copy(os.path.join(live, f), os.path.join(out, "source", f))

def slug_of(url):
    return re.sub(r"[^a-z0-9]+", "-", url.replace(SITE, "").lower()).strip("-") or "home"

def path_of(url):
    return url.replace(SITE, "") or "/"

# inbound internal links (body links only)
inbound = collections.Counter()
for r in crawl:
    for l in r.get("internal_links_out", []):
        inbound[l.rstrip("/") + "/"] += 1

# ---------- content as markdown ----------
STRIP = [".sidebar", ".widget", "#Footer", "#Header", ".section-post-related", ".post-nav",
         ".share-simple-wrapper", "#comments", ".comments", ".section-post-intro-share",
         ".fixed-nav", ".ti-widget", "script", "style", "noscript", "form", "iframe"]
for r in crawl:
    if r["status"] != 200 or r["type"] in ("post_tag", "author"):
        continue
    fp = os.path.join(live, "html", slug_of(r["url"]) + ".html")
    soup = BeautifulSoup(open(fp, encoding="utf-8", errors="ignore").read(), "lxml")
    main = soup.select_one("#Content") or soup.body
    for sel in STRIP:
        for t in main.select(sel):
            t.decompose()
    body = md(str(main), heading_style="ATX", strip=["span", "div", "section"])
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    fm = {
        "url": r["url"], "type": r["type"], "title": r.get("title", ""),
        "meta_description": r.get("meta_desc", ""), "h1": r.get("h1", []),
        "canonical": r.get("canonical", ""), "published": r.get("published", ""),
        "modified": r.get("modified", "") or r.get("lastmod", ""), "words": r.get("words", 0),
    }
    d = os.path.join(out, "content", r["type"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, slug_of(r["url"]) + ".md"), "w") as f:
        f.write("---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()) + "---\n\n" + body + "\n")

# ---------- url-inventory.csv ----------
cols = ["type", "path", "status", "redirects_to", "lastmod", "published", "title", "title_len",
        "meta_description", "meta_len", "h1_count_raw", "h1", "canonical", "robots", "words",
        "inbound_internal_links", "schema_types"]
with open(os.path.join(out, "url-inventory.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in sorted(crawl, key=lambda r: (r["type"], path_of(r["url"]))):
        w.writerow([r["type"], path_of(r["url"]), r["status"],
                    path_of(r["final_url"]) if r["final_url"] != r["url"] else "",
                    r.get("lastmod", ""), r.get("published", ""), r.get("title", ""), len(r.get("title", "")),
                    r.get("meta_desc", ""), len(r.get("meta_desc", "")), len(r.get("h1", [])),
                    " | ".join(r.get("h1", [])), r.get("canonical", ""), r.get("robots", ""),
                    r.get("words", 0), inbound[r["url"].rstrip("/") + "/"], ";".join(r.get("schema", []))])

# ---------- url-map.csv (draft preservation plan) ----------
CORE = {
    "/": "Home", "/facilities/": "Rates & Facilities", "/book-now/": "Book Now / enquiry",
    "/contact-us/": "Contact", "/gallery/": "Gallery", "/news/": "Blog index",
    "/activities-near-mjejane/": "Activities hub (nav dropdown parent)",
    "/game-drive-mjejane-game-reserve/": "Activity: private game drives",
    "/mjejane-game-reserve-birding-guide/": "Activity: birding",
    "/full-and-half-day-game-drive-in-the-kruger-park/": "Activity: Kruger day drives",
    "/kruger-full-day-safari-with-irving-knight-safaris/": "Activity: Irving Knight safaris",
    "/panorama-tours-packages-and-pricing/": "Activity: Panorama Route tours",
    "/mjejane-accommodation-prices-and-packages/": "Packages", "/mjejane-accommodation-specials/": "Specials",
    "/mjejane-game-reserve-accommodation-guide/": "Pillar: Mjejane accommodation guide",
    "/wildlife-and-sightings/": "Wildlife hub", "/wildlife-and-sightings/sightings/": "Wildlife: sightings",
    "/wildlife-and-sightings/wildlife-in-mjejane/": "Wildlife: species of Mjejane",
    "/rules-and-safety/": "Rules & Safety", "/mjejane-bridge-entrance-to-knp/": "Getting here: Mjejane Bridge",
    "/cookies-and-privacy-policy/": "Privacy policy",
    "/self-catering-family-retreat-in-mpumalanga/": "Keyword landing page",
    "/self-catering-getaway-in-mpumalanga/": "Keyword landing page",
    "/luxury-self-catering-lodge-accommodation-in-mpumalanga/": "Keyword landing page",
}
PACKAGE_2023 = re.compile(r"^/(kruger-full-day-safari-with-(irving-knight|lihlosi)-safaris-at-jacana-river-lodge-(weekend|1-week)|kruger-and-panorama-route-tour-(week|weekend))/$")
TIMEBOUND = re.compile(r"(january|february|march|april|may|june|july|august|september|october|november|december)-20\d\d|20(2[0-6])")
dup_titles = collections.defaultdict(list)
for r in crawl:
    if r["type"] == "post" and r.get("title"):
        dup_titles[r["title"]].append(path_of(r["url"]))

def plan(r):
    p, t = path_of(r["url"]), r["type"]
    if p in CORE:
        return "KEEP", p, CORE[p], "Rebuild at the identical path in the new design."
    if p in ("/thank-you/", "/thank-you-for-your-booking-enquiry/"):
        return "KEEP", p, "Form confirmation", "Keep path (conversion tracking). Recommend noindex."
    if p == "/activities/":
        return "PROPOSED 301", "/activities-near-mjejane/", "Duplicate of activities hub", "Same title+meta as /activities-near-mjejane/. Confirm in GSC before redirecting."
    if PACKAGE_2023.match(p):
        return "KEEP (review)", p, "2023 package page", "Thin, no meta. Candidate to consolidate into /mjejane-accommodation-prices-and-packages/ once GSC confirms no traffic."
    if p == "/backlinks/":
        return "KEEP (review)", p, "'Useful links' utility page", "Thin internal-links page. Candidate for noindex."
    if t == "post":
        notes = []
        if len(dup_titles[r.get("title", "")]) > 1:
            notes.append("Duplicate title with: " + ", ".join(x for x in dup_titles[r["title"]] if x != p))
        if TIMEBOUND.search(p):
            notes.append("Time-bound slug; refresh or consolidate later (keep URL).")
        if r.get("words", 0) < 300:
            notes.append(f"Thin ({r.get('words')} words).")
        return "KEEP", p, "Blog post (same slug)", " ".join(notes) or "Migrate as-is."
    if t == "post_tag":
        return "KEEP (review)", p, "Tag archive", "Keep at launch. Recommend noindex after launch (thin archives)."
    if t == "category":
        note = "Recommend noindex." if p == "/category/uncategorized/" else "Keep."
        return "KEEP", p, "Category archive", note
    if t == "author":
        return "KEEP", p, "Author archive", "Keep (E-E-A-T author page)."
    if t in ("testimonial", "portfolio"):
        return "KEEP (review)", p, f"{t} item", "Thin legacy item. Candidate to 301 into a reviews/wildlife page once GSC confirms no traffic."
    return "KEEP", p, "Unclassified page", "Review manually."

with open(os.path.join(out, "url-map.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["type", "old_path", "action", "new_path", "new_site_role", "notes"])
    for r in sorted(crawl, key=lambda r: (r["type"] != "page", r["type"], path_of(r["url"]))):
        a, np, role, note = plan(r)
        w.writerow([r["type"], path_of(r["url"]), a, np, role, note])

print("content files:", sum(len(fs) for _, _, fs in os.walk(os.path.join(out, "content"))))
print("done ->", out)
