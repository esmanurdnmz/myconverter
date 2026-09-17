import streamlit as st
import subprocess
import os
import tempfile
import zipfile
from io import BytesIO

# Sayfa ayarları (Geniş ekran ve tatlı bir ikon)
st.set_page_config(page_title="Engineer Diva - Sınırsız Çevirici", page_icon="🎀", layout="wide")

# CSS ile Soft Pembe Arka Plan ve Özel Tasarım
st.markdown("""
    <style>
    /* Tüm sayfanın arka planını soft pudra pembesi yap */
    .stApp {
        background-color: #FFE4E1; 
    }

    /* Yazı tipleri ve renkleri */
    .baslik {
        font-family: 'Courier New', Courier, monospace;
        color: #D2386C;
        text-align: center;
        font-weight: bold;
    }

    /* Yükleme alanının çerçevesi */
    .stFileUploader {
        border-radius: 15px;
        background-color: #FFF0F5;
        padding: 10px;
    }

    /* Dönüştür Butonu Tasarımı */
    div.stButton > button:first-child {
        background-color: #FF69B4;
        color: white;
        border-radius: 20px;
        border: 2px solid #FF1493;
        padding: 10px 30px;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #FF1493;
        border-color: #C71585;
    }
    </style>
""", unsafe_allow_html=True)

# Üst Kısım: Başlık ve Süsleme Resimleri
col_baslik1, col_baslik2, col_baslik3 = st.columns([1, 2, 1])

with col_baslik1:
    try:
        st.image("r1.jpg", use_container_width=True)  # Piksel kedi
    except:
        pass

with col_baslik2:
    st.markdown("<h1 class='baslik'>✨ @engineerdivaesmanur ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='baslik'>Tatlı Sınırsız Format Dönüştürücüsü 💖</h3>", unsafe_allow_html=True)

with col_baslik3:
    try:
        st.image("r2.jpg", use_container_width=True)  # Mühendis kedi
    except:
        pass

st.write("---")

# Orta Kısım: Ana İşlem ve Diğer Resimler
col_sol, col_orta, col_sag = st.columns([1, 2, 1])

with col_sol:
    try:
        st.image("r3.jpg", use_container_width=True)  # Kod yazan Esmanur
    except:
        pass

with col_orta:
    # 1. Hangi formata çevrileceğini seçtirme
    target_format = st.selectbox(
        "Hangi formata çevirmek istersin?",
        ["pdf", "docx", "odt", "txt", "html"]
    )

    # 2. Dosya yükleme alanı (Tüm dosya tiplerine açık ve çoklu yükleme aktif)
    uploaded_files = st.file_uploader(
        "Dosyalarını buraya bırak tatlım 🌸 (Word, Excel, PowerPoint, Metin vb.)",
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("💖 Sihirli Çeviriyi Başlat 💖"):
            with st.spinner("Arka planda sihir gerçekleşiyor, lütfen bekle... ✨"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    converted_files = []

                    # 3. Yüklenen tüm dosyaları tek tek döngüye alıp çevirme
                    for uploaded_file in uploaded_files:
                        input_path = os.path.join(temp_dir, uploaded_file.name)

                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        command = [
                            "libreoffice", "--headless", "--convert-to", target_format,
                            input_path, "--outdir", temp_dir
                        ]

                        try:
                            subprocess.run(command, check=True, capture_output=True)

                            pdf_filename = uploaded_file.name.rsplit('.', 1)[0] + f".{target_format}"
                            pdf_path = os.path.join(temp_dir, pdf_filename)

                            if os.path.exists(pdf_path):
                                converted_files.append((pdf_filename, pdf_path))
                            else:
                                st.error(
                                    f"❌ {uploaded_file.name} dönüştürülemedi. (Altyapı bu formatı desteklemiyor olabilir)")
                        except Exception as e:
                            st.error(f"Sistemsel bir hata oluştu: {e}")

                    # 4. Çıktıları kullanıcıya sunma
                    if len(converted_files) == 1:
                        # Tek dosya ise doğrudan indir
                        filename, path = converted_files[0]
                        with open(path, "rb") as f:
                            st.success("🎉 Ta-da! Dosyan hazır!")
                            st.download_button(
                                label=f"🎀 {filename} İndir 🎀",
                                data=f.read(),
                                file_name=filename,
                                mime="application/octet-stream"
                            )
                    elif len(converted_files) > 1:
                        # Birden fazla dosya ise ZIP oluştur
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for filename, path in converted_files:
                                zip_file.write(path, filename)

                        st.success("🎉 Tüm dosyaların başarıyla çevrildi ve birleştirildi!")
                        st.download_button(
                            label="🎀 Tümünü ZIP Olarak İndir 🎀",
                            data=zip_buffer.getvalue(),
                            file_name="Diva_Ceviriler.zip",
                            mime="application/zip"
                        )

with col_sag:
    try:
        st.image("r4.jpg", use_container_width=True)  # Esmanur portre
        st.write("")  # Boşluk
        st.image("Bratz.jpg", use_container_width=True)  # PC başındaki kedi
    except:
        pass