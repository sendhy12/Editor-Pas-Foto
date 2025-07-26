import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from rembg import remove
import numpy as np
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Editor Pas Foto Lengkap", layout="centered")
st.title("📸 Editor Pas Foto Lengkap")

# Pilihan ukuran pas foto
photo_sizes = {
    "2x3": (236, 354),
    "3x4": (354, 472),
    "4x6": (472, 709),
    "5x7": (591, 827),
    "6x9": (709, 1063)
}

# Upload foto utama
uploaded_file = st.file_uploader("Unggah foto (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Foto Asli", use_container_width=True)

    # Pilihan ukuran pas foto
    size_option = st.selectbox("Pilih ukuran pas foto:", list(photo_sizes.keys()))
    target_w, target_h = photo_sizes[size_option]

    # Pilihan warna latar atau gambar latar
    st.subheader("Opsi Background")
    bg_mode = st.radio("Pilih mode background:", ["Tetap (asli)", "Ganti Warna", "Ganti Gambar"])
    bg_color = "#FFFFFF"
    bg_image = None

    if bg_mode == "Ganti Warna":
        bg_color = st.color_picker("Pilih warna background", "#FFFFFF")
    elif bg_mode == "Ganti Gambar":
        bg_image_file = st.file_uploader("Unggah gambar background", type=["jpg", "jpeg", "png"])
        if bg_image_file:
            bg_image = Image.open(bg_image_file).convert("RGB")

    # Pilihan grayscale
    grayscale = st.checkbox("Ubah ke Hitam Putih", value=False)

    st.subheader("Atur Posisi Foto (Drag & Zoom)")
    canvas_width, canvas_height = 500, 700
    zoom = st.slider("Zoom", 0.5, 3.0, 1.0, 0.1)

    # Resize gambar untuk canvas
    img_zoomed = image.resize((int(image.width * zoom), int(image.height * zoom)))

    # Canvas interaktif
    st.write("Geser foto di area canvas untuk mengatur posisi.")
    st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=0,
        background_image=img_zoomed,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="transform",
        key="canvas"
    )

    if st.button("Proses Foto"):
        # Langkah 1: Hapus background jika mode bukan 'Tetap'
        if bg_mode in ["Ganti Warna", "Ganti Gambar"]:
            with st.spinner("Menghapus background..."):
                img_no_bg = remove(image)
        else:
            img_no_bg = image.convert("RGBA")

        # Langkah 2: Resize ke target ukuran
        img_resized = img_no_bg.resize((target_w, target_h))

        # Langkah 3: Grayscale jika dipilih
        if grayscale:
            img_resized = ImageOps.grayscale(img_resized).convert("RGBA")

        # Langkah 4: Tambahkan background
        if bg_mode == "Ganti Warna":
            background = Image.new("RGBA", img_resized.size, bg_color)
            final_img = Image.alpha_composite(background, img_resized)
        elif bg_mode == "Ganti Gambar" and bg_image:
            background = bg_image.resize(img_resized.size).convert("RGBA")
            final_img = Image.alpha_composite(background, img_resized)
        else:
            final_img = img_resized

        # Tampilkan hasil
        st.image(final_img, caption=f"Hasil Pas Foto {size_option}", use_container_width=False)

        # Simpan & unduh
        buf = BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG")
        st.download_button(
            label="📥 Unduh Pas Foto",
            data=buf.getvalue(),
            file_name=f"pas_foto_{size_option}.jpg",
            mime="image/jpeg"
        )

else:
    st.info("📤 Unggah foto terlebih dahulu untuk memulai.")
