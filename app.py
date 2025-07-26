import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from rembg import remove
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Konfigurasi halaman
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
    
    # Pilih ukuran pas foto
    size_option = st.selectbox("Pilih ukuran pas foto:", list(photo_sizes.keys()))
    target_w, target_h = photo_sizes[size_option]
    
    # Pilihan mode background
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
    
    # Opsi grayscale
    grayscale = st.checkbox("Ubah ke Hitam Putih", value=False)
    
    st.subheader("Atur Posisi Foto (Drag & Zoom)")
    canvas_width, canvas_height = 500, 700
    zoom = st.slider("Zoom", 0.5, 3.0, 1.0, 0.1)
    
    # Resize foto untuk preview canvas
    img_zoomed = image.resize((int(image.width * zoom), int(image.height * zoom)))
    
    # Resize ke ukuran canvas untuk display
    display_img = img_zoomed.copy()
    if display_img.width > canvas_width or display_img.height > canvas_height:
        display_img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    
    st.write("Geser foto di area canvas untuk mengatur posisi.")
    
    # Canvas untuk positioning (tanpa background image untuk menghindari error)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.1)",  # Transparant orange untuk area selection
        stroke_width=2,
        stroke_color="#FF6600",
        background_color="#F0F0F0",
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="rect",  # Mode rectangle selection
        point_display_radius=0,
        key="canvas"
    )
    
    # Preview area
    col1, col2 = st.columns(2)
    with col1:
        st.image(display_img, caption="Preview Foto", use_container_width=True)
    
    # Input manual untuk crop area (alternatif untuk canvas)
    st.subheader("Atau Atur Crop Manual")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        crop_x = st.number_input("X (kiri)", min_value=0, max_value=image.width, value=0)
    with col2:
        crop_y = st.number_input("Y (atas)", min_value=0, max_value=image.height, value=0)
    with col3:
        crop_w = st.number_input("Lebar", min_value=1, max_value=image.width, value=min(image.width, target_w))
    with col4:
        crop_h = st.number_input("Tinggi", min_value=1, max_value=image.height, value=min(image.height, target_h))
    
    # Tombol proses
    if st.button("Proses Foto"):
        try:
            # Crop gambar berdasarkan input
            cropped_img = image.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
            
            # Hapus background jika perlu
            if bg_mode in ["Ganti Warna", "Ganti Gambar"]:
                with st.spinner("Menghapus background..."):
                    # Convert ke bytes untuk rembg
                    img_bytes = BytesIO()
                    cropped_img.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    
                    # Remove background
                    result_bytes = remove(img_bytes)
                    img_no_bg = Image.open(BytesIO(result_bytes)).convert("RGBA")
            else:
                img_no_bg = cropped_img.convert("RGBA")
            
            # Resize ke ukuran pas foto dengan mempertahankan aspect ratio
            img_no_bg.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Buat canvas dengan ukuran target
            final_canvas = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
            
            # Center image pada canvas
            x_offset = (target_w - img_no_bg.width) // 2
            y_offset = (target_h - img_no_bg.height) // 2
            
            # Grayscale jika dipilih
            if grayscale:
                img_no_bg = ImageOps.grayscale(img_no_bg).convert("RGBA")
            
            # Tambahkan background sesuai pilihan
            if bg_mode == "Ganti Warna":
                # Convert hex to RGBA
                bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                background = Image.new("RGBA", (target_w, target_h), bg_rgb + (255,))
                background.paste(img_no_bg, (x_offset, y_offset), img_no_bg)
                final_img = background
            elif bg_mode == "Ganti Gambar" and bg_image:
                background = bg_image.resize((target_w, target_h)).convert("RGBA")
                background.paste(img_no_bg, (x_offset, y_offset), img_no_bg)
                final_img = background
            else:
                final_canvas.paste(img_no_bg, (x_offset, y_offset), img_no_bg)
                final_img = final_canvas
            
            # Tampilkan hasil
            st.success("✅ Foto berhasil diproses!")
            st.image(final_img, caption=f"Hasil Pas Foto {size_option} ({target_w}x{target_h}px)", use_container_width=False)
            
            # Simpan & unduh
            buf = BytesIO()
            final_img.convert("RGB").save(buf, format="JPEG", quality=95)
            st.download_button(
                label="📥 Unduh Pas Foto",
                data=buf.getvalue(),
                file_name=f"pas_foto_{size_option}.jpg",
                mime="image/jpeg"
            )
            
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
            st.info("💡 Tips: Pastikan area crop tidak melebihi ukuran gambar asli")

else:
    st.info("📤 Unggah foto terlebih dahulu untuk memulai.")
