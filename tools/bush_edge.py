#!/usr/bin/env python3
"""Generate a bushveld-skyline section edge: rolling waves topped with an uneven
tree line (low scrub plus a few flat-topped acacias). Filled below the line.
Usage: bush_edge.py out.svg FILL [seed]"""
import math, random, sys
out, fill = sys.argv[1], sys.argv[2]
rnd = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
W, H = 2000, 120
def base(x):  # long, gentle waves
    return 74 + 22*math.sin(x/2000*2*math.pi*1.6+0.6) + 9*math.sin(x/2000*2*math.pi*3.4+1.9)
pts = []
x = 0.0
acacias = sorted(rnd.sample(range(160, 1840, 40), 6))
while x <= W:
    near = [a for a in acacias if abs(a-x) < 70]
    if near:  # flat-topped acacia: trunk-ish rise, wide flat crown
        a = near[0]; acacias.remove(a)
        y0 = base(a); h = rnd.uniform(24, 34); w = rnd.uniform(90, 130)
        x0 = max(x, a - w/2 - 14)
        for px, py in [(x0, y0), (a - w/2, y0 - h*0.55), (a - w/2 + 6, y0 - h), (a - w*0.15, y0 - h - 2.5),
                       (a + w*0.2, y0 - h - 1), (a + w/2 - 4, y0 - h), (a + w/2, y0 - h*0.5), (a + w/2 + 14, base(a + w/2 + 14))]:
            pts.append((px, py))
        x = a + w/2 + 18
        continue
    # scrub: small irregular bumps
    y = base(x) - abs(rnd.gauss(0, 1.6)) - (rnd.random() < 0.12) * rnd.uniform(2, 5)
    pts.append((x, y))
    x += rnd.uniform(10, 22)
pts.append((W, base(W)))
segs = []
for i in range(1, len(pts) - 1):
    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
    segs.append(f"Q{x1:.1f} {y1:.1f} {(x1 + x2) / 2:.1f} {(y1 + y2) / 2:.1f}")
d = f"M0 {H} L{pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(segs) + f" L{W} {pts[-1][1]:.1f} L{W} {H} Z"
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
       f'<path fill="{fill}" d="{d}"/></svg>\n')
open(out, "w").write(svg); print(len(svg), "bytes")
