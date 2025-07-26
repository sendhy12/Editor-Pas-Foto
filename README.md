# 📸 Editor Pas Foto - AI Background Removal

Aplikasi web sederhana untuk mengedit pas foto dengan fitur AI background removal, crop otomatis, dan konversi hitam-putih menggunakan Streamlit.

![Editor Pas Foto Demo](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PIL](https://img.shields.io/badge/PIL-green?style=for-the-badge)

## ✨ Fitur Utama

### 📏 **Ukuran Pas Foto Standar**
- **2×3 cm** (236×354 px) - KTP, SIM
- **3×4 cm** (354×472 px) - Passport, Visa
- **4×6 cm** (472×709 px) - Ijazah, Sertifikat  
- **5×7 cm** (591×827 px) - Dokumen resmi
- **6×9 cm** (709×1063 px) - Poster kecil

### 🎨 **Background Options**
- **Tetap** - Background asli tidak berubah
- **Hapus + Warna Solid** - AI background removal + ganti warna pilihan
- **Hapus + Transparan** - Background removal dengan hasil PNG transparan

### 🔧 **Fitur Tambahan**
- ✅ AI-powered background removal
- ✅ Crop otomatis sesuai aspect ratio
- ✅ Konversi hitam-putih (grayscale)
- ✅ Penyesuaian posisi foto (offset)
- ✅ Download format JPG/PNG
- ✅ Preview real-time
- ✅ Interface yang user-friendly

## 🎯 Cara Penggunaan

### Step 1: Upload Foto
- Klik "**Browse files**" atau drag & drop
- Format yang didukung: **JPG, JPEG, PNG**
- Ukuran maksimal: **200MB**

### Step 2: Pilih Ukuran
- Pilih ukuran pas foto dari dropdown
- Ukuran otomatis disesuaikan untuk 300 DPI

### Step 3: Atur Background
- **Tetap**: Background asli tidak berubah
- **Hapus + Warna**: Pilih warna dengan color picker
- **Hapus + Transparan**: Background hilang (PNG)

### Step 4: Fine-tuning
- Centang "**Hitam Putih**" jika diperlukan
- Atur posisi dengan slider **Kanan/Kiri** dan **Atas/Bawah**

### Step 5: Proses & Download
- Klik "**🔄 Proses Pas Foto**"
- Tunggu proses selesai
- Klik "**📥 Download**" untuk menyimpan
