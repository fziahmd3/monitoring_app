# Perbaikan Upload Recording

## Masalah yang Diperbaiki

### 1. Error UnboundLocalError: UPLOAD_FOLDER
**Masalah:** Variabel `UPLOAD_FOLDER` didefinisikan di dalam fungsi `admin_dashboard()` tetapi digunakan di tempat lain, menyebabkan error `UnboundLocalError`.

**Solusi:** 
- Memindahkan definisi `UPLOAD_FOLDER` dan `ALLOWED_EXTENSIONS` ke awal fungsi `register_routes()`
- Menghapus definisi duplikat yang ada di dalam fungsi `admin_dashboard()`

### 2. Endpoint Upload Recording
**Masalah:** Belum ada endpoint untuk menerima file rekaman audio dari aplikasi mobile.

**Solusi:**
- Membuat endpoint `/upload_recording` yang menerima:
  - `recording` (file audio)
  - `kodeSantri` (string)
  - `kodeGuru` (string)
- File disimpan di folder `app/static/recordings/`
- Nama file: `{kode_guru}_{kode_santri}_{original_filename}`

## File yang Dimodifikasi

### 1. `app/routes.py`
- Menambahkan definisi `UPLOAD_FOLDER` dan `ALLOWED_EXTENSIONS` di awal fungsi `register_routes()`
- Menambahkan fungsi `allowed_file()` untuk validasi ekstensi file
- Menambahkan endpoint `/upload_recording` untuk menerima file audio
- Menghapus definisi duplikat di fungsi `admin_dashboard()`

### 2. `app/static/recordings/.gitkeep`
- Membuat folder `recordings` untuk menyimpan file audio
- File `.gitkeep` memastikan folder tetap ada di repository

## Endpoint Upload Recording

### URL: `/upload_recording`
### Method: POST
### Content-Type: multipart/form-data

### Parameters:
- `recording`: File audio (m4a, mp3, wav, aac)
- `kodeSantri`: Kode santri (string)
- `kodeGuru`: Kode guru (string)

### Response Success (200):
```json
{
  "success": true,
  "message": "File uploaded",
  "filename": "GURU001_SANTRI001_hafalan_recording_1234567890.m4a"
}
```

### Response Error (400):
```json
{
  "success": false,
  "message": "No file part"
}
```

## Struktur Folder

```
monitoring_app/
├── app/
│   ├── static/
│   │   ├── recordings/          # Folder untuk file audio
│   │   │   └── .gitkeep
│   │   ├── profile_pics/        # Folder untuk foto profil
│   │   └── icon/
│   └── routes.py               # File yang diperbaiki
```

## Cara Penggunaan

### 1. Dari Aplikasi Mobile
1. Rekam audio menggunakan `RekamHafalanScreen`
2. Tekan tombol "Upload Rekaman"
3. File akan dikirim ke endpoint `/upload_recording`
4. Response akan menampilkan status upload

### 2. Testing dengan cURL
```bash
curl -X POST \
  -F "recording=@/path/to/audio.m4a" \
  -F "kodeSantri=SANTRI001" \
  -F "kodeGuru=GURU001" \
  http://localhost:5000/upload_recording
```

## Validasi File

### Ekstensi yang Diizinkan:
- `.m4a` (AAC)
- `.mp3` (MP3)
- `.wav` (WAV)
- `.aac` (AAC)

### Validasi yang Dilakukan:
1. File harus ada dalam request
2. Nama file tidak boleh kosong
3. Ekstensi file harus diizinkan
4. `kodeSantri` dan `kodeGuru` harus ada

## Keamanan

### Nama File:
- Menggunakan `secure_filename()` untuk mencegah path traversal
- Format: `{kode_guru}_{kode_santri}_{original_filename}`
- Timestamp ditambahkan untuk menghindari konflik nama

### Folder:
- File disimpan di folder `static/recordings/`
- Folder dibuat otomatis jika belum ada
- Tidak ada akses langsung ke file dari web

## Troubleshooting

### 1. Error "No file part"
- Pastikan field `recording` ada dalam request
- Pastikan Content-Type adalah `multipart/form-data`

### 2. Error "File type not allowed"
- Pastikan ekstensi file adalah m4a, mp3, wav, atau aac
- Periksa nama file asli

### 3. Error "Missing kodeSantri or kodeGuru"
- Pastikan kedua field dikirim dalam request
- Periksa nama field (case sensitive)

### 4. Error "Permission denied"
- Pastikan folder `static/recordings/` dapat ditulis
- Periksa permission folder

## Testing

### 1. Test Upload File
- Upload file audio dengan format yang diizinkan
- Periksa file tersimpan di folder `static/recordings/`
- Periksa nama file sesuai format

### 2. Test Validasi
- Coba upload file dengan ekstensi tidak diizinkan
- Coba upload tanpa file
- Coba upload tanpa kode santri/guru

### 3. Test Response
- Periksa response JSON sesuai format
- Periksa status code (200 untuk sukses, 400 untuk error)

## Kesimpulan

Perbaikan ini mengatasi masalah utama upload recording dengan:
- Memperbaiki error `UnboundLocalError` untuk `UPLOAD_FOLDER`
- Menambahkan endpoint upload recording yang lengkap
- Menambahkan validasi file dan parameter
- Menyediakan response yang informatif
- Memastikan keamanan file upload 