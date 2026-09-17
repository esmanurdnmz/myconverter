import streamlit as st
import subprocess
import os
import tempfile

# Sayfa ayarları
st.set_page_config(page_title="Sınırsız PDF Çevirici", page_icon="📄")

st.title("Sınırsız PPTX - PDF Dönüştürücü 🔄")
st.markdown("Herhangi bir kota, sınır veya reklam olmadan sunumlarınızı PDF'e çevirin.")

# Dosya yükleme alanı
uploaded_file = st.file_uploader("PPTX dosyanızı sürükleyip bırakın", type=["pptx"])

if uploaded_file is not None:
    if st.button("PDF'e Çevir"):
        with st.spinner("Arka planda dönüştürülüyor, lütfen bekleyin..."):
            # Çakışmaları önlemek için geçici bir klasör açıyoruz
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = os.path.join(temp_dir, uploaded_file.name)

                # Yüklenen PPTX dosyasını bu klasöre kaydediyoruz
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # LibreOffice'e çeviri emri veren terminal komutu
                command = [
                    "libreoffice", "--headless", "--convert-to", "pdf",
                    input_path, "--outdir", temp_dir
                ]

                try:
                    # Komutu çalıştır
                    subprocess.run(command, check=True, capture_output=True)

                    # Oluşacak PDF dosyasının adını tahmin et/belirle
                    pdf_filename = uploaded_file.name.rsplit('.', 1)[0] + ".pdf"
                    pdf_path = os.path.join(temp_dir, pdf_filename)

                    # Dosya başarıyla oluştuysa ekrana indirme butonu bas
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            st.success("🎉 Dönüştürme işlemi başarıyla tamamlandı!")
                            st.download_button(
                                label="📥 PDF'i İndir",
                                data=pdf_file,
                                file_name=pdf_filename,
                                mime="application/pdf"
                            )
                    else:
                        st.error("Dönüştürme tamamlanamadı, dosya oluşturulamadı.")
                except Exception as e:
                    st.error(f"Sistemsel bir hata oluştu: {e}")