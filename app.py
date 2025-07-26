import streamlit as st
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
from rembg import remove

st.set_page_config(page_title="Editor Pas Foto", layout="centered")
st.title("📸 Editor Pas Foto - Ubah Ukuran, Hapus Background & Hitam Putih")

# --- Pilihan Ukuran Pas Foto (dalam pixel untuk 300 DPI) ---
photo_sizes = {
    "2x3": (236, 354),
    "3x4": (354, 472),
    "4x6": (472, 709),
    "5x7": (591, 827),
    "6x9": (709, 1063)
}

# --- Unggah Foto ---
uploaded_file = st.file_uploader("Unggah foto (format JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Foto Asli", use_container_width=True)
    
    # --- Pilihan Ukuran ---
    size_option = st.selectbox("Pilih ukuran pas foto:", list(photo_sizes.keys()))
    target_w, target_h = photo_sizes[size_option]
    
    # --- Opsi Background ---
    st.markdown("### 🎨 Pengaturan Background")
    bg_option = st.radio(
        "Pilih jenis background:",
        ["Tetap (Background Asli)", "Hapus Background + Warna Solid", "Hapus Background + Transparant"]
    )
    
    bg_color = "#FFFFFF"  # Default putih
    if bg_option == "Hapus Background + Warna Solid":
        bg_color = st.color_picker("Pilih warna background:", "#FFFFFF")
        st.write(f"Warna dipilih: {bg_color}")
    
    # --- Opsi Hitam Putih ---
    grayscale = st.checkbox("Ubah ke Hitam Putih (Grayscale)", value=False)
    
    # --- Penyesuaian Posisi ---
    st.markdown("### 📐 Penyesuaian Posisi")
    x_offset = st.slider("Geser Kanan/Kiri", -200, 200, 0)
    y_offset = st.slider("Geser Atas/Bawah", -200, 200, 0)
    
    # --- Tombol Proses ---
    if st.button("🔄 Proses Pas Foto", type="primary"):
        with st.spinner("Memproses foto..."):
            try:
                # --- Proses Background Removal ---
                if bg_option.startswith("Hapus Background"):
                    st.info("🔄 Menghapus background...")
                    
                    # Convert image to bytes for rembg
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    
                    # Remove background using rembg
                    result_bytes = remove(img_bytes)
                    processed_image = Image.open(BytesIO(result_bytes)).convert("RGBA")
                else:
                    processed_image = image.convert("RGBA")
                
                # --- Crop dan Resize ---
                img_np = np.array(processed_image)
                
                # Hitung aspek rasio
                original_h, original_w = processed_image.size[1], processed_image.size[0]
                aspect_ratio = original_w / original_h
                target_aspect = target_w / target_h
                
                # Crop otomatis untuk menyesuaikan rasio dengan offset
                if aspect_ratio > target_aspect:
                    new_width = int(original_h * target_aspect)
                    start_x = max(0, min((original_w - new_width) // 2 + x_offset, original_w - new_width))
                    end_x = start_x + new_width
                    cropped = img_np[:, start_x:end_x]
                else:
                    new_height = int(original_w / target_aspect)
                    start_y = max(0, min((original_h - new_height) // 2 + y_offset, original_h - new_height))
                    end_y = start_y + new_height
                    cropped = img_np[start_y:end_y, :]
                
                # Resize ke ukuran pas foto
                result = Image.fromarray(cropped).resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # --- Tambahkan Background Warna ---
                if bg_option == "Hapus Background + Warna Solid":
                    # Convert hex color to RGB
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    
                    # Buat background dengan warna solid
                    background = Image.new("RGB", (target_w, target_h), bg_rgb)
                    background = background.convert("RGBA")
                    
                    # Composite gambar dengan background
                    result = Image.alpha_composite(background, result.convert("RGBA"))
                    result = result.convert("RGB")
                
                elif bg_option == "Hapus Background + Transparant":
                    # Tetap dalam mode RGBA untuk transparency
                    result = result.convert("RGBA")
                
                else:
                    # Background asli
                    result = result.convert("RGB")
                
                # --- Ubah ke Grayscale ---
                if grayscale:
                    if result.mode == "RGBA":
                        # Untuk RGBA, simpan alpha channel
                        alpha = result.split()[-1]
                        rgb_result = result.convert("RGB")
                        gray_result = ImageOps.grayscale(rgb_result)
                        result = gray_result.convert("RGBA")
                        result.putalpha(alpha)
                    else:
                        result = ImageOps.grayscale(result)
                
                # --- Tampilkan Hasil ---
                st.success("✅ Pas foto berhasil dibuat!")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("### 📷 Hasil Pas Foto")
                    st.image(result, caption=f"Pas Foto {size_option} ({target_w}×{target_h}px)")
                
                with col2:
                    st.markdown("### 📊 Info Hasil")
                    st.write(f"**Ukuran:** {size_option}")
                    st.write(f"**Dimensi:** {target_w}×{target_h}px")
                    st.write(f"**Background:** {bg_option}")
                    if bg_option == "Hapus Background + Warna Solid":
                        st.write(f"**Warna BG:** {bg_color}")
                    st.write(f"**Grayscale:** {'Ya' if grayscale else 'Tidak'}")
                    st.write(f"**Offset:** X={x_offset}, Y={y_offset}")
                
                # --- Download Button ---
                buf = BytesIO()
                
                if bg_option == "Hapus Background + Transparant":
                    # Save as PNG untuk preserve transparency
                    result.save(buf, format="PNG")
                    file_ext = "png"
                    mime_type = "image/png"
                else:
                    # Save as JPEG
                    if result.mode == "RGBA":
                        result = result.convert("RGB")
                    result.save(buf, format="JPEG", quality=95)
                    file_ext = "jpg"
                    mime_type = "image/jpeg"
                
                st.download_button(
                    label=f"📥 Download Pas Foto (.{file_ext})",
                    data=buf.getvalue(),
                    file_name=f"pas_foto_{size_option}_{target_w}x{target_h}.{file_ext}",
                    mime=mime_type,
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {str(e)}")
                st.info("💡 Tips: Pastikan foto memiliki subjek yang jelas untuk background removal yang optimal")

else:
    st.info("📤 Silakan unggah foto terlebih dahulu untuk memulai.")
    
    # Info fitur
    st.markdown("""
    ### 🌟 Fitur Editor Pas Foto:
    
    **📏 Ukuran Standar:**
    - 2×3, 3×4, 4×6, 5×7, 6×9 cm (300 DPI)
    
    **🎨 Background Options:**
    - Tetap background asli
    - Hapus background + ganti warna solid
    - Hapus background + transparant (PNG)
    
    **🔧 Fitur Lainnya:**
    - Konversi hitam-putih
    - Penyesuaian posisi foto
    - Crop otomatis sesuai rasio
    - Download format JPG/PNG
    
    **💡 Tips Penggunaan:**
    - Gunakan foto dengan subjek yang jelas untuk hasil background removal terbaik
    - Adjust posisi untuk mendapatkan crop yang optimal
    - Pilih warna background yang kontras dengan subjek
    """)
