# 🎞 Demo GIF — Panduan Cepat (5 menit jadi)

GIF animasi 5-8 detik untuk header README. Tujuan: pengunjung repo
**langsung lihat Guardian Angel kerja** tanpa harus baca apapun.

---

## 🎯 Apa yang Dijadikan GIF

Satu skenario sederhana: forward pesan phishing → verdict masuk.

```
Frame 1 (0-1s)   : WhatsApp chat kosong dengan kontak 🛡 Guardian Angel
Frame 2 (1-2s)   : User paste / kirim pesan phishing BCA
Frame 3 (2-3s)   : Typing indicator "🛡 Guardian Angel is typing..."
Frame 4 (3-7s)   : Verdict 🛡 muncul lengkap (zoom in ke threat level DANGEROUS)
Frame 5 (7-8s)   : Loop balik ke awal (atau fade-out)
```

Total durasi: **5-8 detik**, ukuran target **<5 MB**.

---

## 📱 Cara Rekam (Android)

### Langkah 1 — Persiapkan HP

- HP yang ter-pair dengan Guardian Angel, online
- Mode **Do Not Disturb** untuk hindari notifikasi lain
- Wallpaper WhatsApp default (atau warna polos) biar tidak distract
- Set **font size WhatsApp** agak besar (Settings → Chats → Font Size: Medium)

### Langkah 2 — Rekam screen

1. Buka WhatsApp, masuk ke chat dengan 🛡 Guardian Angel
2. **Hapus chat history** dulu biar mulai bersih (Long-press → Clear chat)
3. Buka panel notifikasi → tap **Screen Record**
4. Mulai rekam
5. **Paste pesan phishing test** (siapkan dulu di clipboard):
   ```
   URGENT! Akun BCA Ibu akan diblokir dalam 1 jam. Verifikasi sekarang
   di http://bca-secure-verify.tk/login atau kirim kode OTP Anda.
   ```
6. Tap **Send**
7. **Tunggu** verdict masuk (~5-7 detik)
8. Setelah verdict full muncul, **stop recording**

Output: file `.mp4` di galeri HP.

### Langkah 3 — Convert MP4 ke GIF

**Opsi A — Pakai HP (paling cepat)**

1. Install **GIF Maker** (Android) atau **GIPHY** app
2. Import video `.mp4`
3. Trim jadi 5-8 detik
4. Crop ke aspect ratio yang bagus (square 1:1 atau 9:16 vertikal)
5. Export sebagai GIF

**Opsi B — Online tool (kalau ingin lebih kontrol)**

1. Upload `.mp4` ke https://ezgif.com/video-to-gif
2. Trim, crop, set FPS 10-15
3. Set output size **480px** width (cukup untuk README, tidak bikin file gede)
4. Download GIF

**Opsi C — Pakai komputer (kalau ada)**

```bash
# Install ffmpeg dan gifsicle
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos" -t 8 frames.png
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -filter_complex "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" -t 8 output.gif

# Compress kalau masih besar
gifsicle -O3 --lossy=80 output.gif -o demo.gif
```

### Langkah 4 — Optimize size

Target: **<5 MB**, idealnya **<2 MB**.

Trik untuk kecilkan:
- Turunkan FPS dari 30 → 10-15 (mata manusia tidak tahu beda)
- Resize width ke 480px (cukup untuk README)
- Pakai gifsicle dengan `--lossy` flag
- Atau pakai online tool seperti https://ezgif.com/optimize

---

## 📁 Simpan & Embed

### Simpan ke repo

```bash
cp demo.gif /home/ubuntu/repo/docs/demo.gif
cd /home/ubuntu/repo
git add docs/demo.gif
git commit -m "Add demo GIF showing live phishing detection"
git push
```

### Embed di README

Tambahkan di bagian header README, **setelah judul tagline**:

```markdown
# 🛡 Whatsapp Guardian Angel

> _Karena yang paling rentan, bukan yang paling kurang hati-hati..._

<p align="center">
  <img src="docs/demo.gif" alt="Demo Guardian Angel detecting phishing" width="320"/>
</p>

---

## 🌙 Bu Ratna
```

---

## 💡 Tips Pro

### Yang BIKIN GIF bagus
- ✅ Background bersih (wallpaper polos, tidak ada banyak bubble chat lama)
- ✅ Font size HP agak besar biar terbaca di GIF kecil
- ✅ Trim ketat — hilangkan dead time (jeda > 1 detik)
- ✅ Loop seamless (last frame sambung ke first frame)
- ✅ Status bar HP jangan ada notifikasi mencurigakan / jam yang aneh

### Yang HARUS dihindari
- ❌ FPS 30+ — bikin file gede tanpa benefit visual
- ❌ Width >720px — overkill untuk README, bikin file besar
- ❌ Audio — GIF tidak punya audio, jangan rekam dengan suara
- ❌ Recording > 15 detik — terlalu panjang untuk header README
- ❌ Tampilkan nomor HP/data pribadi secara tidak sengaja

---

## 🎨 Alternatif: Static Screenshot (kalau GIF terlalu sulit)

Kalau bikin GIF terlalu ribet, **screenshot static** juga sudah cukup:

1. Test phishing di WhatsApp
2. Screenshot hasil verdict yang lengkap
3. Crop biar fokus ke balon chat verdict
4. Save sebagai PNG
5. Embed ke README

```markdown
<p align="center">
  <img src="docs/screenshot-verdict.png" alt="Verdict sample" width="320"/>
</p>
```

Static screenshot **lebih cepat di-load** dan tetap powerful sebagai
proof-of-work.

---

## 🚀 Setelah GIF Jadi

1. **Push ke repo** sebagai `docs/demo.gif`
2. **Embed di README header** (lihat contoh markdown di atas)
3. **Re-share di sosmed** sebagai standalone visual
4. **Tambahkan di Devpost submission** sebagai gallery image

---

🛡 _Lima detik visual lebih kuat dari 500 kata._
