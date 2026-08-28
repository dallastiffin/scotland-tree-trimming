#!/usr/bin/env python3
"""
Regenerate every logo asset from the master Logo.png.

    python tools/make-logo.py

This build expects a SINGLE circular badge master - the emblem (house, spray
gun, foam) above the stacked wordmark, all inside a ring. The earlier version
expected two lockups side by side and sliced them apart with hardcoded pixel
bounds; that broke the moment a differently-shaped logo was supplied.

Outputs
    icon-{16..512}.png                      full badge, all sizes
    favicon.ico                             multi-resolution
    logo.png                                512px badge, for schema.org
    wordmark-{300,600}.png                  full badge, for light backgrounds
    wordmark-light-{300,600}.png            reversed, for the dark footer
"""
from PIL import Image
from collections import deque
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "Logo.png")
IMG  = os.path.join(ROOT, "site", "images")

# Sampled from the master rather than guessed.
BRAND_PRIMARY = (18, 71, 75)     # #12474B
BRAND_ACCENT  = (164, 71, 27)    # #A4471B

# How much of the trimmed badge height is emblem rather than wordmark. Used
# to crop a legible mark for the very small icon sizes.
EMBLEM_FRACTION = 0.60


def clear_outside(img, thresh=232):
    """Flood-fill transparency inward from the border.

    Deliberately NOT a global white-to-alpha swap: the icon's G is solid white
    and would be punched into a hole. Only white connected to an outside edge
    is removed.
    """
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = [[False] * w for _ in range(h)]
    q = deque()

    def is_white(x, y):
        r, g, b, _ = px[x, y]
        return r >= thresh and g >= thresh and b >= thresh

    for x in range(w):
        for y in (0, h - 1):
            if is_white(x, y) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_white(x, y) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))

    while q:
        x, y = q.popleft()
        px[x, y] = (255, 255, 255, 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and is_white(nx, ny):
                seen[ny][nx] = True
                q.append((nx, ny))

    return img.crop(img.getbbox())


def save_png(img, path, colors=64):
    """Quantise. These are flat-colour marks; 24-bit is wasted bytes."""
    rgba = img.convert("RGBA")
    alpha = rgba.split()[-1]
    out = rgba.convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT).convert("RGBA")
    out.putalpha(alpha)
    out.save(path, optimize=True)


def reverse_colours(img):
    """Recolour the badge for a dark background.

    The indigo becomes white so the ring and the wordmark stay visible. The
    amber and the white foam cloud are already legible on dark, so both are
    left alone.
    """
    out = img.copy()
    px = out.load()

    def near(c, ref):
        return sum((a - b) ** 2 for a, b in zip(c, ref))

    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if r > g + 20 and r > b + 20:      # amber: leave as-is
                continue
            if r > 225 and g > 225 and b > 225:  # foam / highlights: leave white
                continue
            if near((r, g, b), BRAND_PRIMARY) < near((r, g, b), BRAND_ACCENT):
                px[x, y] = (255, 255, 255, a)
    return out


def main():
    os.makedirs(IMG, exist_ok=True)

    badge = clear_outside(Image.open(SRC).convert("RGBA"))

    def square(img):
        side = max(img.size)
        out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        out.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
        return out

    badge_sq = square(badge)

    # Every size uses the full badge. A cropped emblem was tried and read
    # worse at 16-32px: the ring gives the mark a defined circular silhouette,
    # while a crop of the house and gun is ambiguous at that size.
    for size in (512, 192, 180, 96, 64, 48, 32, 16):
        save_png(badge_sq.resize((size, size), Image.LANCZOS),
                 os.path.join(IMG, "icon-%d.png" % size))
        print("  icon-%d.png" % size)

    save_png(badge_sq.resize((512, 512), Image.LANCZOS), os.path.join(IMG, "logo.png"))
    badge_sq.resize((256, 256), Image.LANCZOS).save(
        os.path.join(IMG, "favicon.ico"),
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("  favicon.ico, logo.png")

    light = reverse_colours(badge)
    for w in (600, 300):
        h = round(w * badge.height / badge.width)
        save_png(badge.resize((w, h), Image.LANCZOS),
                 os.path.join(IMG, "wordmark-%d.png" % w))
        save_png(light.resize((w, h), Image.LANCZOS),
                 os.path.join(IMG, "wordmark-light-%d.png" % w))
        print("  wordmark-%d.png, wordmark-light-%d.png  (%dx%d)" % (w, w, w, h))

    print("\nBadge aspect: %d x %d" % badge.size)
    print("Done. Run 'python build.py' to refresh the cache fingerprints.")


if __name__ == "__main__":
    main()
