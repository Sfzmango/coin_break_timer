"""Download coin photos from Wikimedia Commons and cut each coin out to a transparent WebP in coins/."""
import hashlib, io, os, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw

UA = "CoinBreakTimer/1.0 (https://github.com/Sfzmango/coin_break_timer)"
OUT, SIZE = "coins", 384
COINS = [
    ("half-eagle-1908", "both", ["NNC-US-1908-G$5-Indian_Head.jpg"]),
    ("half-eagle-1866", "both", ["NNC-US-1866-G$5-Liberty_Head_(motto).jpg"]),
    ("half-eagle-1834", "both", ["NNC-US-1834-G$5-Classic_Head.jpg"]),
    ("half-eagle-1807", "both", ["NNC-US-1807-G$5-Capped_Bust.jpg"]),
    ("half-eagle-1795", "both", ["NNC-US-1795-G$5-Turban_Head_(heraldic_eagle).jpg"]),
    ("walking-liberty-1945", "pair", ["Walking_Liberty_Half_Dollar_1945D_Obverse.png",
                                      "Walking_Liberty_Half_Dollar_1945D_Reverse.png"]),
]

def fetch(name, width):
    h = hashlib.md5(name.encode()).hexdigest()
    q = urllib.parse.quote(name)
    urls = [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}",
        f"https://commons.wikimedia.org/wiki/Special:FilePath/{q}?width={width}",
        f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}",
    ]
    for u in urls:
        for attempt in range(3):
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                data = urllib.request.urlopen(req, timeout=120).read()
                Image.MAX_IMAGE_PIXELS = None
                return Image.open(io.BytesIO(data)).convert("RGBA")
            except Exception as e:
                print("  retry", u, e, file=sys.stderr)
                time.sleep(3 * (attempt + 1))
    raise RuntimeError("could not download " + name)

def cut(im):
    """Find the coin against a plain or transparent background and return it on a transparent circle."""
    w, h = im.size
    px = im.load()
    corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = [sum(c[i] for c in corners) / 4 for i in range(4)]
    small = im.resize((max(8, w // 4), max(8, h // 4)))
    sw, sh = small.size
    sp = small.load()
    xs, ys = [], []
    for y in range(sh):
        for x in range(sw):
            p = sp[x, y]
            hit = p[3] > 40 if bg[3] < 20 else sum(abs(p[i] - bg[i]) for i in range(3)) > 54
            if hit:
                xs.append(x); ys.append(y)
    if not xs:
        box = (0, 0, w, h)
    else:
        k = w / sw
        box = (min(xs) * k, min(ys) * k, (max(xs) + 1) * k, (max(ys) + 1) * k)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    r = max(box[2] - box[0], box[3] - box[1]) / 2 * 0.985
    sq = im.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r))).resize((SIZE, SIZE), Image.LANCZOS)
    mask = Image.new("L", (SIZE * 4, SIZE * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), fill=255)
    mask = mask.resize((SIZE, SIZE), Image.LANCZOS)
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(sq, (0, 0), mask)
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    for cid, kind, files in COINS:
        print(cid)
        if kind == "both":
            im = fetch(files[0], 1280)
            half = im.width // 2
            sides = [im.crop((0, 0, half, im.height)), im.crop((half, 0, half * 2, im.height))]
        else:
            sides = [fetch(f, 500) for f in files]
        for side, tag in zip(sides, ("obv", "rev")):
            cut(side).save(f"{OUT}/{cid}-{tag}.webp", "WEBP", quality=92, method=6)

if __name__ == "__main__":
    main()
