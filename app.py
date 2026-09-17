import streamlit as st
import subprocess
import os
import tempfile
import zipfile
from io import BytesIO
import platform

try:
    from PyPDF2 import PdfMerger, PdfReader, PdfWriter
except ImportError:
    st.error("Lütfen terminalde 'pip install PyPDF2' çalıştırın.")

st.set_page_config(page_title="Engineer Diva - PDF İstasyonu", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #FCE4EC; /* Soft Pudra Pembe */
    }

    p, label, .stSelectbox label, .stFileUploader label, li, span {
        color: #880E4F !important;
        font-weight: 600;
    }
    h1, h2, h3 {
        color: #D81B60 !important;
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
        font-weight: bold;
    }

    .stFileUploader > div > div {
        background-color: #F8BBD0;
        border-radius: 15px;
        border: 2px dashed #D81B60;
    }

    div.stButton > button {
        background-color: #F06292 !important;
        color: white !important;
        border-radius: 20px;
        border: 2px solid #E91E63 !important;
        width: 100%;
        padding: 10px;
    }
    div.stButton > button:hover {
        background-color: #E91E63 !important;
        box-shadow: 0px 4px 10px rgba(233, 30, 99, 0.4);
    }

    /* Sağ üstteki menüyü, alt bilgiyi ve üst boşluğu gizle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Mobilde alt alta kaymayı iptal edip yan yana göstermeye zorlar */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto;
        }
        div[data-testid="column"] {
            min-width: auto !important;
            padding: 0 2px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Sayfayı kolonlara bölerek resimleri dağınık yerleştirme
col1, col2, col_ana, col4, col5 = st.columns([1, 1, 4, 1, 1])

with col1:
    st.markdown("<br><br>", unsafe_allow_html=True)
    try:
        st.image("_.jpeg", use_container_width=True)
    except:
        pass

with col2:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    try:
        st.image("IMG_9272.jpg", use_container_width=True)
    except:
        pass

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        st.image("_ (2).jpeg", use_container_width=True)
    except:
        pass

with col5:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    try:
        st.image("IMG_0359.jpg", use_container_width=True)
    except:
        pass

# ORTA ALAN: Ana Uygulama Sekmeleri
with col_ana:
    st.markdown("<h1>✨ @engineerdivaesmanur ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Tatlı PDF İstasyonu 💖</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Office ↔ PDF", "🖼️ PDF ↔ JPG", "➕ PDF Birleştir", "✂️ PDF Ayır"])


    def convert_with_libreoffice(uploaded_files, target_format):
        with tempfile.TemporaryDirectory() as temp_dir:
            converted_files = []
            lo_cmd = "/Applications/LibreOffice.app/Contents/MacOS/soffice" if platform.system() == "Darwin" else "libreoffice"
            for uploaded_file in uploaded_files:
                input_path = os.path.join(temp_dir, uploaded_file.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                command = [lo_cmd, "--headless", "--convert-to", target_format, input_path, "--outdir", temp_dir]
                try:
                    subprocess.run(command, check=True, capture_output=True)
                    out_filename = uploaded_file.name.rsplit('.', 1)[0] + f".{target_format}"
                    out_path = os.path.join(temp_dir, out_filename)
                    if os.path.exists(out_path):
                        with open(out_path, "rb") as f:
                            converted_files.append((out_filename, f.read()))
                except Exception as e:
                    st.error(f"Hata: {e}")
            return converted_files


    # --- ARAÇ 1: OFFICE <-> PDF ---
    with tab1:
        st.info("Word, Excel, PowerPoint dosyalarını PDF'e veya PDF'i Word'e çevir.")
        conversion_type = st.selectbox("İşlemi seç:", [
            "Word'den PDF'e (docx -> pdf)",
            "PowerPoint'ten PDF'e (pptx -> pdf)",
            "Excel'den PDF'e (xlsx -> pdf)",
            "PDF'den Word'e (pdf -> docx)"
        ])

        target_ext = conversion_type.split("->")[1].strip().replace(")", "")
        source_ext = conversion_type.split("->")[0].split("(")[1].strip()

        up_files_office = st.file_uploader("Dosyaları yükle 🌸", accept_multiple_files=True, key="offc")

        if up_files_office and st.button("💖 Dönüştür 💖", key="btn_offc"):
            with st.spinner("İşleniyor... ✨"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    converted_files = []
                    lo_cmd = "/Applications/LibreOffice.app/Contents/MacOS/soffice" if platform.system() == "Darwin" else "libreoffice"

                    for uploaded_file in up_files_office:
                        input_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        out_filename = uploaded_file.name.rsplit('.', 1)[0] + f".{target_ext}"
                        out_path = os.path.join(temp_dir, out_filename)

                        try:
                            # PDF'den Word'e özel durum (pdf2docx kütüphanesi kullanılır)
                            if source_ext == "pdf" and target_ext == "docx":
                                from pdf2docx import Converter

                                cv = Converter(input_path)
                                cv.convert(out_path, start=0, end=None)
                                cv.close()
                                if os.path.exists(out_path):
                                    with open(out_path, "rb") as f:
                                        converted_files.append((out_filename, f.read()))

                            # Diğer her şey (Word/Excel/PPT -> PDF) LibreOffice ile yapılır
                            else:
                                command = [lo_cmd, "--headless", "--convert-to", target_ext, input_path, "--outdir",
                                           temp_dir]
                                subprocess.run(command, check=True, capture_output=True)
                                if os.path.exists(out_path):
                                    with open(out_path, "rb") as f:
                                        converted_files.append((out_filename, f.read()))
                        except Exception as e:
                            st.error(f"❌ {uploaded_file.name} dönüştürülürken hata: {e}")

                    # İndirme Butonları
                    for filename, data in converted_files:
                        st.download_button(f"🎀 {filename} İndir", data, file_name=filename)

    # --- ARAÇ 2: PDF <-> JPG ---
    with tab2:
        st.info("Resimleri PDF yap.")
        img_conv_type = st.selectbox("İşlemi seç:", ["JPG'den PDF'e (jpg/png -> pdf)"])
        up_files_img = st.file_uploader("Resimleri yükle 🌸", type=["jpg", "jpeg", "png"], accept_multiple_files=True,
                                        key="img")

        if up_files_img and st.button("💖 PDF'e Çevir 💖", key="btn_img"):
            with st.spinner("Resimler birleştiriliyor... ✨"):
                results = convert_with_libreoffice(up_files_img, "pdf")
                for filename, data in results:
                    st.download_button(f"🎀 {filename} İndir", data, file_name=filename)

    # --- ARAÇ 3: BİRLEŞTİRİCİ ---
    with tab3:
        st.info("İstediğin sırada PDF'leri birleştir.")
        merge_files = st.file_uploader("Birleştirilecek PDF'leri yükle", type=["pdf"], accept_multiple_files=True,
                                       key="mrg")

        if merge_files and st.button("💖 PDF'leri Birleştir 💖"):
            try:
                merger = PdfMerger()
                for pdf in merge_files:
                    merger.append(pdf)
                output_pdf = BytesIO()
                merger.write(output_pdf)
                merger.close()
                st.success("🎉 Başarıyla birleştirildi!")
                st.download_button("🎀 Birleşik PDF'i İndir", output_pdf.getvalue(), file_name="Diva_Birlesik.pdf",
                                   mime="application/pdf")
            except Exception as e:
                st.error(f"Hata: {e}")

    # --- ARAÇ 4: AYIRICI ---
    with tab4:
        st.info("PDF'i bağımsız sayfalara ayır (ZIP olarak indirilir).")
        split_file = st.file_uploader("Ayrılacak PDF'i yükle", type=["pdf"], key="splt")

        if split_file and st.button("💖 Sayfalara Ayır 💖"):
            try:
                reader = PdfReader(split_file)
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for i in range(len(reader.pages)):
                        writer = PdfWriter()
                        writer.add_page(reader.pages[i])
                        page_buffer = BytesIO()
                        writer.write(page_buffer)
                        zip_file.writestr(f"Sayfa_{i + 1}.pdf", page_buffer.getvalue())
                st.success(f"🎉 {len(reader.pages)} sayfa ayrıldı!")
                st.download_button("🎀 Sayfaları ZIP İndir", zip_buffer.getvalue(), file_name="Diva_Sayfalar.zip",
                                   mime="application/zip")
            except Exception as e:
                st.error(f"Hata: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_kedi_sol, col_kedi_sag = st.columns([1, 1])
    with col_kedi_sag:
        try:
            st.image("_ (1).jpeg", width=180)
        except:
            pass