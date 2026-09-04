# Bot Auto-Follow FOMO Family

[English](README.md) | [Bahasa Indonesia](README.id.md)

Script Python untuk otomatisasi follow akun di [fomo.family](https://fomo.family), dengan fitur scrape followers dari beberapa target, skip akun yang sudah difollow, delay antar-request, dan laporan statistik followers/following sebelum & sesudah dijalankan.

> ⚠️ **Disclaimer:** Script ini berinteraksi dengan API internal fomo.family menggunakan token/cookie akun pribadi kamu. Penggunaan automation seperti ini berpotensi melanggar Terms of Service platform dan bisa berujung rate-limit atau suspend akun. Gunakan dengan tanggung jawab sendiri, idealnya dengan volume wajar (bukan mass-follow ribuan akun sekaligus).

## Fitur

- ✅ Scrape followers dari banyak target sekaligus (`targets_to_scrape` bisa berisi banyak ID)
- ✅ Skip otomatis akun yang sudah kamu follow sebelumnya
- ✅ Skip duplikat antar-target (satu follower tidak akan di-follow dua kali)
- ✅ Delay acak antar-follow (dapat dikonfigurasi, default 0.8–2.0 detik)
- ✅ Load token & cookie dari file config, bukan input manual tiap run
- ✅ Laporan followers & following (sebelum vs sesudah)
- ✅ Output terminal berwarna untuk kemudahan baca

## Requirements

- Python 3.8+
- Library `curl_cffi`

Install dependency:

```bash
pip install curl_cffi
```

## Struktur File

```
.
├── bot_autofollow.py   # Script utama
├── config.json          # Konfigurasi (token, cookie, target, dll)
└── README.md
```

## Konfigurasi (`config.json`)

Buat file `config.json` di folder yang sama dengan script, isi seperti ini:

```json
{
  "auth_token": "Bearer xxxxxxxxxxxxxxxx",
  "cookie": "isi_cookie_lengkap_kamu",
  "my_user_id": "uuid-akun-kamu",
  "my_user_handle": "username_kamu",
  "targets_to_scrape": [
    "id-target-1",
    "id-target-2"
  ],
  "limit_per_target": 50,
  "delay_min_seconds": 0.8,
  "delay_max_seconds": 2.0
}
```

### Cara ambil nilai-nilai di atas

| Field | Cara mendapatkannya |
|---|---|
| `auth_token` | Buka fomo.family di browser → Login → buka DevTools (F12) → tab **Network** → cari request apa saja ke `prod-api.fomo.family` → lihat header `authorization` → copy nilainya (termasuk `Bearer `) |
| `cookie` | Di request yang sama, copy nilai header `cookie` |
| `my_user_id` | Ada di response API profil kamu, field `id` |
| `my_user_handle` | Username kamu di fomo.family (yang muncul di URL profil) |
| `targets_to_scrape` | ID user (bukan username) dari akun-akun yang followernya mau kamu scrape. Bisa didapat dari response API leaderboard atau profil user |

⚠️ **Jangan commit `config.json` ke GitHub** — file ini berisi token/cookie pribadi. Tambahkan ke `.gitignore`:

```
config.json
```

Sediakan `config.example.json` (tanpa isi asli) sebagai template untuk publik jika ingin share repo.

## Cara Menjalankan

```bash
python3 main.py
```

Alur yang terjadi:

1. Script membaca `config.json` dan validasi field wajib.
2. Ambil & tampilkan statistik akun kamu (followers & following) **sebelum** proses.
3. Ambil daftar akun yang sudah kamu follow (untuk keperluan skip).
4. Scrape followers dari setiap ID di `targets_to_scrape`, gabungkan jadi daftar unik, buang yang sudah difollow/duplikat.
5. Follow satu per satu dengan delay acak di antaranya, sambil menampilkan status sukses/gagal per akun.
6. Tampilkan ulang statistik followers & following **sesudah** proses, plus selisihnya.

## Konfigurasi Tambahan

| Field | Default | Keterangan |
|---|---|---|
| `limit_per_target` | 50 | Batas total akun unik yang akan difollow dalam satu run (bukan per-target) |
| `delay_min_seconds` | 0.8 | Jeda minimum antar-follow (detik) |
| `delay_max_seconds` | 2.0 | Jeda maksimum antar-follow (detik) |

## Troubleshooting

- **`[ERROR] File 'config.json' tidak ditemukan`** → pastikan `config.json` ada di folder yang sama saat menjalankan script.
- **Status 401 / 403 saat request** → token/cookie sudah expired, login ulang dan ambil token baru.
- **`Tidak ada target baru untuk difollow`** → semua followers dari target yang di-scrape sudah kamu follow sebelumnya.

## Support / Donate

Kalau project ini membantu kamu, boleh banget support pengembangannya. Berapapun jumlahnya sangat saya hargai apresiasinya 🙏

- **Bitcoin:** `13YVRErt7gqG2vVqPSg6ZbXibc4EhuqYZn`
- **EVM Address:** `0x13972547B1c875fC46700364B5A985F39Ce4E46b`
- **Solana:** `GNJGHfr1VygCKmLRxTmrgNXEQm77G1wzyCDjHqFkdHM9`
- **TRX:** `TPW9tZ1Q44nDrCrkuwR2XaGiPohvx41KEC`
- **Sociabuzz:** https://sociabuzz.com/xzvxco/tribe
- **FOMO Family:** [@kobo_kanaeru](https://fomo.family)

Terima kasih, berapapun sangat saya hargai apresiasinya!

## Lisensi

Gunakan dan modifikasi sesuai kebutuhan pribadi. Tidak berafiliasi dengan fomo.family.
