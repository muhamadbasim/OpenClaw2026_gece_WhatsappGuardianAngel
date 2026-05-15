# 📖 Tutorial — WhatsApp Scam Guardian

Panduan lengkap menjalankan Scam Guardian di dua mode:

- **Mode A — Demo terminal** (offline simulation, cocok untuk record video demo)
- **Mode B — Live WhatsApp** (chat asli via OpenClaw + Baileys, end-to-end)

---

## 🎬 Quick Demo (Mode A — Terminal Simulation)

Jalankan demo di terminal tanpa konek WhatsApp asli.

### Langkah 1 — Aktifkan virtual env

```bash
cd /home/ubuntu
source .venv/bin/activate
```

### Langkah 2 — Jalankan demo

```bash
# Tanpa API key (heuristic mode)
python demo.py --offline

# Dengan GPT-4o-mini (set API key dulu)
export OPENAI_API_KEY=sk-your-key-here
python demo.py
```

5 skenario otomatis akan jalan: pesan biasa, phishing bank, URL legit,
fake admin bonus, dan crypto scam.

---

## 📱 Live WhatsApp Integration (Mode B — OpenClaw)

Flow yang Anda mau: **User chat WhatsApp → OpenClaw gateway → Scam
Guardian agent → Reply otomatis ke user.**

### Arsitektur

```
   📱 User WhatsApp                     🖥 Server (Linux VM)
   ─────────────────                    ────────────────────
                                        ┌────────────────────────────┐
   User kirim pesan ──────WhatsApp──────► OpenClaw Gateway           │
   "URGENT! Verify your                 │  (port 18789)              │
    account at .tk/login"               │                            │
                                        │  ├─ Plugin WhatsApp        │
                                        │  │  (Baileys 7.0)          │
                                        │  │                          │
                                        │  └─ Routing                 │
                                        │     ├─ channel: whatsapp ──►│
                                        │     └─ agent: scam-guardian │
                                        │                            │
                                        │      ┌─────────────────┐   │
                                        │      │ Scam Guardian   │   │
   ◄───────WhatsApp reply────────────────┤      │ Agent (LLM)     │   │
   "🛡 DANGEROUS                         │      │ (GPT-5.5 via    │   │
    Phishing detected                    │      │  GrowthCircle)  │   │
    Confidence: 95%"                     │      └─────────────────┘   │
                                        └────────────────────────────┘
```

### Yang Sudah Saya Setup

| Komponen | Status |
|---|---|
| OpenClaw Gateway (port 18789) | ✅ active |
| Plugin `@openclaw/whatsapp` (Baileys 7.0) | ✅ enabled |
| Channel `whatsapp default` | ✅ linked, connected, healthy |
| Agent `scam-guardian` 🛡 | ✅ created with custom system prompt |
| Routing: WhatsApp → scam-guardian | ✅ bound |
| System prompt (SOUL.md, IDENTITY.md, AGENTS.md) | ✅ written |

### Langkah 1 — Cek Status Komponen

```bash
# Pastikan gateway aktif
systemctl --user status openclaw-gateway | head -5

# Lihat semua agent
openclaw agents list

# Cek koneksi WhatsApp
openclaw channels status
```

Hasil yang diharapkan:
```
- WhatsApp default: enabled, configured, linked, running, connected,
  dm:open, allow:*, health:healthy
```

### Langkah 2 — Login WhatsApp (kalau belum)

Status menunjukkan `linked` artinya sudah ter-pair. Kalau perlu re-link:

```bash
openclaw channels login --channel whatsapp
```

Ikuti instruksi:
1. QR code akan muncul di terminal
2. Buka **WhatsApp di HP** → **Settings → Linked Devices → Link a Device**
3. Scan QR code

> ⚠ **Saran**: gunakan nomor WhatsApp terpisah (eSIM atau nomor kedua),
> bukan nomor pribadi utama. Plugin WhatsApp jalan via Baileys (WhatsApp
> Web protocol), bisa beresiko ban kalau dipakai untuk volume tinggi.

### Langkah 3 — Test Live Chat

Dari **HP lain** (atau minta teman), kirim pesan ke nomor WhatsApp yang
ter-link dengan OpenClaw. Coba pesan ini:

**Test 1 — Pesan benign (harus dapat verdict SAFE):**
```
Halo, apa kabar?
```

**Test 2 — Phishing link (harus DANGEROUS):**
```
URGENT! Your bank account will be closed in 1 hour. Verify at
http://secure-bank-verify.tk/login or send your OTP now.
```

**Test 3 — Crypto scam:**
```
Bro double your BTC! Send 1 BTC to crypto-wallet-verify.xyz get 2 back
```

**Test 4 — Bantuan:**
```
help
```

Setiap pesan akan dibalas dalam ~3-10 detik dengan format:

```
🛡 *Scam Guardian Verdict*

*Threat Level:* DANGEROUS
*Type:* phishing_link
*Confidence:* 95%

_Pesan ini menunjukkan beberapa indikator phishing yang kuat._

*Why I think so:*
• URL pakai TLD .tk yang sering dipakai scammer
• Domain mengandung kata "secure" dan "bank" — pola phishing klasik
• Minta OTP — tidak pernah ada layanan resmi minta OTP via WhatsApp
• Urgency tactic ("1 hour")

*Recommended action:* Jangan klik link, jangan kirim OTP.
Block sender dan laporkan ke bank Anda secara langsung.
```

### Langkah 4 — Monitor & Debug

**Lihat log live (real-time):**
```bash
journalctl --user -u openclaw-gateway -f
```

**Lihat log WhatsApp khusus:**
```bash
openclaw channels logs --channel whatsapp --lines 50
```

**Test agent tanpa WhatsApp** (kirim message langsung lewat CLI):
```bash
openclaw agent --agent scam-guardian \
    --message "URGENT! Verify your bank at http://fake.tk now"
```

---

## 🔧 Customize Behavior

Edit file di `/home/ubuntu/.openclaw/agents/scam-guardian/workspace/`:

| File | Untuk apa |
|---|---|
| `SOUL.md` | Logika klasifikasi, format reply, aturan deteksi |
| `IDENTITY.md` | Nama agent, vibe, emoji |
| `AGENTS.md` | Behavior umum dan red lines |

Setelah edit, agent baca ulang otomatis di pesan berikutnya — **tidak
perlu restart gateway**.

### Contoh: Tambah aturan deteksi baru

Edit `SOUL.md`, di bagian **Detection Heuristics — Always Check**, tambah:

```markdown
For text:
- ...
- Investment fraud: "guaranteed return", "trading signals", "VIP group"
- Romance scam: "I love you" dari unknown sender
```

Simpan, lalu kirim pesan test dari WhatsApp — agent langsung pakai aturan
baru.

---

## 🛡 Combine Both: OpenClaw + Python Pipeline (Optional Advanced)

Kalau ingin gabungkan kedua pendekatan (Mode A + Mode B), Anda bisa:

1. Aktifkan plugin hook `messageReceived` di OpenClaw
2. Plugin itu kirim payload ke HTTP endpoint Python kita (`demo.py` jadi
   FastAPI server)
3. Python pipeline jalankan deteksi heuristik + LLM lalu return verdict
4. OpenClaw kirim verdict balik via WhatsApp

Ini memberikan presisi pipeline Python (PBT, deterministic checks) plus
WhatsApp connectivity OpenClaw. Kalau mau saya implementasi, tinggal bilang.

---

## 🎤 Demo Script untuk Video 2 Menit

**0:00–0:20 — Konteks**
"Banyak penipuan masuk via WhatsApp. Scam Guardian adalah AI agent yang
memeriksa setiap pesan masuk dan kasih verdict langsung."

**0:20–0:40 — Arsitektur**
Tampilkan diagram di README. Highlight: User → OpenClaw → Agent → Reply.

**0:40–1:30 — Live demo**
Kirim 3 pesan dari HP test ke nomor terdaftar:
1. Pesan biasa → "🟢 SAFE"
2. Phishing bank dengan TLD .tk → "🔴 DANGEROUS — phishing_link"
3. Scam OTP → "🔴 DANGEROUS — credential phishing"

**1:30–1:50 — Customization**
Buka `SOUL.md`, tunjukkan rule baru bisa ditambahkan tanpa restart.

**1:50–2:00 — Closing**
"Stack: OpenClaw + Baileys + GPT-5.5. Open source. Setup di bawah 5
menit."

---

## 🚨 Troubleshooting

### "WhatsApp: linked tapi pesan tidak dibalas"
1. Cek routing: `openclaw agents list` — pastikan scam-guardian punya
   `Routing rules: 1`
2. Cek log gateway: `journalctl --user -u openclaw-gateway -n 100`
3. Test agent langsung: `openclaw agent --agent scam-guardian --message "test"`

### "QR code tidak muncul saat login"
```bash
# Hapus auth lama dan login ulang
openclaw channels logout --channel whatsapp
openclaw channels login --channel whatsapp
```

### "Gateway not running"
```bash
systemctl --user start openclaw-gateway
systemctl --user enable openclaw-gateway
```

### "Agent reply tidak sesuai format SOUL.md"
- Pastikan `SOUL.md` ada di workspace yang benar:
  `/home/ubuntu/.openclaw/agents/scam-guardian/workspace/SOUL.md`
- Cek log untuk lihat prompt yang dipakai:
  `openclaw channels logs --channel whatsapp --lines 200`

### "Pesan dari group chat tidak diproses"
By design, untuk demo cuma DM (`groupPolicy: allowlist` default). Untuk
aktifkan group monitoring, edit `~/.openclaw/openclaw.json`:

```json
"channels": {
  "whatsapp": {
    "groupPolicy": "open"
  }
}
```

Lalu restart: `systemctl --user restart openclaw-gateway`.

---

## 📁 Cheatsheet

| Perintah | Fungsi |
|---|---|
| `openclaw channels status` | Cek koneksi WhatsApp |
| `openclaw agents list` | Lihat semua agent |
| `openclaw channels login --channel whatsapp` | QR pairing |
| `openclaw channels logout --channel whatsapp` | Unlink WhatsApp |
| `openclaw channels logs --channel whatsapp --lines 50` | Log WA |
| `openclaw agent --agent scam-guardian --message "..."` | Test agent |
| `journalctl --user -u openclaw-gateway -f` | Live log gateway |
| `systemctl --user restart openclaw-gateway` | Restart gateway |
| `python demo.py --offline` | Demo terminal mode |

---

## 📚 Referensi File Project

```
/home/ubuntu/
├── demo.py                                    # Demo terminal (Mode A)
├── README.md
├── TUTORIAL.md                                # File ini
├── src/                                       # Modul Python (URL extractor, etc.)
└── .openclaw/
    ├── openclaw.json                          # Config OpenClaw + binding
    ├── extensions/whatsapp/                   # Plugin Baileys (built-in)
    └── agents/scam-guardian/
        └── workspace/
            ├── SOUL.md                        # ← EDIT INI untuk ubah behavior
            ├── IDENTITY.md
            └── AGENTS.md
```

Selamat melindungi grup WhatsApp Anda dari scammers. 🛡
