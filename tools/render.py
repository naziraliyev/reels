"""Render a Reels video (1080x1920, 30fps, H.264 + original music) from a JSON spec.

Usage:  python3 tools/render.py path/to/spec.json OUT_DIR
Writes OUT_DIR/video.mp4, OUT_DIR/caption.txt and OUT_DIR/preview/*.png (one frame per scene).

Spec format (see tools/example_spec.json):
{
  "topic": "short id of the topic",           # logged in topics.md
  "lang": "sql" | "dart" | "python" | "js",   # code highlighting
  "accent": "#facc15",                         # optional
  "caption": "full Instagram caption with hashtags",
  "music": "lofi" | "sql" | "flutter",         # optional; default from lang: sql->sql, dart->flutter, else lofi
  "scenes": [ {"type": ..., "dur": seconds, ...}, ... ]
}
Scene types:
  hook     {title, lines[], footer}
  text     {title, lines[]}                     big readable explanation
  bullets  {title, items[]}
  code     {title, desc[], code[], out_title, out[] | table:{cols[],rows[][]}}
           (a code/out line starting with "!" is drawn as plain red error text,
            one starting with "~" as plain white output text)
  compare  {title, bad_label, bad[], good_label, good[], note}
  table    {title, tables:[{name, cols[], rows[][]}], note[]}
  cta      {title, lines[], box_title, box_text, footer[]}
Every scene gets a fade, a gentle zoom-free hold and a bottom progress bar.
"""
import json, os, re, subprocess, sys, random

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
F = "/usr/share/fonts/opentype/inter/"
M = "/usr/share/fonts/truetype/dejavu/"

BG = (13, 17, 28)
CARD = (24, 30, 46)
CODEBG = (8, 11, 20)
TXT = (236, 240, 248)
MUTED = (140, 150, 172)
CYAN = (56, 189, 248)
PINK = (244, 114, 182)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
STR = (163, 230, 53)
NUM = (251, 146, 60)
COMMENT = (100, 116, 139)
NULLC = (120, 128, 148)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(weight, size):
    return ImageFont.truetype(F + f"Inter-{weight}.otf", size)


def mono(size, bold=False):
    return ImageFont.truetype(M + ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"), size)


KEYWORDS = {
    "sql": "select from where join inner left right full outer on group by order having limit insert into values update set delete create table alter drop as and or not null is in between like distinct count sum avg min max case when then else end union all exists primary key foreign references index view with over partition row_number rank dense_rank desc asc".split(),
    "dart": "void main class extends implements with final const var int double String bool return if else for while new import async await Future Stream StatelessWidget StatefulWidget State Widget build BuildContext setState override super this true false null late required dynamic List Map Set try catch throw static get set enum switch case break".split(),
    "python": "def return if elif else for while in import from as class try except finally with lambda yield None True False and or not is pass break continue print self async await".split(),
    "js": "function return if else for while const let var class new import export from async await true false null undefined this try catch throw switch case break of in".split(),
}


def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, spec):
        self.accent = hexrgb(spec.get("accent", "#facc15"))
        self.lang = spec.get("lang", "sql")
        self.kw = set(k.lower() for k in KEYWORDS.get(self.lang, []))

    def new(self):
        im = Image.new("RGB", (W, H), BG)
        # subtle top glow
        glow = Image.new("RGB", (W, 500), BG)
        gd = ImageDraw.Draw(glow)
        for i in range(500):
            a = int(18 * (1 - i / 500))
            gd.line([(0, i), (W, i)], fill=(BG[0] + a // 3, BG[1] + a // 2, BG[2] + a))
        im.paste(glow, (0, 0))
        return im, ImageDraw.Draw(im)

    # ---- primitives -------------------------------------------------------
    def center(self, d, y, text, fnt, fill=TXT, maxw=W - 140, gap=1.18):
        for line in wrap(d, text, fnt, maxw):
            d.text((W // 2, y), line, font=fnt, fill=fill, anchor="ma")
            y += int(fnt.size * gap)
        return y

    def title(self, d, y, text, size=92):
        fnt = font("Black", size)
        while d.textlength(text, font=fnt) > W - 120 and size > 56:
            size -= 4
            fnt = font("Black", size)
        return self.center(d, y, text, fnt, self.accent)

    def code_line(self, d, x, y, line, size):
        # tokens: strings, comments, numbers, words, other
        if line.startswith("!"):  # error/exception output line: plain red text
            d.text((x, y), line[1:], font=mono(size), fill=RED)
            return
        if line.startswith("~"):  # plain program output line (no highlighting)
            d.text((x, y), line[1:], font=mono(size), fill=TXT)
            return
        if self.lang in ("sql",) and line.strip().startswith("--") or line.strip().startswith("//") or line.strip().startswith("#"):
            d.text((x, y), line, font=mono(size), fill=COMMENT)
            return
        for tok in re.findall(r"'[^']*'|\"[^\"]*\"|\d+\.?\d*|\w+|\s+|.", line):
            low = tok.lower()
            if tok[:1] in "'\"":
                col, f = STR, mono(size)
            elif re.fullmatch(r"\d+\.?\d*", tok):
                col, f = NUM, mono(size)
            elif low in self.kw:
                col, f = self.accent, mono(size, True)
            elif tok[:1].isupper() and self.lang == "dart":
                col, f = CYAN, mono(size)
            else:
                col, f = TXT, mono(size)
            d.text((x, y), tok, font=f, fill=col)
            x += d.textlength(tok, font=f)

    def code(self, d, y, lines, size=None):
        longest = max((len(l) for l in lines), default=10)
        if size is None:
            size = 40
            while size > 24 and longest * size * 0.602 > W - 200:
                size -= 2
        lh = int(size * 1.5)
        h = 60 + lh * len(lines)
        d.rounded_rectangle((60, y, W - 60, y + h), radius=24, fill=CODEBG, outline=(40, 48, 70), width=2)
        for i, line in enumerate(lines):
            self.code_line(d, 100, y + 30 + i * lh, line, size)
        return y + h

    def table(self, d, x, y, w, cols, rows, name=None, color=TXT):
        rh = 68
        top = y
        h = rh * (len(rows) + 1) + 24 + (rh if name else 0)
        d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=CARD)
        if name:
            d.text((x + 28, y + 18), name, font=font("Bold", 38), fill=color)
            y += rh
        cw = (w - 56) / max(1, len(cols))
        for i, c in enumerate(cols):
            d.text((x + 28 + i * cw, y + 18), str(c), font=font("SemiBold", 30), fill=MUTED)
        for r, row in enumerate(rows):
            for i, v in enumerate(row):
                v = str(v)
                isnull = v.upper() == "NULL"
                d.text((x + 28 + i * cw, y + rh * (r + 1) + 12), v, font=mono(34, not isnull), fill=NULLC if isnull else TXT)
        return top + h

    # ---- scenes -----------------------------------------------------------
    def s_hook(self, s):
        im, d = self.new()
        y = 470
        y = self.title(d, y, s["title"], 150) + 40
        for l in s.get("lines", []):
            y = self.center(d, y, l, font("Black", 104)) + 6
        if s.get("sub"):
            y = self.center(d, y + 70, s["sub"], font("SemiBold", 54), MUTED)
        if s.get("footer"):
            self.center(d, 1500, s["footer"], font("Bold", 54), CYAN)
        return im

    def s_text(self, s):
        im, d = self.new()
        y = self.title(d, 220, s["title"]) + 80
        for l in s.get("lines", []):
            y = self.center(d, y, l, font("SemiBold", 66), TXT, gap=1.3) + 50
        return im

    def s_bullets(self, s):
        im, d = self.new()
        y = self.title(d, 220, s["title"]) + 90
        fnt = font("SemiBold", 58)
        for i, it in enumerate(s["items"]):
            lines = wrap(d, it, fnt, W - 300)
            bh = 72 * len(lines) + 56
            d.rounded_rectangle((70, y, W - 70, y + bh), radius=24, fill=CARD)
            d.ellipse((100, y + 30, 156, y + 86), fill=self.accent)
            d.text((128, y + 58), str(i + 1), font=font("Black", 34), fill=BG, anchor="mm")
            for j, l in enumerate(lines):
                d.text((190, y + 28 + j * 72), l, font=fnt, fill=TXT)
            y += bh + 30
        return im

    def s_code(self, s):
        im, d = self.new()
        y = self.title(d, 170, s["title"]) + 30
        for l in s.get("desc", []):
            y = self.center(d, y, l, font("SemiBold", 46)) + 2
        y = self.code(d, y + 60, s["code"]) + 50
        if s.get("table"):
            if s.get("out_title"):
                y = self.center(d, y, s["out_title"], font("Bold", 40), MUTED) + 16
            t = s["table"]
            self.table(d, 140, y, 800, t["cols"], t["rows"])
        elif s.get("out"):
            y = self.center(d, y, s.get("out_title", "Natija:"), font("Bold", 40), MUTED) + 16
            self.code(d, y, s["out"])
        return im

    def s_compare(self, s):
        im, d = self.new()
        y = self.title(d, 170, s["title"]) + 60
        d.text((80, y), "✗ " + s.get("bad_label", "Noto'g'ri"), font=font("Bold", 46), fill=RED)
        y = self.code(d, y + 80, s["bad"]) + 60
        d.text((80, y), "✓ " + s.get("good_label", "To'g'ri"), font=font("Bold", 46), fill=GREEN)
        y = self.code(d, y + 80, s["good"]) + 60
        if s.get("note"):
            self.center(d, y, s["note"], font("SemiBold", 46), MUTED)
        return im

    def s_table(self, s):
        im, d = self.new()
        y = self.title(d, 200, s["title"]) + 80
        cols = [CYAN, PINK, GREEN]
        for i, t in enumerate(s["tables"]):
            y = self.table(d, 90, y, 900, t["cols"], t["rows"], t.get("name"), cols[i % 3]) + 60
        for l in s.get("note", []):
            y = self.center(d, y, l, font("SemiBold", 46), MUTED) + 4
        return im

    def s_cta(self, s):
        im, d = self.new()
        y = self.title(d, 540, s.get("title", "Saqlab qo'ying"), 104) + 30
        for l in s.get("lines", []):
            y = self.center(d, y, l, font("SemiBold", 56)) + 4
        d.rounded_rectangle((140, 1000, W - 140, 1280), radius=30, fill=CARD)
        self.center(d, 1050, s.get("box_title", "Obuna bo'ling"), font("Black", 72), CYAN)
        self.center(d, 1160, s.get("box_text", "SQL  ·  Flutter  ·  Dasturlash"), font("Bold", 50))
        y = 1450
        for l in s.get("footer", []):
            y = self.center(d, y, l, font("SemiBold", 48), MUTED) + 4
        return im


def recenter(cv, im, top=150, bottom=1640):
    """Move the drawn content so it sits in the vertical middle of the safe area."""
    from PIL import ImageChops
    base, _ = cv.new()
    box = ImageChops.difference(im, base).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    h = y1 - y0
    if h > bottom - top:
        return im
    ny = top + (bottom - top - h) // 2
    content = im.crop((0, y0, W, y1))
    mask = ImageChops.difference(content, base.crop((0, y0, W, y1))).convert("L").point(lambda v: 255 if v > 0 else 0)
    base.paste(content, (0, ny), mask)
    return base


def check_fit(im):
    """True when nothing is drawn into the bottom area covered by Instagram's UI."""
    import numpy as np
    strip = np.asarray(im.crop((0, 1690, W, 1880)).convert("L"))
    return int(strip.max()) < sum(BG) // 3 + 40


def render(spec_path, out_dir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(os.path.join(out_dir, "preview"), exist_ok=True)
    tmp = os.path.join(out_dir, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    cv = Canvas(spec)
    scenes = spec["scenes"]
    total = sum(float(s.get("dur", 5)) for s in scenes)
    problems = []
    elapsed = 0.0
    listfile = os.path.join(tmp, "list.txt")
    with open(listfile, "w") as lf:
        for i, s in enumerate(scenes):
            im = getattr(cv, "s_" + s["type"])(s)
            if s["type"] not in ("hook", "cta"):
                im = recenter(cv, im)
            if not check_fit(im):
                problems.append(f"scene {i + 1} ({s['type']}) draws into the bottom Instagram UI area - shorten it")
            png = os.path.join(out_dir, "preview", f"{i + 1:02d}_{s['type']}.png")
            im.save(png)
            dur = float(s.get("dur", 5))
            fo = dur - 0.3
            # progress bar grows from elapsed/total to (elapsed+dur)/total during the scene
            x0 = int(W * elapsed / total)
            x1 = int(W * (elapsed + dur) / total)
            ac = "0x%02x%02x%02x" % cv.accent
            vf = (f"format=yuv420p,loop=-1:1,trim=duration={dur},setpts=N/{FPS}/TB,"
                  f"fade=t=in:st=0:d=0.25,fade=t=out:st={fo}:d=0.3")
            part = os.path.join(tmp, f"p{i:02d}.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", png,
                            "-f", "lavfi", "-i", f"color=c=0x1b2133:s={W}x14:r={FPS}:d={dur}",
                            "-f", "lavfi", "-i", f"color=c={ac}:s={W}x14:r={FPS}:d={dur}",
                            "-filter_complex",
                            f"[0:v]{vf}[bg];"
                            f"[bg][1:v]overlay=0:{H - 14}:shortest=1[b1];"
                            f"[b1][2:v]overlay=x='-{W}+{x0}+({x1 - x0})*t/{dur}':y={H - 14}:shortest=1,format=yuv420p",
                            "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", part + ".tmp.mp4"], check=True)
            os.replace(part + ".tmp.mp4", part)
            lf.write(f"file '{os.path.abspath(part)}'\n")
            elapsed += dur
    silent = os.path.join(tmp, "v.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", silent], check=True)
    wav = os.path.join(tmp, "m.wav")
    style = spec.get("music") or {"sql": "sql", "dart": "flutter"}.get(spec.get("lang"), "lofi")
    subprocess.run([sys.executable, os.path.join(HERE, "music.py"), wav, str(total + 0.5), str(random.randint(1, 10 ** 6)), style], check=True, stdout=subprocess.DEVNULL)
    out = os.path.join(out_dir, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out + ".tmp.mp4"], check=True)
    os.replace(out + ".tmp.mp4", out)
    with open(os.path.join(out_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(spec["caption"].strip() + "\n")
    for name in os.listdir(tmp):
        os.remove(os.path.join(tmp, name))
    os.rmdir(tmp)
    print(json.dumps({"video": out, "seconds": total, "problems": problems}, ensure_ascii=False))


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
