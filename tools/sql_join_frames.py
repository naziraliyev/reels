from PIL import Image, ImageDraw, ImageFont
import os, sys

W, H = 1080, 1920
OUT = os.path.dirname(os.path.abspath(__file__))
F = "/usr/share/fonts/opentype/inter/"
M = "/usr/share/fonts/truetype/dejavu/"
def f(name, size): return ImageFont.truetype(F + name, size)
def mono(size, bold=False): return ImageFont.truetype(M + ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"), size)

BG = (13, 17, 28)
CARD = (24, 30, 46)
TXT = (236, 240, 248)
MUTED = (140, 150, 172)
A = (56, 189, 248)    # left table - cyan
B = (244, 114, 182)   # right table - pink
HL = (250, 204, 21)   # highlight - yellow
NULLC = (120, 128, 148)

def base():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    return im, d

def center(d, y, text, font, fill=TXT):
    d.text((W // 2, y), text, font=font, fill=fill, anchor="ma")

def venn(im, cy, mode):
    """mode: inner, left, right, full"""
    r = 190
    cxL, cxR = W // 2 - 120, W // 2 + 120
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    mask_l = Image.new("L", (W, H), 0); ImageDraw.Draw(mask_l).ellipse((cxL - r, cy - r, cxL + r, cy + r), fill=255)
    mask_r = Image.new("L", (W, H), 0); ImageDraw.Draw(mask_r).ellipse((cxR - r, cy - r, cxR + r, cy + r), fill=255)
    from PIL import ImageChops
    inter = ImageChops.multiply(mask_l, mask_r)
    fillmask = {"inner": inter, "left": mask_l, "right": mask_r, "full": ImageChops.lighter(mask_l, mask_r)}[mode]
    fillc = Image.new("RGBA", (W, H), HL + (200,))
    layer.paste(fillc, (0, 0), fillmask)
    im.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(im)
    d.ellipse((cxL - r, cy - r, cxL + r, cy + r), outline=A, width=8)
    d.ellipse((cxR - r, cy - r, cxR + r, cy + r), outline=B, width=8)
    d.text((cxL - 90, cy), "A", font=f("Inter-Black.otf", 72), fill=A if mode not in ("left", "full") else BG, anchor="mm")
    d.text((cxR + 90, cy), "B", font=f("Inter-Black.otf", 72), fill=B if mode not in ("right", "full") else BG, anchor="mm")

def table(d, x, y, w, title, color, cols, rows, highlight=None):
    rh = 72
    if not title:
        y -= rh
        d.rounded_rectangle((x, y + rh, x + w, y + rh * (len(rows) + 2)), radius=22, fill=CARD)
    else:
        d.rounded_rectangle((x, y, x + w, y + rh * (len(rows) + 2)), radius=22, fill=CARD)
    d.text((x + 28, y + 20), title, font=f("Inter-Bold.otf", 38), fill=color)
    cw = w // len(cols)
    for i, c in enumerate(cols):
        d.text((x + 28 + i * cw, y + rh + 14), c, font=f("Inter-SemiBold.otf", 30), fill=MUTED)
    for r, row in enumerate(rows):
        yy = y + rh * (r + 2) + 10
        for i, v in enumerate(row):
            isnull = v == "NULL"
            col = NULLC if isnull else TXT
            if highlight and highlight[r] and not isnull:
                col = HL
            d.text((x + 28 + i * cw, yy), v, font=mono(36, bold=not isnull), fill=col)

def code(d, y, lines):
    h = 70 + 60 * len(lines)
    d.rounded_rectangle((60, y, W - 60, y + h), radius=22, fill=(8, 11, 20), outline=(40, 48, 70), width=2)
    for i, (txt, kw) in enumerate(lines):
        # simple keyword coloring: kw words in cyan
        xx = 100
        for word in txt.split(" "):
            colr = HL if word in kw else TXT
            d.text((xx, y + 35 + i * 60), word, font=mono(40, bold=word in kw), fill=colr)
            xx += d.textlength(word + " ", font=mono(40, bold=word in kw))

T = [("Ali", "SQL"), ("Vali", "Flutter")]

def join_scene(name, mode, title, desc, sql, rows):
    im, d = base()
    center(d, 190, title, f("Inter-Black.otf", 96), HL)
    center(d, 310, desc[0], f("Inter-SemiBold.otf", 44))
    center(d, 370, desc[1], f("Inter-SemiBold.otf", 44))
    venn(im, 670, mode)
    d = ImageDraw.Draw(im)
    code(d, 910, sql)
    center(d, 1200, "Natija:", f("Inter-Bold.otf", 40), MUTED)
    table(d, 140, 1260, 800, "", TXT, ["ism", "kurs"], rows)
    im.save(os.path.join(OUT, name + ".png"))

# Scene 1: hook
im, d = base()
center(d, 520, "SQL JOIN", f("Inter-Black.otf", 170), HL)
center(d, 730, "4 turi", f("Inter-Black.otf", 120))
center(d, 880, "30 soniyada", f("Inter-Black.otf", 120))
center(d, 1120, "Suhbatda eng ko'p", f("Inter-SemiBold.otf", 56), MUTED)
center(d, 1195, "so'raladigan mavzu", f("Inter-SemiBold.otf", 56), MUTED)
center(d, 1500, "Oxirigacha ko'ring", f("Inter-Bold.otf", 54), A)
im.save(os.path.join(OUT, "s1.png"))

# Scene 2: the tables
im, d = base()
center(d, 200, "2 ta jadval bor", f("Inter-Black.otf", 92))
table(d, 90, 400, 900, "A: talabalar", A, ["id", "ism"], [("1", "Ali"), ("2", "Vali"), ("3", "Hasan")])
table(d, 90, 900, 900, "B: kurslar", B, ["talaba_id", "kurs"], [("1", "SQL"), ("2", "Flutter"), ("4", "Python")])
center(d, 1440, "Hasan hech qaysi kursda yo'q", f("Inter-SemiBold.otf", 46), MUTED)
center(d, 1510, "Python kursining talabasi (4) yo'q", f("Inter-SemiBold.otf", 46), MUTED)
im.save(os.path.join(OUT, "s2.png"))

ON = ("ON", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "SELECT", "FROM")
join_scene("s3", "inner", "INNER JOIN", ("Faqat ikkala jadvalda", "mos keladiganlar"),
           [("SELECT ism, kurs FROM A", ON), ("INNER JOIN B", ON), ("ON A.id = B.talaba_id;", ON)],
           [("Ali", "SQL"), ("Vali", "Flutter")])
join_scene("s4", "left", "LEFT JOIN", ("Chap jadval to'liq,", "mos kelmasa NULL"),
           [("SELECT ism, kurs FROM A", ON), ("LEFT JOIN B", ON), ("ON A.id = B.talaba_id;", ON)],
           [("Ali", "SQL"), ("Vali", "Flutter"), ("Hasan", "NULL")])
join_scene("s5", "right", "RIGHT JOIN", ("O'ng jadval to'liq,", "mos kelmasa NULL"),
           [("SELECT ism, kurs FROM A", ON), ("RIGHT JOIN B", ON), ("ON A.id = B.talaba_id;", ON)],
           [("Ali", "SQL"), ("Vali", "Flutter"), ("NULL", "Python")])
join_scene("s6", "full", "FULL JOIN", ("Ikkala jadval ham to'liq", "(FULL OUTER JOIN)"),
           [("SELECT ism, kurs FROM A", ON), ("FULL JOIN B", ON), ("ON A.id = B.talaba_id;", ON)],
           [("Ali", "SQL"), ("Vali", "Flutter"), ("Hasan", "NULL"), ("NULL", "Python")])

# Scene 7: CTA
im, d = base()
center(d, 560, "Saqlab qo'ying", f("Inter-Black.otf", 104), HL)
center(d, 700, "imtihon va suhbatda", f("Inter-SemiBold.otf", 56))
center(d, 775, "kerak bo'ladi", f("Inter-SemiBold.otf", 56))
d.rounded_rectangle((140, 1000, W - 140, 1280), radius=30, fill=CARD)
center(d, 1050, "Obuna bo'ling", f("Inter-Black.otf", 72), A)
center(d, 1160, "SQL  ·  Flutter  ·  Python", f("Inter-Bold.otf", 50))
center(d, 1450, "Izohda yozing: qaysi JOIN", f("Inter-SemiBold.otf", 48), MUTED)
center(d, 1515, "sizga qiyin bo'lgan?", f("Inter-SemiBold.otf", 48), MUTED)
im.save(os.path.join(OUT, "s7.png"))
print("ok")
