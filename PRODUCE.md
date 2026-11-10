# Bitta yangi Reels tayyorlash va joylash (har kuni, har 5 soatda: 08:17, 13:17, 18:17, 23:17)

Maqsad: Instagram @naziraliyevurinboy uchun **yuqori sifatli, original** o'quv Reels.
Mavzular FAQAT: Dasturlash / SQL / Flutter (Dart). Til: o'zbek (lotin).

## 1. Papka
- Vaqt zonasi: Asia/Tashkent. Sana = bugun.
- `queue/<bugun>/` ichida keyingi bo'sh raqamli papkani yarating (`01`, `02`, ...).
- Agar `queue/` da `posted.txt` siz qolgan eski video bo'lsa (oldingi ishga tushirishdan), avval uni POST.md bo'yicha joylang,
  keyin yangi video yasang va uni ham joylang.

## 2. Mavzu tanlash
- `topics.md` ni o'qing — u yerdagi mavzularni TAKRORLAMANG.
- Shu sanadagi boshqa videolar bilan bir xil yo'nalish bo'lmasin (aralash: SQL, Flutter, umumiy dasturlash).
- `stats.md` bo'lsa — yaxshi ishlagan mavzu/format turiga yaqinroq mavzu tanlang.
- Yaxshi formatlar: "X ning 3 turi", "Ko'p uchraydigan xato", "Suhbat savoli", "A vs B", "1 qatorli trick",
  "Boshlovchi bilishi shart bo'lgan ...". Trend formatlardan ilhom oling, kontent esa doim original bo'lsin.

## 3. Spec yozish va render
- `tools/example_spec.json` namunasidek `queue/<sana>/<NN>/spec.json` yozing (sahna turlari `tools/render.py` boshida).
- Qoidalar: 25–40 soniya; 1-sahna `hook` (3–3.5 s, kuchli savol/va'da); oxirgi sahna `cta`;
  har sahnada kam matn, katta shrift; kod ≤ 14 qator, qator ≤ 46 belgi; kod HAQIQATDAN to'g'ri va ishlaydigan bo'lsin.
  Sahna davomiyligi: o'qishga yetadigan (matn ~ 0.35 s/so'z, kod sahnasi 6–8 s).
- `lang` ni mavzuga mos qo'ying (sql/dart/python/js), `accent` ni har xil qiling
  (#facc15 sariq, #38bdf8 havorang, #a78bfa binafsha, #4ade80 yashil, #fb923c to'q sariq).
- Caption: 1-qator hook + emoji, 2–3 qator qiymat, "📌 Saqlab qo'ying", savol bilan izohga chaqiruv,
  obuna chaqiruvi, keyin 8–12 ta mos hashtag (#dasturlash #uzbekistan va mavzuga xos teglar).
- Render: `python3 tools/render.py queue/<sana>/<NN>/spec.json queue/<sana>/<NN>`
  (natija JSON'idagi `problems` bo'sh bo'lishi shart).

## 4. Sifat nazorati (majburiy)
- `queue/<sana>/<NN>/preview/*.png` dagi HAR BIR kadrni Read bilan ko'ring:
  matn kesilmagan, ustma-ust tushmagan, o'qilishi oson, imlo xatosi yo'q, kod to'g'ri.
- Muammo bo'lsa — spec'ni tuzatib qayta render qiling. Mukammal bo'lmaguncha commit qilmang.

## 5. Saqlash
- `topics.md` ga qator qo'shing: `- <sana> <NN> <topic> — <qisqa sarlavha>`.
- `preview/` papkasi git'ga qo'shilmaydi (.gitignore).
- Commit va `git push` (main). Push 413/xato bersa — avval `git pull --rebase`.

## 6. Joylash
- Push'dan keyin POST.md bo'yicha shu videoni darhol Instagram'ga joylang (`posted.txt`, commit, push).
- Kuniga bir marta (13:17 dagi ishga tushirishda) statistikani yig'ib `stats.md` ni yangilang.
