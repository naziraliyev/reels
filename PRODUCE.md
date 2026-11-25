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

### O'rgatuvchi kontent (MAJBURIY — foydalanuvchi talabi)
Video faqat "qiziq quiz" bo'lib qolmasin — tomoshabin undan aniq bilim olib ketsin.
- Har kuni kamida 2 ta video (4 tadan) **dars formatida** bo'lsin: bitta tushunchani bosqichma-bosqich o'rgatadi
  (masalan: "SQL GROUP BY 30 soniyada", "Flutter'da ListView.builder qanday ishlaydi", "Python dict metodlari",
  "SQL'da 3 qadamda JOIN yozish", "Dart'da null safety: ?, !, ??"). Qolganlari quiz bo'lishi mumkin.
  Kunlik navbat: 08:17 dars, 13:17 quiz, 18:17 dars, 23:17 quiz (statistikaga qarab moslashtirish mumkin).
- Dars tuzilishi: hook (muammo/va'da) → tushuncha 1 jumlada → oddiy misol (kod + natija) → amaliy misol
  (real loyihadan: do'kon, talabalar, foydalanuvchilar jadvali; Flutter ekrani) → ko'p uchraydigan xato yoki maslahat →
  "Esda tuting" xulosa sahnasi (`bullets`, 2–3 band) → cta.
- Quiz videolarida ham "Nega?" tushuntirishi + to'g'ri yozish usuli + qachon ishlatish sahnasi bo'lishi shart.
- Har bir video oxirida tomoshabin bitta qoidani yodlab qolsin (xulosa sahnasi yoki cta matnida).
- Darajasi (foydalanuvchi talabi, 2026-11-25: "darslar saviyasi tushib boryapti — yuqoriroq saviyali videolar"):
  **o'rta va yuqori daraja** (junior→middle dasturchi, intervyuga tayyorlanayotganlar). Boshlovchi mavzularini
  (sort/sorted, tuple vergul, append/extend, f-string, oddiy metodlar ro'yxati) ENDI BERMANG.
  Har bir video real ishda yoki texnik intervyuda kerak bo'ladigan narsani o'rgatsin. Mavzu misollari:
  - SQL: window funksiyalar (LAG/LEAD, SUM() OVER — running total, NTILE), CTE va rekursiv CTE, indekslar va EXPLAIN,
    tranzaksiyalar va izolyatsiya darajalari, deadlock, N+1 muammo, normalizatsiya, UPSERT (ON CONFLICT), EXISTS vs IN, self-join.
  - Python: generatorlar va yield, dekoratorlar, context manager (with / __enter__), iterator protokoli, dataclass,
    GIL va threading vs multiprocessing, asyncio, mutable/immutable va xotira (is vs ==, id), __slots__, typing.
  - Flutter/Dart: state management (Provider/Riverpod/BLoC farqi), widget lifecycle, keys (ValueKey/GlobalKey),
    const widget va rebuild optimizatsiyasi, isolates/compute, Stream va StreamBuilder, mixin, extension, sealed class + pattern matching.
  - Umumiy: Big-O amaliy misolda, SOLID, REST vs GraphQL, caching, git rebase vs merge.
  Har bir videoda kamida bitta "nega" (ichki mexanizm) tushuntirilsin, faqat sintaksis emas.
  Atamalarni o'zbekcha izohlang, lekin soddalashtirib mazmunni yo'qotmang.
  Hook'da daraja yorlig'i: "SQL intervyu", "Python o'rta daraja", "Flutter middle" kabi.
- Mavzularni ketma-ket seriya qilib qurish mumkin (masalan, SQL asoslari: SELECT → WHERE → GROUP BY → JOIN),
  caption'da "Seriya: SQL asoslari #3" deb belgilang. topics.md da seriyaning keyingi qismini kuzatib boring.
- Caption'da ham 2–3 qatorlik qisqa konspekt bo'lsin (asosiy qoida + misol), saqlashga undaydigan.

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
- O'rgatuvchi sifatni ham tekshiring: boshlovchi shu videodan nimani o'rgandi? Javob aniq bo'lmasa — sahna qo'shing/tuzating.
- Muammo bo'lsa — spec'ni tuzatib qayta render qiling. Mukammal bo'lmaguncha commit qilmang.

## 5. Saqlash
- `topics.md` ga qator qo'shing: `- <sana> <NN> <topic> — <qisqa sarlavha>`.
- `preview/` papkasi git'ga qo'shilmaydi (.gitignore).
- Commit va `git push` (main). Push 413/xato bersa — avval `git pull --rebase`.

## 6. Joylash
- Push'dan keyin POST.md bo'yicha shu videoni darhol Instagram'ga joylang (`posted.txt`, commit, push).
- Kuniga bir marta (13:17 dagi ishga tushirishda) statistikani yig'ib `stats.md` ni yangilang.
