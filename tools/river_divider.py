#!/usr/bin/env python3
"""Generate assets/images/river-divider.svg: a flat vector river divider
(reeds, lily pads, tapered water lines) traced from the supplied artwork.
Above the top water line is transparent; below it is filled with the next
section's colour (#FFF9F4). Re-run after tweaking the numbers below."""
import math, sys

W, H = 2000, 150          # viewBox
PAPER = "#FFF9F4"
BLUE, BLUE_LIGHT = "#60B2FD", "#9DCBF4"
GREEN, GREEN_DARK = "#7AB123", "#689A1C"

def ty(y):                # artwork y (2000x667 source) -> viewBox y; flattens the waves
    return round(0.5 * (y - 270) + 45, 2)

def spline(pts, n=14):
    """Catmull-Rom through pts, returns dense list of (x, y)."""
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def ribbon(pts, wmax, taper=0.55):
    """Filled shape around a centreline whose width swells in the middle and tapers to points."""
    c = spline(pts); n = len(c); top, bot = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = wmax * math.sin(math.pi * i / (n - 1)) ** taper / 2
        top.append((x + nx * w, y + ny * w)); bot.append((x - nx * w, y - ny * w))
    ring = top + bot[::-1]
    return "M" + " ".join(f"{f(x)} {f(y)}" for x, y in ring) + "Z"

def blade(base, ctrl, tip, wbase):
    """A reed leaf: quadratic curve base->tip, tapering from wbase to a point."""
    pts = []
    for k in range(13):
        t = k / 12
        x = (1 - t) ** 2 * base[0] + 2 * (1 - t) * t * ctrl[0] + t * t * tip[0]
        y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * ctrl[1] + t * t * tip[1]
        pts.append((x, y))
    L_, R_ = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, 12)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L; w = wbase * (1 - i / 12) ** 0.9 / 2
        L_.append((x + nx * w, y + ny * w)); R_.append((x - nx * w, y - ny * w))
    ring = L_ + R_[::-1]
    return "M" + " ".join(f"{f(x)} {f(y)}" for x, y in ring) + "Z"

def pad(cx, cy, rx, ry, notch=(-24, -10)):
    """Lily pad: ellipse with a narrow slit from the rim to the centre (upper right)."""
    a1, a2 = (math.radians(a) for a in notch)
    p1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
    p2 = (cx + rx * math.cos(a2), cy + ry * math.sin(a2))
    return (f"M{f(cx + rx * 0.05)} {f(cy - ry * 0.05)} L{f(p2[0])} {f(p2[1])} "
            f"A{f(rx)} {f(ry)} 0 1 1 {f(p1[0])} {f(p1[1])}Z")

S = lambda pts: [(x, ty(y)) for x, y in pts]

# --- water lines (centrelines traced from the artwork) ---
fullA = S([(40, 402), (120, 375), (220, 348), (320, 318), (420, 299), (520, 291), (620, 294), (720, 311), (820, 337),
           (920, 362), (1020, 374), (1100, 378), (1170, 371), (1270, 341), (1370, 318), (1470, 312), (1570, 319),
           (1670, 337), (1770, 351), (1870, 348), (1920, 333), (1985, 300)])
lineA = [p for p in fullA if 150 <= p[0] <= 1870]   # keep the drawn lines clear of the screen edges
lineB = S([(330, 352), (470, 327), (570, 331), (670, 343), (770, 361), (870, 383), (970, 395), (1050, 393), (1110, 384)])
lineC = S([(1060, 420), (1170, 418), (1270, 406), (1370, 385), (1470, 363), (1570, 352), (1670, 360), (1770, 385),
           (1840, 392), (1880, 386)])
ripple = S([(130, 352), (200, 334), (260, 320)])

# paper fill: everything under line A (extended to both edges)
fill_line = spline([(0, ty(410))] + fullA + [(W, ty(286))])
fill = "M" + " ".join(f"{f(x)} {f(y + 1)}" for x, y in fill_line) + f" L{W} {H} L0 {H}Z"

shapes = [f'<path fill="{PAPER}" d="{fill}"/>',
          f'<path fill="{BLUE}" d="{ribbon(lineA, 11)}"/>',
          f'<path fill="{BLUE}" d="{ribbon(lineB, 10)}"/>',
          f'<path fill="{BLUE_LIGHT}" d="{ribbon(lineC, 8)}"/>',
          f'<path fill="{BLUE_LIGHT}" d="{ribbon(ripple, 3)}"/>']

# --- lily pads ---
for cx, cy, rx, ry in [(357, 329, 62, 17), (522, 377, 58, 15), (1550, 373, 64, 17)]:
    shapes.append(f'<path fill="{GREEN}" d="{pad(cx, ty(cy), rx, ry)}"/>')

# --- reeds (base, control, tip, width) in viewBox units ---
def reeds(bx, by, spec, flip=1):
    out = []
    for (cdx, cdy, tdx, tdy, w, col) in spec:
        out.append(f'<path fill="{col}" d="{blade((bx, by), (bx + flip * cdx, by + cdy), (bx + flip * tdx, by + tdy), w)}"/>')
    return out
spec = [(-12, -27, -48, -50, 12, GREEN),        # long blade leaning out
        (-2, -32, -10, -60, 12, GREEN_DARK),    # tall, slightly back
        (6, -31, 16, -63, 13, GREEN),           # tallest, upright
        (17, -21, 50, -36, 11, GREEN),          # arching to the side
        (-20, -12, -62, -19, 9, GREEN_DARK),    # low blade along the water
        (23, -9, 60, -12, 8, GREEN_DARK)]       # low blade, other side
shapes += reeds(206, ty(342), spec, flip=1)
shapes += reeds(1742, ty(368), spec, flip=-1)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">'
       + "".join(shapes) + "</svg>\n")
open(sys.argv[1] if len(sys.argv) > 1 else "assets/images/river-divider.svg", "w").write(svg)
print(len(svg), "bytes")
