"""Split a tall page screenshot into viewport-height tiles (decision from P1-02).

Full-page captures are often 10-60k px tall; vision models shrink them until text
is unreadable. Each tile is roughly one screen, so text stays legible.
"""
import io

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # full-page captures are legitimately huge

MOBILE_MAX_WIDTH = 1000   # wider captures are treated as desktop
MOBILE_RATIO = 2.16       # 390 x 844 phone screen
DESKTOP_RATIO = 0.625     # 16:10 laptop screen


def device_of(width):
    return "mobile" if width < MOBILE_MAX_WIDTH else "desktop"


def tile_height(width):
    return round(width * (MOBILE_RATIO if device_of(width) == "mobile" else DESKTOP_RATIO))


def tiles(image_bytes, max_tiles=None, quality=85):
    """Return (device, total_tiles, [jpeg bytes per tile]), top to bottom."""
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = im.size
    th = tile_height(w)
    out = []
    for top in range(0, h, th):
        buf = io.BytesIO()
        im.crop((0, top, w, min(top + th, h))).save(buf, "JPEG", quality=quality)
        out.append(buf.getvalue())
    total = len(out)
    return device_of(w), total, out[:max_tiles] if max_tiles else out
