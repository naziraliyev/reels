# Instagram'ga joylash (Du–Sha 13:30 vazifasi)

1. Bugungi sana (Asia/Tashkent) papkasi: `queue/<YYYY-MM-DD>/`. Bo'lmasa yoki bo'sh bo'lsa — hech narsa joylamang, xabar bering.
2. Har bir `NN` papka uchun (01 dan boshlab tartib bilan), agar `posted.txt` YO'Q bo'lsa:
   - video havolasi: `https://raw.githubusercontent.com/naziraliyev/reels/main/queue/<sana>/<NN>/video.mp4`
     (avval HEAD so'rov bilan 200 qaytishini tekshiring)
   - Windsor.ai `execute_action`: connector `instagram`, account `17841447411509990`, action `create_video_post`,
     params: `video_url`, `caption` = `caption.txt` matni, `share_to_feed: true`, `thumb_offset: 1000`.
   - Muvaffaqiyatli bo'lsa `posted.txt` ga media id va vaqtni yozing.
   - Postlar orasida ~1 daqiqa kuting.
3. `posted.txt` fayllarini commit va push qiling.
4. Statistika: Windsor `get_data` (instagram, oxirgi 30 kun) — har bir media uchun
   media_views, media_reach, media_like_count, media_comments_count, media_saved, media_shares,
   media_reel_avg_watch_time, media_reel_skip_rate, media_caption. Natijani `stats.md` ga jadval qilib yozing
   va qisqa xulosa qo'shing: qaysi mavzu/format yaxshi ishladi — keyingi videolar shunga moslashadi.
