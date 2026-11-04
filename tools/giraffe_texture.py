"""Generate a seamless giraffe-skin texture (Voronoi patches, warped edges, cream gaps)."""
import numpy as np
from PIL import Image, ImageFilter
rng = np.random.default_rng(7)
W, H = 800, 240           # tile; shown at half size (400x120) for crispness
N = 34                    # patches per tile
# jittered seeds for even spacing
cols, rows = 9, 4
pts = []
for r in range(rows):
    for c in range(cols):
        if len(pts) >= N: break
        pts.append([(c + .5 + rng.uniform(-.38, .38)) * W / cols + (r % 2) * W / cols / 2,
                    (r + .5 + rng.uniform(-.35, .35)) * H / rows])
pts = np.array(pts) % [W, H]
yy, xx = np.mgrid[0:H, 0:W].astype(float)
# smooth tileable noise for wobbly edges
def tnoise(scale, amp, seed):
    g = np.random.default_rng(seed)
    out = np.zeros((H, W))
    for k in range(1, 4):
        for _ in range(3):
            fx, fy = g.integers(1, 4) * k, g.integers(1, 3) * k
            ph = g.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * (fx * xx / W + fy * yy / H) + ph) / k
    return out / np.abs(out).max() * amp
wx, wy = tnoise(1, 9, 1), tnoise(1, 9, 2)
X, Y = xx + wx, yy + wy
d1 = np.full((H, W), 1e9); d2 = np.full((H, W), 1e9); idx = np.zeros((H, W), int)
for i, (px, py) in enumerate(pts):
    dx = np.abs(X - px); dx = np.minimum(dx, W - dx)
    dy = np.abs(Y - py); dy = np.minimum(dy, H - dy)
    d = np.sqrt(dx * dx + dy * dy)
    m = d < d1
    d2 = np.where(m, d1, np.minimum(d2, d)); idx = np.where(m, i, idx); d1 = np.where(m, d, d1)
edge = d2 - d1                         # distance to cell border
gap = 7 + tnoise(1, 3, 3)              # cream line width varies
cream = np.array([224, 208, 186]); cream2 = np.array([206, 188, 166])
tone = rng.uniform(-.12, .10, N)
base = np.array([128, 80, 50])
patch = base[None, None, :] * (1 + tone[idx])[..., None]
# darker toward patch edges, slight inner highlight
shade = np.clip(edge / 26, 0, 1)
patch = patch * (0.82 + 0.18 * shade)[..., None]
cn = (tnoise(1, 1, 4) + 1) / 2
creamc = cream * (1 - cn[..., None] * .5) + cream2 * (cn[..., None] * .5)
a = np.clip((edge - gap) / 1.6, 0, 1)[..., None]    # antialiased border
img = creamc * (1 - a) + patch * a
img += np.random.default_rng(5).normal(0, 4, img.shape)  # fur grain
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))
im.save('/home/user/jacanariverlodge/assets/images/giraffe-texture.jpg', quality=82, optimize=True, progressive=True)
print('ok')
