import streamlit as st
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Editor Pas Foto", layout="centered")
st.title("📸 Editor Pas Foto - Ubah Ukuran, Hitam Putih & Posisi")

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

    # --- Opsi Hitam Putih ---
    grayscale = st.checkbox("Ubah ke Hitam Putih (Grayscale)", value=False)

    # --- Penyesuaian Posisi ---
    st.markdown("### Penyesuaian Posisi (piksel)")
    x_offset = st.slider("Geser Kanan/Kiri", -100, 100, 0)
    y_offset = st.slider("Geser Atas/Bawah", -100, 100, 0)

    # --- Proses Gambar ---
    img_np = np.array(image)

    # Hitung aspek rasio
    original_h, original_w = image.size[1], image.size[0]
    aspect_ratio = original_w / original_h
    target_aspect = target_w / target_h

    # Crop otomatis untuk menyesuaikan rasio
    if aspect_ratio > target_aspect:
        new_width = int(original_h * target_aspect)
        start_x = max(0, (original_w - new_width) // 2 + x_offset)
        end_x = start_x + new_width
        cropped = img_np[:, start_x:end_x]
    else:
        new_height = int(original_w / target_aspect)
        start_y = max(0, (original_h - new_height) // 2 + y_offset)
        end_y = start_y + new_height
        cropped = img_np[start_y:end_y, :]

    # Resize ke ukuran pas foto
    result = Image.fromarray(cropped).resize((target_w, target_h))

    # Ubah ke grayscale jika dipilih
    if grayscale:
        result = ImageOps.grayscale(result)

    # Tampilkan hasil
    st.markdown("### Hasil Pas Foto")
    st.image(result, caption=f"Pas Foto {size_option}", use_container_width=False)

    # Unduh hasil
    buf = BytesIO()
    result.save(buf, format="JPEG")
    st.download_button(
        label="📥 Unduh Pas Foto",
        data=buf.getvalue(),
        file_name=f"pas_foto_{size_option}.jpg",
        mime="image/jpeg"
    )

else:
    st.info("📤 Silakan unggah foto terlebih dahulu untuk memulai.")
