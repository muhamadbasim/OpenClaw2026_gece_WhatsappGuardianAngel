# 🔬 Kenapa Guardian Angel ≠ ChatGPT / Gemini Generic

> _"Tinggal copy-paste pesan phishing ke ChatGPT, kan?"_
>
> Bisa, tapi hasilnya tidak sama. Ini buktinya.

---

## 📋 Test Setup

**Pesan input** (sama untuk semua):
```
URGENT! Akun BCA Ibu akan diblokir dalam 1 jam. Verifikasi sekarang
di http://bca-secure-verify.tk/login atau kirim kode OTP Anda untuk
menjaga akses.
```

**Yang kami bandingkan:**
1. ChatGPT (GPT-4o, no system prompt)
2. Gemini (default web)
3. Generic LLM dengan prompt "is this phishing?"
4. **Whatsapp Guardian Angel** (system prompt + konteks Indonesia)

---

## 🤖 Hasil Bandingan

| Aspek | ChatGPT/Gemini Generic | Guardian Angel |
|---|---|---|
| **Bahasa balasan** | Inggris (default) atau Indonesia formal-kaku | **Bahasa Indonesia natural**, sesuai tone WhatsApp |
| **Format** | Paragraf panjang, paragraf bersambung | **Format WhatsApp**: bold, italic, bullet, fit di 1 layar HP |
| **Confidence score** | Tidak ada angka | **99%** dengan reasoning |
| **Action konkret** | "Be careful" / "Verifikasi keasliannya" | **"Hubungi BCA via call center 1500888"** — nomor resmi spesifik |
| **Konteks lokal** | Tidak tahu yang mana TLD `.tk` lazim di scam Indonesia | Tahu pola scam Indonesia (BCA, Mandiri, BRI, JNE, Shopee Express) |
| **Pengalaman user** | Buka browser, copy paste, tunggu, baca dinding teks | **Forward pesan, tunggu 5 detik, lihat verdict** — tetap di WhatsApp |
| **Setup untuk lansia** | Harus install app baru, login, paham UI chatbot | **Cuma simpan kontak WhatsApp** — UI yang sudah dikenal |
| **Privacy** | Pesan masuk ke OpenAI/Google database | LLM call, no DB persistence (versi demo) |

---

## 💬 Output Sample

### ChatGPT (GPT-4o, generic, tanpa system prompt)

> _The message you received appears to be a phishing attempt. Here are several reasons why I believe so:_
>
> _1. The URL `http://bca-secure-verify.tk` uses a `.tk` top-level domain, which is commonly used in phishing scams._
> _2. The message uses urgency tactics, such as claiming your account will be blocked within 1 hour._
> _3. Legitimate banks like BCA never ask for OTP codes via WhatsApp messages._
> _4. The grammar and structure resemble common phishing templates._
>
> _I recommend not clicking the link, not sharing your OTP, and contacting BCA directly through their official channels to verify._

**Masalah:**
- 📝 Inggris, paragraf panjang
- ❌ Tidak ada threat level / type / confidence
- ❌ "Official channels" — abstrak, tidak kasih nomor spesifik
- ❌ Format paragraf, tidak fit untuk WhatsApp
- ⏱ User harus copy ke ChatGPT, lalu kembali ke WhatsApp

### Gemini (default web)

> _Pesan tersebut sangat mungkin merupakan upaya phishing. Berikut adalah alasannya:_
>
> _Bahasa yang Mendesak: Pesan tersebut menggunakan kata "URGENT" dan ancaman akun akan diblokir dalam 1 jam, ini adalah taktik klasik untuk membuat Anda panik._
>
> _Tautan Mencurigakan: Tautan `http://bca-secure-verify.tk/login` bukanlah situs web resmi BCA. Domain `.tk` seringkali digunakan untuk situs web palsu..._
>
> _[paragraf panjang lainnya]_
>
> _Saya sangat menyarankan Anda untuk **tidak mengklik tautan tersebut** dan **tidak memberikan kode OTP Anda** kepada siapa pun. Hubungi BCA melalui saluran resmi mereka untuk memverifikasi._

**Masalah:**
- ✅ Indonesia (lebih baik dari ChatGPT)
- ❌ Bahasa kaku ("Tautan Mencurigakan", "saluran resmi")
- ❌ Tidak ada threat level / confidence
- ❌ Format paragraf panjang, tidak fit di layar WhatsApp HP
- ❌ "Hubungi BCA" tanpa nomor spesifik
- ⏱ User harus tab terpisah, masih ribet untuk lansia

### 🛡 Whatsapp Guardian Angel

> _🛡 Scam Guardian Verdict_
>
> _Threat Level:_ **DANGEROUS**
> _Type:_ phishing_link, credential_phishing, bank_impersonation
> _Confidence:_ 99%
>
> _Pesan ini sangat berbahaya — kemungkinan besar mencoba mencuri akses akun BCA Anda._
>
> _Kenapa saya pikir begitu:_
> • Memakai ancaman mendesak ("akun diblokir 1 jam")
> • Meminta OTP — bank tidak pernah meminta OTP lewat WhatsApp
> • Domain `.tk` dengan kata "secure" dan "verify" untuk meniru BCA
>
> _Recommended action:_ Jangan klik link, jangan kirim OTP. Block pengirim. **Hubungi BCA hanya lewat aplikasi resmi atau call center 1500888.**

**Kenapa lebih baik:**
- ✅ Bahasa Indonesia natural (bukan terjemahan kaku)
- ✅ Threat level + type + confidence yang scannable
- ✅ Reasoning chain dengan bullet (cepat baca)
- ✅ **Nomor call center spesifik** (1500888) — actionable, tidak abstrak
- ✅ Format WhatsApp markdown (`*bold*`, `_italic_`)
- ✅ User **tidak perlu keluar dari WhatsApp** — chat ada di WhatsApp, balasan ada di WhatsApp

---

## 🎯 Insight: Kenapa System Prompt + Konteks Lokal Penting

Ini bukan soal LLM yang lebih pintar. **GPT-5.5 yang kami pakai pun underlying-nya sama dengan ChatGPT.** Bedanya:

### 1. Konteks lokal di system prompt
SOUL.md kami punya:
- Daftar bank Indonesia: BCA, Mandiri, BRI, BNI
- Pola scam khas Indonesia: kurir paket, e-commerce, "anda menang lotere"
- Nomor call center resmi: BCA 1500888, Mandiri 14000, dst
- TLD pattern Indonesia: .tk, .ml, .xyz, .top spesifik untuk konteks lokal

### 2. Format yang dirancang untuk WhatsApp
Bukan untuk web browser, bukan untuk dashboard. Untuk **layar HP 6 inch** dengan font WhatsApp default. SOUL.md punya:
- 2 contoh full verdict sebagai anchor visual
- Aturan "no markdown headers" karena WhatsApp tidak render itu
- Aturan "no tables" karena tidak fit di layar

### 3. Pengalaman user yang seamless
ChatGPT/Gemini = "buka tab baru, copy paste, tunggu, baca, balik ke WhatsApp" — ada 4 langkah dengan friction tinggi.

Guardian Angel = "long-press → forward → kirim → tunggu 5 detik" — 1 langkah dalam app yang sudah dibuka. **Lansia mampu ini, tanpa pelatihan.**

### 4. Persistensi & integrasi grup
ChatGPT tidak bisa di-add ke grup keluarga. Guardian Angel bisa, dan otomatis scan tiap pesan masuk. Network effect: 1 setup = melindungi semua anggota grup.

---

## 📊 TL;DR

| | ChatGPT | Gemini | Guardian Angel |
|---|:---:|:---:|:---:|
| Bahasa Indonesia natural | ❌ | 🟡 | ✅ |
| Threat level + confidence | ❌ | ❌ | ✅ |
| Format WhatsApp-friendly | ❌ | ❌ | ✅ |
| Nomor call center spesifik | ❌ | ❌ | ✅ |
| User tetap di WhatsApp | ❌ | ❌ | ✅ |
| Cocok untuk lansia | ❌ | ❌ | ✅ |
| Bisa di-add ke grup keluarga | ❌ | ❌ | ✅ |
| **Time-to-verdict** | ~30 detik | ~30 detik | **~5 detik** |

LLM yang sama, system prompt + UX yang berbeda, dampak yang berbeda.

---

🛡 _Tools tidak menyelamatkan orang. Tools yang **dirancang untuk orang yang membutuhkannya** yang menyelamatkan._

— **Tim Gece**
