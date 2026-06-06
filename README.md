<div align="center">
  <img src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?q=80&w=1000&auto=format&fit=crop" alt="Jalan Tol" width="100%" height="250" style="object-fit: cover; border-radius: 10px;">

  <h1>🚔 Smart Assistant Bot JMTO - Ruas JSM 🛣️</h1>
  
  <p>
    <strong>Sistem Otomatisasi Pelaporan Operasional & Penjadwalan Berbasis Telegram</strong>
  </p>

  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://core.telegram.org/bots/api"><img src="https://img.shields.io/badge/Telegram_API-Ready-2CA5E0.svg?style=flat&logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://github.com/python-telegram-bot/python-telegram-bot"><img src="https://img.shields.io/badge/Library-PTB_v20+-green.svg?style=flat" alt="PTB"></a>
  <br><br>
</div>

---

## 🌟 Tentang Bot Ini

Bot ini dirancang khusus untuk mempermudah kinerja personil lapangan **Jasa Marga Tollroad Operator (JMTO) di Ruas Surabaya - Mojokerto (JSM)**. Mengubah input teks sederhana dari pengguna menjadi draf laporan standar operasional yang rapi, terstruktur, dan bebas *typo* dalam hitungan detik! ⚡

Tidak hanya itu, bot ini juga dibekali mesin penjadwalan pintar untuk mengecek shift petugas lapangan maupun MCSS secara presisi.

---

## 🚀 Fitur Unggulan

Berikut adalah amunisi *command* yang bisa digunakan di dalam bot:

### 📝 Menu Laporan Operasional
* `/lapor` — **Laporan Serah Terima Shift.** Lengkap dengan perhitungan jumlah *Oddo* (Jarak Tempuh) otomatis (Awal Tugas & Akhir Tugas).
* `/laka` — **Laporan Awal Kejadian 33 (Laka).** Pembuatan format laporan cepat tanggap darurat lengkap dengan data ban.
* `/pantauan` — **Laporan Pantauan Kondisi.** Dengan fitur cerdas pendeteksi ucapan waktu (Pagi/Siang/Sore/Malam) otomatis dari server.
* `/trace` — **Laporan Penanganan Kendala (Trace).** Menghasilkan form *Tindak Lanjut* dan pelaporan ganti ban/derek.
* `/giat` — **Laporan Penanganan Biasa.** Untuk mencatat kegiatan patroli rutin di ruas tol.

### 📅 Menu Jadwal Cerdas
* `/jadwal` — **Cek Jadwal Sebulan.** Masukkan nama petugas, dan bot akan menampilkan jadwal shift selama 1 bulan penuh.
* `/shift` — **Cek Petugas Harian.** Masukkan tanggal, bot akan menampilkan siapa saja personil Unit 211 & 212 yang bertugas di shift 1, 2, dan 3.
* `/210` — **Jadwal Kashift / MCSS.** Sama seperti `/jadwal`, namun khusus untuk database bos MCSS.
* `/210s` — **Shift Kashift Harian.** Mengecek MCSS yang bertugas per tanggal, lengkap dengan logika pengganti cuti otomatis!

---

## ⚙️ Persyaratan Sistem

Pastikan kamu memiliki ini sebelum menjalankan bot:
- **Python 3.8** atau yang lebih baru.
- Library `python-telegram-bot` (Versi 20.x ke atas).
- **Bot Token** dari [@BotFather](https://t.me/botfather) di Telegram.

---

## 🛠️ Cara Instalasi & Menjalankan Bot

Ikuti langkah-langkah mudah berikut untuk menghidupkan bot di komputer/server kamu:

**1. Clone Repository ini**
```bash
git clone [https://github.com/USERNAME_GITHUB_KAMU/bot-laporan-jsm.git](https://github.com/USERNAME_GITHUB_KAMU/bot-laporan-jsm.git)
cd bot-laporan-jsm