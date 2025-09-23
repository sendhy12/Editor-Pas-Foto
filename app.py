import streamlit as st
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
from rembg import remove
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Editor Foto",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS khusus untuk tampilan modern
def load_css():
    st.markdown("""
    <style>
    /* Import font modern */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variabel root untuk tema konsisten */
    :root {
        --primary-color: #6366f1;
        --primary-hover: #5855eb;
        --secondary-color: #f1f5f9;
        --accent-color: #10b981;
        --danger-color: #ef4444;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --background: #ffffff;
        --surface: #f8fafc;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius: 12px;
        --radius-sm: 8px;
    }
    
    /* Styling aplikasi utama */
    .main {
        padding: 2rem 3rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sembunyikan elemen default Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header khusus */
    .app-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        padding: 2rem 3rem;
        margin: -2rem -3rem 3rem -3rem;
        border-radius: 0 0 var(--radius) var(--radius);
        color: white;
        box-shadow: var(--shadow-lg);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Komponen kartu */
    .card {
        background: var(--background);
        border-radius: var(--radius);
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--secondary-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Styling area upload */
    .upload-area {
        border: 2px dashed var(--border-color);
        border-radius: var(--radius);
        padding: 3rem;
        text-align: center;
        background: var(--surface);
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: var(--primary-color);
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* Styling tombol */
    .stButton > button {
        background: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow) !important;
    }
    
    .stButton > button:hover {
        background: var(--primary-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Varian tombol sukses */
    .success-button > button {
        background: var(--accent-color) !important;
    }
    
    /* Styling tombol download */
    .stDownloadButton > button {
        background: var(--accent-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow) !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        background: #059669 !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Styling kontrol form */
    .stSelectbox > div > div {
        background: var(--background) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: var(--shadow) !important;
    }
    
    .stRadio > div {
        background: var(--surface) !important;
        padding: 1rem !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stSlider > div > div > div {
        background: var(--primary-color) !important;
    }
    
    /* Styling tampilan gambar */
    .image-container {
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        margin: 1rem 0;
    }
    
    /* Bagian info */
    .info-section {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
    }
    
    .info-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .info-text {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* Kartu statistik */
    .stats-card {
        background: var(--background);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        text-align: center;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
    }
    
    .stats-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Grid fitur */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        background: var(--background);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Indikator proses */
    .progress-container {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        margin: 2rem 0;
        text-align: center;
    }
    
    /* Desain responsif */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        .app-header {
            padding: 1.5rem;
            margin: -1rem -1rem 2rem -1rem;
        }
        
        .app-title {
            font-size: 2rem;
        }
        
        .card {
            padding: 1.5rem;
        }
    }
    
    /* Peringatan khusus */
    .stAlert {
        border-radius: var(--radius-sm) !important;
        border: none !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: var(--surface) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius) !important;
        padding: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Komponen khusus
def create_header():
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">
            📸 Editor Foto Paspor Pro
        </h1>
        <p class="app-subtitle">
            Editor foto profesional dengan AI untuk menghapus latar belakang
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_card(title, content, icon=""):
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            {icon} {title}
        </div>
        <div class="card-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_feature_grid():
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">📏</div>
            <div class="feature-title">Ukuran Standar</div>
            <div class="feature-description">Berbagai ukuran foto dengan kualitas 300 DPI</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Hapus Latar Belakang</div>
            <div class="feature-description">Penghapusan latar belakang otomatis dengan AI dan pilihan warna custom</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⚫</div>
            <div class="feature-title">Konversi Hitam Putih</div>
            <div class="feature-description">Opsi konversi ke hitam putih yang profesional</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Posisi Pintar</div>
            <div class="feature-description">Pemotongan otomatis dengan penyesuaian manual</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load CSS
load_css()

# Buat header
create_header()

# Konfigurasi ukuran foto
photo_sizes = {
    "2x3 cm": (236, 354),
    "3x4 cm": (354, 472),
    "4x6 cm": (472, 709),
    "5x7 cm": (591, 827),
    "6x9 cm": (709, 1063)
}

# Aplikasi utama
col1, col2 = st.columns([2, 1])

with col1:
    # Bagian upload file
    st.markdown("""
    <div class="card">
        <div class="card-header">
            📁 Unggah Foto Anda
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Pilih foto Anda",
        type=["jpg", "jpeg", "png"],
        help="Unggah foto yang jelas dengan pencahayaan baik untuk hasil terbaik"
    )

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    
    # Tampilkan gambar asli
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                🖼️ Foto Asli
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.image(image, use_container_width=True)
    
    # Panel pengaturan
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                ⚙️ Pengaturan Foto
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pemilihan ukuran
        st.subheader("📏 Pilih Ukuran")
        size_option = st.selectbox(
            "Pilih ukuran foto paspor:",
            list(photo_sizes.keys()),
            help="Ukuran foto paspor standar dengan resolusi 300 DPI"
        )
        target_w, target_h = photo_sizes[size_option]
        
        # Opsi latar belakang
        st.subheader("🎨 Pilihan Latar Belakang")
        bg_option = st.radio(
            "Jenis latar belakang:",
            [
                "Pertahankan Asli", 
                "Hapus + Warna Solid", 
                "Hapus + Transparan"
            ]
        )
        
        bg_color = "#FFFFFF"
        if bg_option == "Hapus + Warna Solid":
            bg_color = st.color_picker("Warna latar belakang:", "#FFFFFF")
        
        # Opsi tambahan
        st.subheader("🎛️ Opsi Tambahan")
        grayscale = st.checkbox("Ubah ke Hitam Putih", value=False)
        
        # Penyesuaian posisi
        st.subheader("📐 Penyesuaian Posisi")
        x_offset = st.slider("Posisi horizontal", -200, 200, 0, help="Geser subjek ke kiri/kanan")
        y_offset = st.slider("Posisi vertikal", -200, 200, 0, help="Geser subjek ke atas/bawah")
        
        # Tombol proses
        st.markdown("<br>", unsafe_allow_html=True)
        process_button = st.button("🚀 Proses Foto", type="primary", use_container_width=True)

    # Pemrosesan dan hasil
    if process_button:
        with st.spinner("🔄 Sedang memproses foto Anda..."):
            try:
                # Penghapusan latar belakang
                if bg_option.startswith("Hapus"):
                    st.info("🤖 Penghapusan latar belakang AI sedang berjalan...")
                    
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    
                    result_bytes = remove(img_bytes)
                    processed_image = Image.open(BytesIO(result_bytes)).convert("RGBA")
                else:
                    processed_image = image.convert("RGBA")
                
                # Pemrosesan gambar
                img_np = np.array(processed_image)
                
                # Hitung rasio aspek dan potong
                original_h, original_w = processed_image.size[1], processed_image.size[0]
                aspect_ratio = original_w / original_h
                target_aspect = target_w / target_h
                
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
                
                # Ubah ukuran
                result = Image.fromarray(cropped).resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # Pemrosesan latar belakang
                if bg_option == "Hapus + Warna Solid":
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    background = Image.new("RGB", (target_w, target_h), bg_rgb)
                    background = background.convert("RGBA")
                    result = Image.alpha_composite(background, result.convert("RGBA"))
                    result = result.convert("RGB")
                elif bg_option == "Hapus + Transparan":
                    result = result.convert("RGBA")
                else:
                    result = result.convert("RGB")
                
                # Konversi hitam putih
                if grayscale:
                    if result.mode == "RGBA":
                        alpha = result.split()[-1]
                        rgb_result = result.convert("RGB")
                        gray_result = ImageOps.grayscale(rgb_result)
                        result = gray_result.convert("RGBA")
                        result.putalpha(alpha)
                    else:
                        result = ImageOps.grayscale(result)
                
                # Tampilkan hasil
                st.success("✅ Foto berhasil diproses!")
                
                col_result1, col_result2 = st.columns([3, 1])
                
                with col_result1:
                    st.markdown("""
                    <div class="card">
                        <div class="card-header">
                            🎉 Hasil Akhir
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.image(result, caption=f"Foto Paspor {size_option}")
                
                with col_result2:
                    # Info foto
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-number">{size_option}</div>
                        <div class="stats-label">Ukuran</div>
                    </div>
                    
                    <div class="stats-card" style="margin-top: 1rem;">
                        <div class="stats-number">{target_w}×{target_h}</div>
                        <div class="stats-label">Piksel</div>
                    </div>
                    
                    <div class="info-section" style="margin-top: 1rem;">
                        <div class="info-title">Detail Pemrosesan</div>
                        <div class="info-text">
                            <strong>Latar Belakang:</strong> {bg_option}<br>
                            <strong>Hitam Putih:</strong> {'Ya' if grayscale else 'Tidak'}<br>
                            <strong>Posisi:</strong> X={x_offset}, Y={y_offset}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Bagian download
                st.markdown("""
                <div class="card">
                    <div class="card-header">
                        💾 Unduh Foto Anda
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                buf = BytesIO()
                
                if bg_option == "Hapus + Transparan":
                    result.save(buf, format="PNG")
                    file_ext = "png"
                    mime_type = "image/png"
                else:
                    if result.mode == "RGBA":
                        result = result.convert("RGB")
                    result.save(buf, format="JPEG", quality=95)
                    file_ext = "jpg"
                    mime_type = "image/jpeg"
                
                st.download_button(
                    label=f"📥 Unduh Foto Paspor (.{file_ext})",
                    data=buf.getvalue(),
                    file_name=f"foto_paspor_{size_option.replace(' ', '_')}_{target_w}x{target_h}.{file_ext}",
                    mime=mime_type
                )
                
            except Exception as e:
                st.error(f"❌ Pemrosesan gagal: {str(e)}")
                st.info("💡 **Tips:** Pastikan foto Anda memiliki subjek yang jelas untuk hasil penghapusan latar belakang yang optimal")

else:
    # Layar selamat datang
    st.markdown("""
    <div class="card">
        <div class="card-header">
            👋 Selamat Datang di Editor Foto Paspor Pro
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📤 **Mulai Sekarang:** Unggah foto Anda di atas untuk mulai membuat foto paspor profesional")
    
    create_feature_grid()
    
    # Tips penggunaan
    st.markdown("""
    <div class="card">
        <div class="card-header">
            💡 Tips Pro untuk Hasil Terbaik
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown("""
        <div class="info-section">
            <div class="info-title">📷 Kualitas Foto</div>
            <div class="info-text">
                • Gunakan foto dengan pencahayaan baik dan resolusi tinggi<br>
                • Pastikan subjek terlihat jelas<br>
                • Hindari bayangan dan pantulan cahaya
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tips_col2:
        st.markdown("""
        <div class="info-section">
            <div class="info-title">🎯 Posisi</div>
            <div class="info-text">
                • Pusatkan subjek di dalam bingkai<br>
                • Gunakan slider posisi untuk penyesuaian halus<br>
                • Coba berbagai warna latar belakang
            </div>
        </div>
        """, unsafe_allow_html=True)
