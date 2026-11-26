"""Reels statistikasini tahlil qilish (har bir ishga tushirishda).

Usage:  python3 tools/analyze.py WINDSOR_JSON > stats.md
WINDSOR_JSON — Windsor get_data natijasi (instagram, last_30dT) fayli: {"data": [...]} yoki [...].
Kerakli maydonlar: media_id, timestamp, media_views, media_reach, media_like_count,
media_comments_count, media_saved, media_shares, media_reel_avg_watch_time, media_reel_skip_rate.

media_id -> queue/<sana>/<NN>/posted.txt orqali video, spec.json (topic, lang) va topics.md (dars/quiz) bilan bog'lanadi.
Ball (score) = ko'rish + 10*like + 15*saqlash + 15*ulashish + 5*izoh. Yo'nalish/format bo'yicha o'rtachalar
faqat >= 24 soatlik videolardan hisoblanadi (yangi videolar ko'rishni hali yig'magan).
"""
import json, os, re, sys, glob
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    d = json.load(open(path))
    return d["data"] if isinstance(d, dict) else d


def videos():
    out = {}
    topics = open(os.path.join(ROOT, "topics.md")).read().splitlines()
    for p in glob.glob(os.path.join(ROOT, "queue/*/*/posted.txt")) + glob.glob(os.path.join(ROOT, "queue/*/posted.txt")):
        txt = open(p).read()
        m = re.search(r"(\d{15,})", txt)
        if not m:
            continue
        d = os.path.dirname(p)
        rel = os.path.relpath(d, os.path.join(ROOT, "queue"))
        spec = {}
        if os.path.exists(os.path.join(d, "spec.json")):
            spec = json.load(open(os.path.join(d, "spec.json")))
        topic = spec.get("topic", "")
        line = ""
        if topic:
            line = next((l for l in topics if " " + topic + " " in l + " "), "")
        if not topic:
            parts = rel.split("/")
            line = next((l for l in topics if l.startswith("- " + parts[0])), "")
            mt = re.match(r"- \S+ (?:\d\d )?(\S+)", line)
            topic = mt.group(1) if mt else rel
        low = line.lower()
        fmt = "quiz" if "(quiz)" in low or "quiz:" in low else ("dars" if "dars" in low else "boshqa")
        lang = spec.get("lang") or topic.split("-")[0]
        cat = {"dart": "Flutter/Dart", "flutter": "Flutter/Dart", "sql": "SQL", "python": "Python",
               "js": "JS"}.get(lang, "Boshqa")
        if topic.startswith("flutter"):
            cat = "Flutter/Dart"
        level = "middle" if rel[:10] >= "2026-11-25" else "boshlang'ich"
        out[m.group(1)] = dict(rel=rel, topic=topic, fmt=fmt, cat=cat, level=level)
    return out


def main():
    rows = load(sys.argv[1])
    vids = videos()
    now = datetime.now(timezone.utc)
    items = []
    for r in rows:
        v = vids.get(str(r.get("media_id")))
        if not v:
            continue
        ts = r.get("timestamp")
        age = (now - datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")).total_seconds() / 3600 if ts else 999
        g = lambda k: r.get(k) or 0
        it = dict(v, views=g("media_views"), reach=g("media_reach"), likes=g("media_like_count"),
                  comments=g("media_comments_count"), saves=g("media_saved"), shares=g("media_shares"),
                  watch=g("media_reel_avg_watch_time") / 1000, skip=g("media_reel_skip_rate"), age=age)
        it["score"] = it["views"] + 10 * it["likes"] + 15 * it["saves"] + 15 * it["shares"] + 5 * it["comments"]
        it["eng"] = 100 * (it["likes"] + it["saves"] + it["shares"]) / it["views"] if it["views"] else 0
        items.append(it)
    items.sort(key=lambda x: -x["score"])
    p = print
    tz = datetime.now().astimezone()
    p("# Instagram Reels statistikasi (oxirgi 30 kun, Windsor.ai)")
    p(f"Yangilangan: {now.strftime('%Y-%m-%d %H:%M')} UTC. Avtomatik: `tools/analyze.py`. "
      "Ball = ko'rish + 10×like + 15×saqlash + 15×ulashish + 5×izoh. Faol % = (like+saqlash+ulashish)/ko'rish.")
    p()

    def agg(key):
        groups = {}
        for it in items:
            if it["age"] < 24:
                continue
            groups.setdefault(it[key], []).append(it)
        res = []
        for k, lst in groups.items():
            n = len(lst)
            res.append((k, n, sum(x["views"] for x in lst) / n, sum(x["likes"] for x in lst) / n,
                        sum(x["saves"] for x in lst) / n, sum(x["score"] for x in lst) / n,
                        sum(x["eng"] for x in lst) / n, sum(x["watch"] for x in lst) / n))
        res.sort(key=lambda x: -x[5])
        p(f"| {key} | soni | o'rt. ko'rish | o'rt. like | o'rt. saqlash | o'rt. ball | faol % | o'rt. tomosha (s) |")
        p("|---|---|---|---|---|---|---|---|")
        for k, n, v, l, s, sc, e, w in res:
            p(f"| {k} | {n} | {v:.0f} | {l:.1f} | {s:.1f} | {sc:.0f} | {e:.1f} | {w:.1f} |")
        p()
        return res

    p("## Yo'nalish × format reytingi (≥ 24 soatlik videolar)")
    for it in items:
        it["cat_fmt"] = f"{it['cat']} {it['fmt']}"
    ranking = agg("cat_fmt")
    p("## Yo'nalish bo'yicha")
    agg("cat")
    p("## Format bo'yicha")
    agg("fmt")
    p("## Daraja bo'yicha (middle = 2026-11-25 dan keyin)")
    agg("level")

    p("## Top-10 video (ball bo'yicha)")
    p("| # | Sana/NN | Mavzu | Format | Ko'rish | Like | Saqlash | Ulashish | Ball | Faol % |")
    p("|---|---|---|---|---|---|---|---|---|---|")
    for i, it in enumerate(items[:10], 1):
        p(f"| {i} | {it['rel']} | {it['topic']} | {it['fmt']} | {it['views']} | {it['likes']} | {it['saves']} | "
          f"{it['shares']} | {it['score']} | {it['eng']:.1f} |")
    p()
    p("## Barcha videolar")
    p("| Sana/NN | Mavzu | Format | Yosh (soat) | Ko'rish | Qamrov | Like | Izoh | Saqlash | Ulashish | O'rt. tomosha (s) | 3s skip | Ball |")
    p("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for it in sorted(items, key=lambda x: x["rel"], reverse=True):
        p(f"| {it['rel']} | {it['topic']} | {it['fmt']} | {it['age']:.0f} | {it['views']} | {it['reach']} | {it['likes']} | "
          f"{it['comments']} | {it['saves']} | {it['shares']} | {it['watch']:.1f} | {it['skip']:.0%} | {it['score']} |")
    p()
    missing = sorted(set(vids) - {str(r.get('media_id')) for r in rows})
    if missing:
        p("Windsor javobida yo'q: " + ", ".join(vids[m]["rel"] for m in missing))
        p()
    p("## Avtomatik tavsiya (keyingi mavzular uchun)")
    if ranking:
        best = [r[0] for r in ranking[:2]]
        worst = [r[0] for r in ranking[-2:] if r[1] >= 2]
        p(f"- Eng kuchli yo'nalish×format: **{best[0]}**" + (f", keyin **{best[1]}**" if len(best) > 1 else "") + ".")
        if worst:
            p(f"- Eng zaif: {', '.join(worst)} — kamroq bering yoki hook/formatni o'zgartiring.")
    top = items[:5]
    p("- Top-5 videolar mavzulari (shu uslub va chuqurlikka yaqin yangi mavzu tanlang): "
      + ", ".join(f"{t['topic']} ({t['fmt']})" for t in top) + ".")


if __name__ == "__main__":
    main()
