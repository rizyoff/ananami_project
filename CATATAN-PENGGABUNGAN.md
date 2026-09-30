# Ananami Landscape — One Page Company Profile

Seluruh isi `sect_3.html` … `sect_16.html` sudah digabung ke dalam **satu** `index.html`.
Cukup buka `index.html`, lalu scroll dari atas ke bawah.

## Struktur folder
```
index.html              <- SATU-SATUNYA halaman
style.css               <- CSS asli (tidak diubah)
sections.css            <- CSS section 3–16, sudah di-scope per section
sections.js             <- JS section 3–16 + navbar one-page
assets/                 <- gambar (path tidak berubah)
_arsip-section-lama/    <- sect_3..sect_16.html asli, disimpan sebagai arsip
```

## Peta section
| ID | Asal | Isi |
|----|------|-----|
| `#p1`  | index.html | About |
| `#p2`  | index.html | Company Legality |
| `#p3`  | sect_3.html  | Project Types |
| `#p4`  | sect_4.html  | Our Best Service |
| `#p5`  | sect_5.html  | Portfolio — Landscape Design |
| `#p6`  | sect_6.html  | Taman Villa |
| `#p7`  | sect_7.html  | Private House Bali |
| `#p8`  | sect_8.html  | Design Tabanan |
| `#p9`  | sect_9.html  | Garden Details |
| `#p10` | sect_10.html | Landscape Details |
| `#p11` | sect_11.html | Landscape Construction |
| `#p12` | sect_12.html | Landscape Build |
| `#p13` | sect_13.html | Landscape Maintenance |
| `#p14` | sect_14.html | Our Best Team |
| `#p15` | sect_15.html | Get In Touch |
| `#p16` | sect_16.html | Thank You |

## Yang diperbaiki saat penggabungan

1. **Satu `<html>`, `<head>`, `<body>`.** `<head>` tiap section dilebur; meta, font,
   Tailwind, Font Awesome, dan Lucide hanya dimuat sekali.
2. **CSS di-scope.** Tiap aturan CSS section diberi awalan `#pN`.
   - `body` / `:root` / `html` → dipetakan ke elemen pembungkus `#pN`.
   - selector turunan memakai `:where(#pN)` supaya *specificity* aslinya tidak berubah
     (penting agar utility Tailwind seperti `p-4` tetap menang).
   - Contoh: `.container` milik `sect_5` tidak lagi bentrok dengan `.container` lain.
3. **`@keyframes` di-rename** (`fadeInUp` → `fadeInUp__p12`) karena nama yang sama
   dipakai 5 file berbeda; referensi di `animation:` ikut diperbarui.
4. **ID ganda di-rename**: `modalImg`→`p11-modalImg`, `detailModal`→`p13-detailModal`,
   `toast`→`p16-toast`, dst. Referensi di HTML, CSS, dan JS ikut diubah.
5. **JS diisolasi.** Tiap script dibungkus `__sectionScope()` yang memberi
   `document` & `window` semu:
   - `getElementById` / `querySelector` / `querySelectorAll` hanya mencari di dalam
     section itu sendiri;
   - `window.onload` diubah jadi listener tambahan, jadi `sect_3` dan `sect_16`
     tidak saling menimpa;
   - variabel/fungsi tidak lagi bocor ke global scope.
6. **Fungsi untuk `onclick` diberi akhiran unik** (`selectProject__p3`,
   `showToast__p15` vs `showToast__p16`) dan diekspor ke `window` secara terkontrol.
7. **Konfigurasi Tailwind digabung.** Bentrokan `font-serif`/`font-sans` antara
   `sect_7`/`sect_16` dan section lain ditangani lewat override ber-scope
   (`#p16 .font-serif { … }`).
8. **Navbar jadi anchor.** Semua link memakai `#pN`, tidak ada satu pun link ke
   `sect_*.html`. Link `google.com` yang salah diarahkan ke `#p11`.
9. **Navbar sticky + hamburger.** `style.css` sudah punya aturan off-canvas untuk
   layar ≤900px tapi tombolnya belum ada, jadi tombol `.nav-toggle` + backdrop
   ditambahkan beserta logikanya. Tinggi navbar dihitung ke `--topbar-h`.
10. **Smooth scroll + `scroll-margin-top`** memakai `--topbar-h`, jadi judul section
    tidak tertutup navbar.
11. **Scrollspy**: menu aktif dan indikator garis mengikuti posisi scroll.

## Catatan
- Section 5 di `index.html` lama sudah ter-copy markup-nya tetapi **CSS-nya tidak
  ikut**, sehingga tampil berantakan. Versi ini mengambil ulang dari `sect_5.html`
  lengkap dengan CSS-nya.
- Sebagian besar gambar memakai URL Unsplash, jadi butuh koneksi internet.
  Tailwind, Font Awesome, dan Lucide juga dimuat dari CDN.
- Kalau nanti ada section baru, jalankan ulang skrip penggabung
  (`build_onepage.py`) daripada menempel manual.
