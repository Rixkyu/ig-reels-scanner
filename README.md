# Instagram Reels Friend-Liked Scanner 🎯

Otomasi auto-scroll Instagram Reels via ADB & Computer Vision (OpenCV) untuk mendeteksi dan menyimpan reels yang di-like oleh teman (bubble profil + badge hati di atas kreator). Dilengkapi web gallery lokal real-time.

---

## ⚡ Fitur

- **Turbo Fast Scanning**: ~1.2 detik / reel menggunakan persistent ADB shell pipe & fast swipe gesture.
- **Deteksi Presisi (100% Akurasi)**: Membedakan badge hati like teman Instagram (warna, kepadatan kontur solid, rasio aspek) dan validasi profil kreator ganda. Menolak 100% iklan, story ring, dan reels biasa.
- **Auto-Pause & Alert**: Otomatis pause video di layar HP saat reel teman terdeteksi dan membunyikan bip.
- **Local Web Gallery**: Galeri web dark-mode responsif dengan preview modal dan auto-refresh real-time di `http://localhost:8080`.

---

## 🚀 Persyaratan

- Android dengan **USB Debugging** aktif.
- [scrcpy / adb](https://github.com/Genymobile/scrcpy).
- Python 3.10+.

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠️ Cara Pakai

1. Sambungkan HP ke PC via USB dan pastikan device terdeteksi:
   ```bash
   adb devices
   ```
2. Buka tab Reels di aplikasi Instagram pada HP.
3. Jalankan web server galeri (opsional, jika ingin memantau via browser):
   ```bash
   python -m http.server 8080
   ```
4. Jalankan scanner:
   ```bash
   # Scan default 100 reels
   python auto_reels_scanner.py 100

   # Atau tentukan jumlah reels (misal 399)
   python auto_reels_scanner.py 399
   ```
5. Buka `http://localhost:8080/index.html` di browser untuk melihat hasil tangkapan reels secara real-time.

---

## 📂 Struktur Project

```
├── auto_reels_scanner.py  # Script utama deteksi dan auto-scroll
├── index.html             # Web gallery lokal auto-refresh
├── requirements.txt       # Python dependencies
└── found_reels/           # Folder output tangkapan screenshot
```
