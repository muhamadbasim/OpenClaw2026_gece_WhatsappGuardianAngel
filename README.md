# 🛡 Whatsapp Guardian Angel

> _An AI agent that watches your WhatsApp inbox like a guardian angel —
> reading every suspicious message, sniffing out scams, and warning you
> before you click the wrong link._

**Built for OpenClaw Agenthon 2026** · Indonesian hackathon, 12-hour sprint
· Team **Gece**

---

## 🌙 The Story

It was a Tuesday night. Sari, 62, was about to pour her tea when her phone
buzzed.

> _"URGENT! Akun BCA Anda akan diblokir dalam 1 jam. Verifikasi sekarang_
> _di http://bca-secure-verify.tk/login atau kirim kode OTP Anda sekarang_
> _untuk menjaga akses."_

Her hands trembled. The bank's name was right. The urgency felt real. She
almost typed the OTP from her latest SMS into the chat.

But before she could, another message appeared in the same WhatsApp window —
from a contact called **🛡 Guardian Angel**:

> 🛡 _Scam Guardian Verdict_
>
> _Threat Level:_ **DANGEROUS**
> _Type:_ phishing_link
> _Confidence:_ 95%
>
> _This message has multiple strong phishing indicators._
>
> _Why I think so:_
> • URL uses .tk TLD — frequently used by scammers
> • Domain contains "secure", "bank", "verify" — classic phishing pattern
> • Asks for OTP — no legitimate bank ever asks for OTP via WhatsApp
> • Urgency tactic ("1 hour") meant to bypass critical thinking
>
> _Recommended action:_ Do NOT click the link. Do NOT share your OTP.
> Block the sender and call your bank's official number directly.

Sari put her phone down. She poured the tea. Disaster averted, on a
Tuesday night, by an AI agent that never sleeps.

This is **Whatsapp Guardian Angel**.

---

## 🎯 What It Does

You forward any suspicious WhatsApp message — text, link, screenshot
caption, anything — to the Guardian Angel's WhatsApp number. Within
seconds, it replies with a verdict:

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

### Want to just **try the live bot** right now?

The Guardian Angel is already deployed and listening on
**+62 823-1399-6991**. Save the number and message it from any WhatsApp.
See **[`docs/HOW_TO_TEST.md`](docs/HOW_TO_TEST.md)** for ready-to-copy
test messages.

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
