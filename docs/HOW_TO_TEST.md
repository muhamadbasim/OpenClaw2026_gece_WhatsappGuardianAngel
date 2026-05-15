# 🧪 Cara Test Whatsapp Guardian Angel

Tutorial paling singkat: **simpan nomor, kirim pesan, lihat balasan.**

---

## ⚡ TL;DR (30 detik)

1. **Simpan nomor** di kontak HP Anda:
   ```
   Nama   : 🛡 Guardian Angel
   Nomor  : +62 823-1399-6991
   ```
2. **Buka WhatsApp**, mulai chat ke kontak itu.
3. **Forward pesan mencurigakan** apa pun ke Guardian Angel.
4. **Tunggu 5–10 detik.** Balasan akan datang dengan verdict 🟢 / 🟡 / 🔴.

Selesai. Begitu cara pakai sehari-hari.

---

## 📋 Test Skenario (5 menit)

Kirim 4 pesan ini ke Guardian Angel **secara berurutan**, satu per satu,
tunggu balasan tiap pesan baru kirim yang berikutnya.

### ✅ Test 1 — Pesan biasa (harus 🟢 SAFE)

```
Halo, lagi ngapain?
```

**Ekspektasi:**
> 🛡 Scam Guardian Verdict
> *Threat Level:* SAFE
> *Confidence:* ~98%
> _Pesan terlihat biasa, tidak ada indikator scam._

### 🚨 Test 2 — Phishing bank Indonesia (harus 🔴 DANGEROUS)

```
URGENT! Akun BCA Anda akan diblokir dalam 1 jam. Verifikasi sekarang di http://bca-secure-verify.tk/login atau kirim kode OTP Anda untuk menjaga akses.
```

**Ekspektasi:**
> 🛡 Scam Guardian Verdict
> *Threat Level:* DANGEROUS
> *Type:* phishing_link, credential_phishing, bank_impersonation
> *Confidence:* ~99%
> _Pesan ini sangat berbahaya..._
>
> *Why I think so:*
> • Ancaman mendesak ("akun diblokir 1 jam")
> • Minta OTP — bank tidak pernah minta OTP via chat
> • Domain `.tk` dengan kata "secure" dan "verify" untuk meniru BCA

### 💰 Test 3 — Scam crypto (harus 🔴 DANGEROUS)

```
Bro double your BTC! Send 1 BTC to crypto-wallet-verify.xyz dapat 2 BTC back guaranteed
```

**Ekspektasi:** DANGEROUS — financial scam + phishing link

### 🤝 Test 4 — Bantuan

```
help
```

**Ekspektasi:** Penjelasan singkat siapa Guardian Angel dan cara pakainya.

---

## 👥 Test di Group WhatsApp

Guardian Angel bisa juga jaga grup WhatsApp Anda.

### Cara setup grup test

1. **Buat grup WhatsApp baru** (boleh hanya beranggotakan Anda + Guardian Angel)
2. **Tambah +62 823-1399-6991** sebagai anggota grup
3. Kirim pesan ke grup, Guardian akan auto-scan tiap pesan masuk

### Aturan respond di grup

| Jenis pesan | Yang Guardian lakukan |
|---|---|
| Pesan normal (sapaan, obrolan) | **Diam** — tidak ingin spam grup |
| Pesan suspicious (URL aneh, urgency mild) | Reply singkat (3 baris) |
| Pesan dangerous (phishing, OTP request) | Reply lengkap dengan reasoning chain |

### Test pesan grup

**Pesan biasa (Guardian diam):**
```
Selamat pagi semua
```

**Pesan suspicious (Guardian respond singkat):**
```
Cek promo bulan ini bit.ly/promo-besar
```

**Pesan dangerous (Guardian respond panjang):**
```
HALO ANGGOTA GRUP! Saya admin BCA, mohon verifikasi data semua di https://bca-verify-account.tk sebelum akun diblokir.
```

---

## 🐛 Troubleshooting

### "Saya tidak dapat balasan"

1. Pastikan Anda kirim ke nomor yang benar: **+62 823-1399-6991**
2. Tunggu 10–15 detik (LLM butuh waktu thinking)
3. Cek: apakah nomor itu memblokir Anda? Coba dari WhatsApp lain
4. Kalau tetap tidak ada balasan, tim admin (mention saya di chat dev)
   akan cek log gateway

### "Balasan formatnya berbeda dari ekspektasi"

Berarti pesan Anda di-route ke agent default, bukan Scam Guardian. Ini
bisa terjadi kalau session WhatsApp Anda dibuat sebelum routing rule
aktif. Tim admin perlu reset session Anda — kabari kami.

### "Saya kirim banyak pesan tapi balasan lambat"

Setiap pesan butuh ~5–10 detik karena agent panggil LLM. Kalau Anda kirim
3 pesan beruntun, balasan #3 mungkin baru datang setelah ~30 detik.
Sabar, atau kirim satu per satu dengan jeda.

### "Saya mau test di grup tapi Guardian tidak respond apapun"

Kemungkinan:
1. Grup belum pernah dapat pesan suspicious — Guardian sengaja diam untuk
   pesan SAFE supaya tidak spam
2. Coba kirim Test 2 (phishing BCA) di grup — pasti Guardian respond

---

## 💡 Tips Penggunaan Sehari-hari

### Untuk diri sendiri

- **Forward pesan mencurigakan** dari WhatsApp utama Anda ke Guardian
  Angel via DM
- Kalau verdict DANGEROUS, langsung block sender di chat aslinya
- Kalau SUSPICIOUS, hubungi sender via channel lain (telepon, email
  resmi) untuk verifikasi

### Untuk keluarga / orang tua

- **Jadikan Guardian Angel bagian dari grup keluarga** — tiap pesan
  suspicious yang masuk grup akan otomatis kena verdict
- Kasih tahu orang tua: _"Kalau Mama dapat pesan aneh, forward dulu ke
  Guardian Angel sebelum klik apapun."_

### Untuk grup komunitas

- Add Guardian Angel ke grup — terutama grup besar yang sering kena
  spam dari nomor unknown
- Saat ada pesan phishing massal, semua anggota grup langsung lihat
  warning dari Guardian
- Admin tetap bisa hapus/block sender berdasarkan verdict Guardian

---

## 🔒 Privasi

- Pesan yang Anda kirim ke Guardian Angel **diproses oleh LLM** (GPT-5.5
  via GrowthCircle)
- Pesan **tidak disimpan di database** untuk versi demo ini (kecuali log
  sementara di server untuk debugging)
- Jangan kirim pesan dengan informasi sensitif sungguhan (PIN asli, OTP
  asli, password Anda) — pakai contoh fiktif
- Untuk versi production, threat log akan dipersist ke SQLite dengan
  retention 90 hari (lihat `python-demo/src/threat_log.py`)

---

## 🆘 Kontak Admin

Kalau ada bug atau masalah, kabari tim Gece. Sertakan:

1. Pesan yang Anda kirim
2. Balasan yang Anda terima (atau "tidak ada balasan")
3. Waktu kirim (jam:menit)

Dengan info ini admin bisa lihat log gateway dan trace masalah dengan
cepat.

---

🛡 _Selamat menggunakan Whatsapp Guardian Angel. Stay safe online._
