import streamlit as st
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO
from rembg import remove
import numpy as np

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
    
    st.subheader("Atur Posisi dan Ukuran Foto")
    
    # Preview area dengan slider controls
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.write("**Kontrol Posisi & Zoom:**")
        zoom = st.slider("Zoom", 0.3, 3.0, 1.0, 0.1)
        
        # Hitung ukuran gambar setelah zoom
        zoomed_w = int(image.width * zoom)
        zoomed_h = int(image.height * zoom)
        
        # Slider untuk posisi
        max_x = max(0, zoomed_w - target_w)
        max_y = max(0, zoomed_h - target_h)
        
        pos_x = st.slider("Posisi Horizontal", 0, max_x, max_x//2 if max_x > 0 else 0)
        pos_y = st.slider("Posisi Vertikal", 0, max_y, max_y//2 if max_y > 0 else 0)
        
        st.write(f"**Target Size:** {target_w} x {target_h} px")
        st.write(f"**Zoom Size:** {zoomed_w} x {zoomed_h} px")
    
    with col1:
        # Buat preview dengan crop area
        preview_img = image.resize((zoomed_w, zoomed_h), Image.Resampling.LANCZOS)
        
        # Buat gambar preview dengan frame crop
        preview_canvas = Image.new("RGB", (target_w + 40, target_h + 40), (240, 240, 240))
        
        # Crop area dari gambar yang sudah di-zoom
        crop_left = pos_x
        crop_top = pos_y
        crop_right = min(pos_x + target_w, zoomed_w)
        crop_bottom = min(pos_y + target_h, zoomed_h)
        
        # Paste bagian yang akan di-crop ke preview canvas
        if crop_right > crop_left and crop_bottom > crop_top:
            cropped_preview = preview_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            preview_canvas.paste(cropped_preview, (20, 20))
        
        # Tambahkan border untuk menunjukkan area crop
        draw = ImageDraw.Draw(preview_canvas)
        draw.rectangle([20, 20, 20 + target_w, 20 + target_h], outline="red", width=2)
        
        st.image(preview_canvas, caption=f"Preview Crop Area ({size_option})", use_container_width=True)
    
    # Area untuk menampilkan koordinat crop
    st.info(f"📍 **Crop Coordinates:** X={pos_x}, Y={pos_y}, Width={min(target_w, zoomed_w-pos_x)}, Height={min(target_h, zoomed_h-pos_y)}")
    
    # Manual adjustment (opsional)
    with st.expander("🔧 Penyesuaian Manual (Opsional)"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            manual_x = st.number_input("X Manual", min_value=0, max_value=zoomed_w, value=pos_x)
        with col2:
            manual_y = st.number_input("Y Manual", min_value=0, max_value=zoomed_h, value=pos_y)
        with col3:
            manual_w = st.number_input("Width Manual", min_value=1, max_value=target_w, value=min(target_w, zoomed_w-pos_x))
        with col4:
            manual_h = st.number_input("Height Manual", min_value=1, max_value=target_h, value=min(target_h, zoomed_h-pos_y))
        
        use_manual = st.checkbox("Gunakan koordinat manual")
        if use_manual:
            pos_x, pos_y = manual_x, manual_y
    
    # Tombol proses
    if st.button("🔄 Proses Pas Foto", type="primary"):
        try:
            with st.spinner("Memproses foto..."):
                # Resize gambar sesuai zoom
                zoomed_img = image.resize((zoomed_w, zoomed_h), Image.Resampling.LANCZOS)
                
                # Crop sesuai posisi yang dipilih
                crop_right = min(pos_x + target_w, zoomed_w)
                crop_bottom = min(pos_y + target_h, zoomed_h)
                
                if crop_right > pos_x and crop_bottom > pos_y:
                    cropped_img = zoomed_img.crop((pos_x, pos_y, crop_right, crop_bottom))
                else:
                    st.error("❌ Area crop tidak valid!")
                    st.stop()
                
                # Pastikan ukuran sesuai target (resize jika perlu)
                if cropped_img.size != (target_w, target_h):
                    cropped_img = cropped_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # Proses background removal jika diperlukan
                if bg_mode in ["Ganti Warna", "Ganti Gambar"]:
                    # Convert ke bytes untuk rembg
                    img_bytes = BytesIO()
                    cropped_img.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    
                    # Remove background
                    result_bytes = remove(img_bytes)
                    img_no_bg = Image.open(BytesIO(result_bytes)).convert("RGBA")
                else:
                    img_no_bg = cropped_img.convert("RGBA")
                
                # Apply grayscale jika dipilih
                if grayscale:
                    # Convert ke grayscale tapi tetap RGBA untuk transparency
                    gray_img = ImageOps.grayscale(img_no_bg.convert("RGB"))
                    img_no_bg = gray_img.convert("RGBA")
                    if bg_mode in ["Ganti Warna", "Ganti Gambar"]:
                        # Restore alpha channel untuk background removal
                        original_alpha = Image.open(BytesIO(result_bytes)).split()[-1]
                        img_no_bg.putalpha(original_alpha)
                
                # Buat background sesuai pilihan
                if bg_mode == "Ganti Warna":
                    # Convert hex to RGB
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    background = Image.new("RGB", (target_w, target_h), bg_rgb)
                    background = background.convert("RGBA")
                    final_img = Image.alpha_composite(background, img_no_bg)
                elif bg_mode == "Ganti Gambar" and bg_image:
                    background = bg_image.resize((target_w, target_h)).convert("RGBA")
                    final_img = Image.alpha_composite(background, img_no_bg)
                else:
                    final_img = img_no_bg
                
                # Convert ke RGB untuk output final
                final_img = final_img.convert("RGB")
            
            # Tampilkan hasil
            st.success("✅ Pas foto berhasil dibuat!")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.image(final_img, caption=f"Hasil Pas Foto {size_option} ({target_w}×{target_h}px)")
            
            with col2:
                st.write("**📊 Info Hasil:**")
                st.write(f"• Ukuran: {size_option}")
                st.write(f"• Dimensi: {target_w}×{target_h}px")
                st.write(f"• Background: {bg_mode}")
                st.write(f"• Grayscale: {'Ya' if grayscale else 'Tidak'}")
            
            # Tombol download
            buf = BytesIO()
            final_img.save(buf, format="JPEG", quality=95)
            st.download_button(
                label="📥 Download Pas Foto",
                data=buf.getvalue(),
                file_name=f"pas_foto_{size_option}_{target_w}x{target_h}.jpg",
                mime="image/jpeg",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
            st.info("💡 Coba adjust posisi dan zoom, atau upload foto dengan format yang berbeda")

else:
    st.info("📤 Silakan upload foto terlebih dahulu untuk memulai")
    st.markdown("""
    ### 🔧 Fitur Editor:
    - ✅ Crop foto dengan preview real-time
    - ✅ Multiple ukuran pas foto standar
    - ✅ Background removal otomatis
    - ✅ Ganti background (warna/gambar)
    - ✅ Konversi ke hitam-putih
    - ✅ Zoom dan positioning yang presisi
    """)
