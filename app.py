import streamlit as st
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
from rembg import remove

# =====================
# Konfigurasi halaman
# =====================
st.set_page_config(
    page_title="Editor Foto Pro",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================
# Fungsi bantu
# =====================
@st.cache_resource
def remove_bg(image_bytes):
    """Caching penghapusan background"""
    return remove(image_bytes)

def resize_for_preview(img, max_size=1024):
    """Resize foto besar agar pemrosesan lebih cepat"""
    img_copy = img.copy()
    img_copy.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return img_copy

# =====================
# Header
# =====================
st.title("📸 Editor Foto Pro")
st.write("Editor foto dengan fitur AI: hapus background, ubah warna, dan buat pasfoto.")

# =====================
# Ukuran standar
# =====================
photo_sizes = {
    "2x3 cm": (236, 354),
    "3x4 cm": (354, 472),
    "4x6 cm": (472, 709),
    "5x7 cm": (591, 827),
    "6x9 cm": (709, 1063)
}

# =====================
# Upload foto
# =====================
uploaded_file = st.file_uploader("📤 Unggah foto Anda", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image = resize_for_preview(image)

    st.image(image, caption="Foto Asli", use_container_width=True)

    # Panel pengaturan
    st.subheader("⚙️ Pengaturan Foto")
    size_option = st.selectbox("Pilih ukuran foto:", list(photo_sizes.keys()))
    target_w, target_h = photo_sizes[size_option]

    bg_option = st.radio(
        "Jenis latar belakang:",
        ["Pertahankan Asli", "Hapus + Warna Solid", "Hapus + Transparan"]
    )
    bg_color = "#FFFFFF"
    if bg_option == "Hapus + Warna Solid":
        bg_color = st.color_picker("Warna latar belakang:", "#FFFFFF")

    grayscale = st.checkbox("Ubah ke Hitam Putih", value=False)

    x_offset = st.slider("Posisi horizontal", -200, 200, 0)
    y_offset = st.slider("Posisi vertikal", -200, 200, 0)

    if st.button("🚀 Proses Foto", use_container_width=True):
        with st.spinner("🔄 Memproses foto..."):
            try:
                # Hapus background jika dipilih
                if bg_option.startswith("Hapus"):
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    result_bytes = remove_bg(img_bytes)
                    processed_image = Image.open(BytesIO(result_bytes)).convert("RGBA")
                else:
                    processed_image = image.convert("RGBA")

                img_np = np.array(processed_image)

                # Hitung rasio & crop
                original_w, original_h = processed_image.size
                aspect_ratio = original_w / original_h
                target_aspect = target_w / target_h

                if aspect_ratio > target_aspect:
                    new_width = int(original_h * target_aspect)
                    start_x = max(0, min((original_w - new_width) // 2 + x_offset, original_w - new_width))
                    cropped = img_np[:, start_x:start_x + new_width]
                else:
                    new_height = int(original_w / target_aspect)
                    start_y = max(0, min((original_h - new_height) // 2 + y_offset, original_h - new_height))
                    cropped = img_np[start_y:start_y + new_height, :]

                result = Image.fromarray(cropped).resize((target_w, target_h), Image.Resampling.LANCZOS)

                # Tambah background
                if bg_option == "Hapus + Warna Solid":
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    background = Image.new("RGB", (target_w, target_h), bg_rgb).convert("RGBA")
                    result = Image.alpha_composite(background, result.convert("RGBA"))
                    result = result.convert("RGB")
                elif bg_option == "Hapus + Transparan":
                    result = result.convert("RGBA")
                else:
                    result = result.convert("RGB")

                # Konversi grayscale (full hitam putih natural)
                if grayscale:
                    result = ImageOps.grayscale(result).convert("RGB")
                    enhancer = ImageEnhance.Contrast(result)
                    result = enhancer.enhance(1.2)  # 1.0 = normal, >1 = lebih kontras

                # Tampilkan hasil
                st.success("✅ Foto berhasil diproses!")
                st.image(result, caption=f"Hasil {size_option}", use_container_width=True)

                # Download
                buf = BytesIO()
                if bg_option == "Hapus + Transparan":
                    result.save(buf, format="PNG")
                    file_ext, mime_type = "png", "image/png"
                else:
                    result.save(buf, format="JPEG", quality=95)
                    file_ext, mime_type = "jpg", "image/jpeg"

                st.download_button(
                    "📥 Unduh Foto",
                    data=buf.getvalue(),
                    file_name=f"foto_{size_option.replace(' ', '_')}.{file_ext}",
                    mime=mime_type
                )

            except Exception as e:
                st.error(f"❌ Gagal memproses: {e}")

else:
    st.info("📤 Unggah foto untuk mulai mengedit.")

