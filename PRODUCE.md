# Bitta yangi Reels tayyorlash (har 5 soatda ishlaydigan vazifa)

Maqsad: Instagram @naziraliyevurinboy uchun **yuqori sifatli, original** o'quv Reels.
Mavzular FAQAT: Dasturlash / SQL / Flutter (Dart). Til: o'zbek (lotin).

## 1. Qaysi kun uchun
- Vaqt zonasi: Asia/Tashkent. Joylash kunlari: dushanba–shanba, 13:30.
- Maqsad sana = 13:30 hali o'tmagan eng yaqin dushanba–shanba kuni
  (bugun Du–Sha bo'lib, soat 13:30 dan oldin bo'lsa — bugun; aks holda keyingi Du–Sha kuni).
- `queue/<YYYY-MM-DD>/` ichida allaqachon 4 ta video papkasi bo'lsa — **hech narsa qilmang, to'xtang**.
- Aks holda keyingi raqamli papkani yarating: `queue/<sana>/01`, `02`, `03`, `04`.

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
