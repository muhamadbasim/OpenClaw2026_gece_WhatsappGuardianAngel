# 🛡 Whatsapp Guardian Angel

> _Karena yang paling rentan, bukan yang paling kurang hati-hati —_
> _melainkan yang paling tidak siap untuk zaman ini._

---

## 🌙 Bu Ratna

Bu Ratna usia 64. Suaminya sudah lima tahun tiada. Anak-anak besar, sibuk
di kota lain. Setiap hari, WhatsApp adalah jembatannya ke dunia: video
call cucu di hari Minggu, kabar dari adik di kampung, broadcast doa pagi
dari grup pengajian.

Lalu suatu malam, jam 11, sebuah pesan masuk:

> _"URGENT! Akun BCA Ibu akan diblokir dalam 1 jam karena masalah_
> _verifikasi. Untuk menjaga akses tabungan Ibu, mohon verifikasi sekarang_
> _di link berikut: http://bca-secure-verify.tk/login. Atau kirim kode_
> _OTP yang baru saja masuk ke nomor Ibu. Terima kasih, Customer Service_
> _BCA."_

Logo BCA. Bahasa formal. Ada nomor hotline. Ada urgensi.

Tangan Bu Ratna gemetar. Itu uang pensiun mendiang suami — uang yang
harus cukup sampai akhir hidupnya. Kalau benar diblokir, anak-anaknya
pasti akan repot. Lebih baik dia urus sendiri saja.

Dia hampir mengetik OTP yang baru saja masuk lewat SMS.

---

## …tapi

…di kontak WhatsApp Bu Ratna, ada satu nama yang dimasukkan oleh anaknya
beberapa bulan lalu, ditemani pesan singkat:

> _"Bu, kalau ada pesan WhatsApp aneh, terutama yang minta OTP atau_
> _password, forward dulu ke nomor ini ya. Namanya **Guardian Angel**._
> _Dia bisa bantu cek apakah pesan itu beneran atau penipuan."_

Bu Ratna ingat. Sebelum mengetik OTP, dia menahan diri. Dia long-press
pesan itu, klik **Forward**, dan kirim ke kontak bernama 🛡 Guardian Angel.

Lima detik kemudian, balasan datang:

> 🛡 _Scam Guardian Verdict_
>
> _Threat Level:_ **DANGEROUS**
> _Confidence:_ 99%
>
> _Pesan ini sangat berbahaya — kemungkinan besar mencoba mencuri akses_
> _akun BCA Ibu._
>
> _Kenapa saya pikir begitu:_
> • Memakai ancaman mendesak ("akun diblokir 1 jam")
> • Meminta OTP — bank tidak pernah meminta OTP lewat WhatsApp
> • Domain `.tk` dengan kata "secure" dan "verify" untuk meniru BCA
>
> _Recommended action:_ Jangan klik link, jangan kirim OTP. Block pengirim.
> Hubungi BCA hanya lewat aplikasi resmi atau call center 1500888.

Bu Ratna menarik napas. Dia tidak mengetik apa-apa. Dia block nomor itu.
Dia letakkan handphone-nya. Dia pergi membuat teh.

Malam itu, dia tidur dengan tabungan yang masih utuh.

---

## Mengapa Project Ini Ada

Penipuan via WhatsApp di Indonesia bukan masalah teknologi.

Ini masalah **kepercayaan dan kerentanan**.

Penjahat siber tahu persis siapa yang paling mudah ditipu:
- Orang tua yang baru kenal smartphone 5 tahun terakhir
- Ibu rumah tangga yang sibuk dengan anak
- Pekerja yang terburu-buru di jam istirahat
- Anak muda yang panik karena dijanjikan promo terbatas

Mereka semua punya satu kesamaan: **dalam momen panik, mereka tidak punya
waktu untuk verifikasi.**

Yang mereka butuhkan bukan buku panduan keamanan setebal 200 halaman.
Yang mereka butuhkan adalah **teman yang bisa ditanya dalam 5 detik**:
_"Eh ini beneran nggak ya?"_

Project ini dibangun dalam 12 jam untuk OpenClaw Agenthon 2026 oleh tim
**Gece** — tapi niatnya bukan untuk menang lomba. Niatnya adalah membuat
sesuatu yang, kalau dipasang di handphone ibu kami sendiri, akan kami
tidur lebih nyenyak.

Kalau project ini bisa menyelamatkan satu Bu Ratna dari kehilangan uang
pensiunnya — itu sudah cukup.

> 📖 _Cerita lengkap dengan refleksi "untuk siapa", "apa yang Guardian_
> _**bukan** lakukan", dan "cara bantu" — baca di:_
> _**[`docs/CERITA.md`](docs/CERITA.md)**_

---

## 🚀 Mau coba sekarang?

📱 **Simpan nomor di kontak Anda:**
```
Nama   : 🛡 Guardian Angel
Nomor  : +62 823-1399-6991
```

Forward pesan WhatsApp mencurigakan ke nomor itu → balasan verdict dalam
~5 detik. Bisa juga di-add ke grup keluarga / komunitas untuk auto-scan
setiap pesan masuk.

➡ **Tutorial test step-by-step (Bahasa Indonesia):
[`docs/HOW_TO_TEST.md`](docs/HOW_TO_TEST.md)**

🎬 **Mau bikin video tutorial sendiri? Skrip lengkap siap rekam:
[`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md)**

---

**Built for OpenClaw Agenthon 2026** · Indonesian hackathon, 12-hour
sprint · Team **Gece**

---

## 🎯 What It Does

You forward any suspicious WhatsApp message — text, link, screenshot
caption, anything — to the Guardian Angel's WhatsApp number. Within
seconds, it replies with a verdict in **Bahasa Indonesia**:

| Threat Level | Meaning | What you should do |
|---|---|---|
| 🟢 **SAFE** | Normal message, no manipulation indicators | Carry on |
| 🟡 **SUSPICIOUS** | 1–2 weak indicators, could be legitimate | Verify through another channel |
| 🔴 **DANGEROUS** | Multiple strong indicators or one critical | Don't click, don't reply, block |

The agent looks for:

- **URL phishing** — suspicious TLDs (.tk, .ml, .xyz), brand impersonation
  (paypa1, g00gle), URL shorteners hiding the real destination, raw IP
  addresses, phishing keywords in the domain
- **Social engineering** — urgency tactics, fear-based pressure, authority
  impersonation (banks, admins, government)
- **Credential phishing** — any request for OTP, password, PIN, or
  verification code
- **Financial scams** — "double your money", "claim your prize", "send X
  receive 2X back", investment fraud

It works in **Indonesian and English** out of the box (multilingual via the
LLM).

---

## 🏗 Architecture

The system has two layers — a Python pipeline (deterministic, testable)
and a live WhatsApp integration via OpenClaw + Baileys.

```
   📱 User WhatsApp                       🖥 Guardian Server
   ─────────────────                      ──────────────────
                                          ┌───────────────────────────┐
   User forwards a                        │   OpenClaw Gateway        │
   suspicious message  ─────WhatsApp─────►│   :18789                  │
                                          │                           │
                                          │   ├─ WhatsApp plugin      │
                                          │   │  (Baileys 7.0)        │
                                          │   │                        │
                                          │   └─ Routing               │
                                          │      └─► scam-guardian    │
                                          │          (custom agent)   │
                                          │                            │
                                          │   ┌──────────────────┐    │
   ◄─────────reply via WhatsApp───────────┤   │ SOUL.md system   │    │
   "🛡 DANGEROUS                          │   │ prompt drives    │    │
    Phishing detected                     │   │ the LLM verdict  │    │
    Confidence: 95% ..."                  │   └──────────────────┘    │
                                          └───────────────────────────┘
```

For development and CI, the same logic runs as a **standalone Python
demo** (`python-demo/demo.py`) — no WhatsApp account needed, just
heuristics + GPT-4o-mini structured outputs.

---

## ⚡ Quick Start (5 minutes)

### Option 1 — Terminal demo (no WhatsApp setup)

```bash
git clone https://github.com/muhamadbasim/OpenClaw2026_gece_WhatsappGuardianAngel.git
cd OpenClaw2026_gece_WhatsappGuardianAngel/python-demo

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Offline mode (heuristics only, no API key needed)
python demo.py --offline

# Online mode (uses GPT-4o-mini)
export OPENAI_API_KEY=sk-...
python demo.py
```

You'll see five scenarios run automatically: a benign message, a fake
bank phishing attempt, a legitimate marketing URL, a fake admin bonus
scam, and a crypto "double your BTC" fraud. Each one gets a panel with
the agent's reasoning chain and the WhatsApp-formatted alert that
_would_ be posted to the chat.

### Option 2 — Live WhatsApp via OpenClaw

```bash
# 1. Install OpenClaw (https://docs.openclaw.ai)
npm install -g openclaw

# 2. Configure
openclaw configure                     # interactive setup
openclaw plugins enable whatsapp

# 3. Drop in the agent workspace from this repo
mkdir -p ~/.openclaw/agents/scam-guardian/workspace
cp openclaw-workspace/*.md ~/.openclaw/agents/scam-guardian/workspace/

# 4. Register the agent and route WhatsApp to it
openclaw agents add scam-guardian \
    --workspace ~/.openclaw/agents/scam-guardian/workspace \
    --non-interactive
openclaw agents bind --agent scam-guardian --bind whatsapp

# 5. Login WhatsApp (QR code)
openclaw channels login --channel whatsapp

# 6. Done — message your linked WhatsApp number from any other phone
```

Full step-by-step in [`docs/TUTORIAL.md`](docs/TUTORIAL.md).

---

## 🧪 Two Scenarios Worth Recording

If you're shooting a 2-minute demo video, these two beats land best:

### Scene 1 — The save (90 seconds)

1. Open WhatsApp on the demo phone
2. Send the agent: _"URGENT! Akun BCA diblokir dalam 1 jam, verifikasi di
   http://bca-secure-verify.tk/login atau kirim OTP segera"_
3. Wait ~5 seconds — verdict appears with red 🔴 DANGEROUS, full reasoning
   chain, and recommended action. Done.

### Scene 2 — The customization (30 seconds)

1. Open `openclaw-workspace/SOUL.md` in your editor
2. Add a new rule under "Detection Heuristics" — e.g. _"Investment fraud
   keywords: 'guaranteed return', 'VIP signal group'"_
3. Save. No restart. Send the agent a message containing one of those
   phrases — it picks up the new rule on the next message.

That's the whole pitch: **a security agent you can teach in plain markdown.**

---

## 📁 Repository Layout

```
.
├── README.md                       ← you are here
├── docs/
│   └── TUTORIAL.md                 ← step-by-step setup, both modes
├── spec/
│   ├── requirements.md             ← user stories + acceptance criteria
│   ├── design.md                   ← architecture, data models, properties
│   └── tasks.md                    ← 61-task implementation plan
├── openclaw-workspace/             ← drop-in OpenClaw agent definition
│   ├── SOUL.md                     ← classification rules, output format
│   ├── IDENTITY.md                 ← agent persona
│   └── AGENTS.md                   ← workspace behavior
└── python-demo/                    ← standalone Python pipeline
    ├── demo.py                     ← runnable terminal demo
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .env.example
    ├── src/
    │   ├── url_extractor.py        ← regex URL extraction
    │   ├── url_resolver.py         ← async redirect chain follower
    │   ├── models.py               ← ThreatLevel, ThreatType, dataclasses
    │   ├── config.py               ← Pydantic settings loader
    │   ├── storage_models.py       ← SQLAlchemy ThreatRecord
    │   └── threat_log.py           ← persistent threat log + retry queue
    └── tests/
        └── test_threat_log.py      ← property-based tests (Hypothesis)
```

---

## 🔬 Why two implementations?

Because hackathons reward both **demo polish** and **engineering depth**:

- **`python-demo/`** — runnable in 30 seconds, no external accounts, ideal
  for the recorded video and judges who want to see the pipeline run
  locally. Includes property-based tests covering URL completeness,
  redirect chain bounds, threat level totality, and confidence-score
  bounds.
- **`openclaw-workspace/`** — the production-feel integration. The agent
  receives real WhatsApp messages via Baileys (the same library used by
  most WhatsApp open-source bots) and replies as a real WhatsApp contact.
  Editing markdown changes behavior live.

The Python demo is what you'd ship to a CI pipeline. The OpenClaw setup
is what you'd actually run in production.

---

## 🧰 Tech Stack

| Layer | Tech |
|---|---|
| Runtime (Python) | Python 3.12, asyncio |
| LLM (Python demo) | OpenAI 2.x with `chat.completions.parse` (structured outputs), Pydantic v2 |
| LLM (OpenClaw) | GPT-5.5 via GrowthCircle API |
| WhatsApp connector | OpenClaw 2026.5.12 + Baileys 7.0 |
| Storage | SQLite + SQLAlchemy 2.0 (optional, for persistent threat logging) |
| Testing | pytest + Hypothesis (property-based tests) |
| UI | Rich (terminal demo panels) |

No paid APIs required for the offline demo.

---

## 🌏 Why this matters in Indonesia

Penipuan via WhatsApp is **the** dominant scam channel in Indonesia:

- Fake BCA / Mandiri / BRI account-block notices asking for OTP
- "Selamat Anda menang giveaway" lottery scams
- Crypto doubling schemes targeting younger users
- "Kurir paket" tarik-OTP scams during e-commerce sale events

Older users (parents, grandparents) get hit hardest. The Guardian Angel
is designed to be **the second pair of eyes** — you forward anything that
feels off, you get a verdict in the same chat window where the scam
arrived. No new app to learn. No new login.

---

## 🚧 Roadmap

- [x] Multi-agent pipeline (Link Scanner + Message Analyzer + Alert Agent)
- [x] OpenClaw + Baileys WhatsApp integration
- [x] Property-based tests for invariants
- [x] Bilingual EN/ID detection
- [ ] Group chat monitoring (currently DM-only by design)
- [ ] Image OCR for screenshot scams
- [ ] VirusTotal + URLScan.io enrichment for live URL scoring
- [ ] Weekly summary reports per group
- [ ] Whitelist of known-good domains per user

---

## 🤝 Credits

Built by **Team Gece** for the OpenClaw Agenthon 2026.

- **Framework:** [OpenClaw](https://docs.openclaw.ai) — multi-channel agent
  runtime
- **WhatsApp:** [Baileys](https://github.com/WhiskeySockets/Baileys) — Web
  protocol implementation
- **LLM:** OpenAI structured outputs + GrowthCircle GPT-5.5
- **Inspiration:** every parent, grandparent, and friend who's ever
  almost clicked the wrong link

---

## 📜 License

MIT. Use it, fork it, teach your own family's WhatsApp to fight back.

---

> 🛡 _Stay sharp. The next message could be the one._
