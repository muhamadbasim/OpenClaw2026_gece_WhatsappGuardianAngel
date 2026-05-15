# 📝 Devpost Submission Content

Konten siap copy-paste ke form Devpost.

---

## 🎯 General Info

**Project name** (49 chars):
```
Whatsapp Guardian Angel — AI Anti-Scam Indonesia
```

**Elevator pitch** (165 chars):
```
AI yang jaga keluarga dari penipuan WhatsApp. Forward pesan mencurigakan ke kontak Guardian Angel → verdict dalam 5 detik. Untuk Bu Ratna, dan ibu kita semua. 🛡
```

**Thumbnail:** `docs/thumbnail.png` (1200×800, 3:2 ratio)

---

## ✨ Inspiration

Setiap hari di Indonesia, ribuan pesan penipuan masuk ke WhatsApp dengan pola yang sama: nama bank besar, urgensi 1 jam, link mencurigakan, permintaan OTP. Yang paling sering jadi korban bukan hacker atau orang yang kurang teliti — melainkan orang tua kita, yang baru kenal smartphone 5-10 tahun terakhir.

Kami punya satu cerita yang jadi kompas project ini: **Bu Ratna**, 64 tahun, janda, tabungan pensiun mendiang suami nyaris hilang karena pesan phishing BCA palsu. Dia hampir mengetik OTP — sebelum dia ingat, anaknya pernah bilang: _"Bu, kalau ada pesan aneh, forward dulu ke nomor ini ya."_

Kami sadar masalah ini bukan masalah teknologi. Ini masalah **kepercayaan dan kerentanan**. Yang dibutuhkan orang tua kita bukan buku panduan keamanan setebal 200 halaman — tapi teman digital yang bisa ditanya dalam 5 detik: _"Eh ini beneran nggak ya?"_

Niat kami sederhana: kalau Guardian Angel dipasang di handphone ibu kami sendiri, kami bisa tidur lebih nyenyak.

---

## 🛡 What it does

**Whatsapp Guardian Angel** adalah satu kontak WhatsApp (`+62 823-1399-6991`) yang berperan sebagai analis keamanan otomatis 24/7.

**Cara pakai:**
1. User forward pesan WhatsApp mencurigakan ke kontak Guardian Angel
2. Dalam ~5 detik, balasan datang dengan verdict terstruktur

**Output verdict berisi:**
- 🟢 **SAFE** / 🟡 **SUSPICIOUS** / 🔴 **DANGEROUS** — threat level
- Tipe ancaman (`phishing_link`, `social_engineering`, `bank_impersonation`, `credential_phishing`, dll)
- Tingkat keyakinan AI (0–100%)
- Reasoning chain — alasan kenapa pesan dianggap berbahaya
- Recommended action — saran konkret (jangan klik, block sender, hubungi call center resmi)

**Modes operasi:**
- **DM 1-on-1** — full verdict untuk setiap pesan
- **Group chat** — auto-scan tiap pesan, tapi diam untuk SAFE, reply singkat untuk SUSPICIOUS, reply lengkap untuk DANGEROUS (tidak banjiri grup)

**Bahasa output:** selalu Bahasa Indonesia, terlepas dari bahasa input.

**Yang dideteksi:** TLD mencurigakan (.tk, .xyz), shortener (bit.ly), brand impersonation (paypa1, bca-secure-verify), permintaan OTP/PIN/password, urgency tactics, financial lures, authority impersonation.

---

## 🏗 How we built it

**Stack:**
- **OpenClaw 2026.5.12** sebagai agent runtime + multi-channel router
- **Baileys 7.0** (via OpenClaw plugin) untuk koneksi WhatsApp Web protocol
- **GPT-5.5** via GrowthCircle API sebagai brain LLM
- **SOUL.md** — single markdown file sebagai system prompt
- **Python 3.12 + asyncio** untuk demo pipeline (terminal mode)
- **OpenAI 2.x structured outputs** + **Pydantic v2** untuk verdict schema
- **SQLAlchemy 2.0 + Hypothesis** untuk threat log dengan property-based tests

**Arsitektur:**
```
User WhatsApp ──► OpenClaw Gateway ──► Baileys plugin ──► Routing rule
                                                                │
                                                                ▼
                                                       scam-guardian agent
                                                                │
                                                                ▼
                                                        GPT-5.5 + SOUL.md
                                                                │
                                                                ▼
                                                         Verdict reply
```

**Workflow yang kami pakai:**
1. **Spec-driven** — tulis `requirements.md` (9 user stories, EARS format) dan `design.md` (10 correctness properties testable) dulu, baru coding
2. **Dual implementation** — Python demo standalone untuk testability, plus OpenClaw workspace untuk live WhatsApp
3. **Markdown-as-config** — semua behavior agent didefinisikan di `SOUL.md`. Edit file → live reload, tanpa restart gateway

**Insight kunci:** kami tidak butuh agent framework rumit. Cukup satu LLM + system prompt yang well-crafted + connector WhatsApp yang reliable. Total ~400 baris Python untuk demo, ditambah 200 baris markdown untuk SOUL.md.

---

## 🚧 Challenges we ran into

**1. Routing rule yang tidak ter-trigger**
Setelah register agent `scam-guardian` dan bind ke channel WhatsApp, pesan dari nomor test malah masih di-route ke agent default `main`. Akar masalahnya: session WhatsApp pre-existing dari sebelum binding aktif. Solusi: restart gateway untuk clean-load routing rules.

**2. LLM tidak konsisten balas Bahasa Indonesia**
Iterasi pertama SOUL.md cuma bilang "balas dalam Bahasa Indonesia kecuali user nulis Inggris". LLM tetap follow bahasa input. Solusinya: tambah aturan paksa di paling atas SOUL.md dengan ⚠ emoji + 2 contoh konkret verdict (SAFE & DANGEROUS) dalam Bahasa Indonesia. Setelah itu LLM konsisten.

**3. Group chat policy — kapan diam, kapan respond?**
Default behavior agent adalah balas tiap pesan. Tapi di grup, ini bikin spam. Solusi: tulis aturan di SOUL.md — diam untuk pesan SAFE, reply singkat untuk SUSPICIOUS, reply lengkap untuk DANGEROUS. Plus mode `requireMention: false` untuk auto-scan tanpa mention.

**4. Tone yang seimbang**
Mudah jatuh ke dua ekstrem: terlalu teknis (jargon yang lansia tidak paham) atau terlalu fearmongering (mirip scammer aslinya). Solusi: tulis 2 contoh full verdict di SOUL.md sebagai anchor, plus rule "jangan alarmist untuk pesan benign".

**5. Time pressure 12 jam**
12 jam tidak cukup untuk implementasi 61 task plan original. Pivot di tengah: dari "build full system" jadi "build minimal demo + drop-in agent yang bisa dipakai langsung". Hasilnya lebih realistis untuk hackathon.

**6. Sensitif data WhatsApp**
Plugin Baileys menyimpan auth state (creds.json) yang sangat sensitif. Saat push ke GitHub, kami audit `.gitignore` ekstra hati-hati untuk pastikan tidak ada credential, session, atau API key yang ter-commit.

---

## 🏆 Accomplishments that we're proud of

**1. Bot live, bukan mockup.** Setiap orang bisa langsung simpan nomor `+62 823-1399-6991` di HP mereka dan test sekarang juga. Tidak perlu install apapun.

**2. Bilingual detection.** Pesan phishing dalam Inggris, Indonesia, atau campuran semua dideteksi. Verdict selalu dikembalikan dalam Bahasa Indonesia natural — bukan terjemahan kaku.

**3. UX yang hangat, bukan technical.** README utama dibuka dengan cerita Bu Ratna, bukan dengan diagram arsitektur. CERITA.md menjelaskan niat project tanpa jargon. HOW_TO_TEST.md ditulis untuk non-developer.

**4. Spec-driven dengan property-based testing.** 10 correctness properties (URL extraction completeness, threat level totality, confidence bounds, redirect chain bounds, dst) — semua testable dengan Hypothesis. 6/6 tests pass.

**5. Markdown-as-config.** Customize behavior Guardian Angel cukup dengan edit satu file `SOUL.md`. Live reload, tidak perlu restart. Cocok untuk non-coder.

**6. Repo yang siap fork.** Drop-in workspace, Docker compose, .env.example, terminal demo, full documentation. Siapapun bisa setup Guardian Angel sendiri dengan nomor WhatsApp mereka.

**7. Niat dan output sejalan.** Setiap dokumen, dari README sampai SOUL.md, semua mengarah ke satu tujuan: melindungi yang paling rentan. Tidak ada feature creep.

---

## 📚 What we learned

**1. LLM dengan prompt yang dirancang baik > agent framework rumit.** Kami sempat planning pakai LangChain dengan multi-agent pattern (Link Scanner Agent, Message Analyzer Agent, Alert Agent terpisah). Akhirnya cukup 1 LLM + 1 SOUL.md dengan instruksi clear. Hasilnya lebih maintainable dan justru lebih akurat.

**2. OpenClaw drop-in architecture sangat powerful.** Membuat agent baru = bikin folder dengan 3 markdown file. Tidak ada compile, tidak ada deploy. Iterasi behavior dalam hitungan detik.

**3. Steering LLM ke bahasa tertentu butuh paksaan eksplisit.** "Tolong balas Bahasa Indonesia" tidak cukup. Harus: aturan di paling atas, contoh konkret, plus negative example.

**4. Storytelling > spec sheet.** Cerita Bu Ratna lebih menggerakkan daripada bullet list fitur. Judges, user, dan tester semua respond ke narasi yang menyentuh.

**5. Ship the empathy first, the tech second.** Project ini bisa saja jadi "yet another phishing detector". Yang membedakan: kami menulis untuk Bu Ratna, bukan untuk engineer. Setiap UX decision lewat filter "apakah ini berguna untuk lansia?"

**6. Property-based tests menemukan edge case lebih dari unit tests.** Hypothesis menemukan kasus URL dengan trailing punctuation, redirect chain edge cases, dan confidence score boundary issues yang kami tidak pernah pikirkan.

**7. Bahasa Indonesia di tech masih kurang dilayani.** Sebagian besar tools security berbasis Inggris. Membangun yang native Indonesia (verdict, dokumentasi, error message) terasa berdampak nyata.

---

## 🚀 What's next for Whatsapp Guardian Angel — AI Anti-Scam Indonesia

**Roadmap dekat (1-2 minggu):**

- 📸 **Image OCR** — banyak scam dikirim sebagai screenshot (misalnya "transfer dulu ke rekening ini"). Integrasikan OCR (Tesseract atau Google Vision) untuk ekstrak teks dari gambar, lalu analisis seperti pesan biasa.

- 🔍 **VirusTotal + URLScan.io enrichment** — saat ini deteksi URL berbasis heuristik (TLD, kata kunci domain). Tambah live API call untuk reputation score real-time.

- 📊 **Threat dashboard untuk admin grup** — admin bisa lihat statistik mingguan: total threats di grup, jenis paling sering, anggota yang paling sering jadi target.

**Roadmap menengah (1-3 bulan):**

- 🌐 **Multi-account support** — saat ini 1 nomor WhatsApp = 1 instance. Kami mau buat self-hosted version sehingga setiap keluarga bisa punya Guardian Angel sendiri dengan nomor mereka.

- 🧠 **Fine-tuned model untuk konteks Indonesia** — train model lebih kecil dengan dataset scam Indonesia (BCA, BRI, Mandiri, Shopee Express, JNE, dll). Lebih cepat, lebih akurat, bisa run di edge.

- 🤝 **Integrasi dengan Kominfo / OJK** — kalau Guardian Angel deteksi nomor scammer dengan confidence tinggi, otomatis lapor ke channel resmi pelaporan penipuan.

- 📱 **Mobile app companion** — app untuk anak yang setup Guardian Angel di HP orang tua mereka, plus dashboard untuk lihat pesan apa saja yang sudah diselamatkan.

**Roadmap jangka panjang:**

- 🏫 **Kampanye literasi digital** — kerja sama dengan komunitas senior, posyandu lansia, perkumpulan ibu PKK. Pasang Guardian Angel sebagai bagian dari pelatihan WhatsApp untuk lansia.

- 🌏 **Ekspansi ASEAN** — Bahasa Melayu (Malaysia), Tagalog (Filipina), Vietnamese. Phishing pattern di ASEAN punya banyak kemiripan, banyak yang bisa di-reuse.

- 📜 **Open dataset scam Indonesia** — kumpulkan (dengan persetujuan user) sample pesan scam Indonesia dan rilis sebagai open dataset untuk riset keamanan.

Tujuan akhir kami sederhana: dalam 2 tahun, **setiap orang Indonesia yang punya WhatsApp** punya akses ke teman digital yang melindungi mereka dari penipuan — gratis, sederhana, dan dalam bahasa mereka sendiri.

🛡 _Lima detik kadang cukup untuk menyelamatkan tabungan setahun. Dan kebaikan itu, harusnya milik semua orang._

— **Tim Gece**, OpenClaw Agenthon 2026
