import os
import tempfile
import subprocess
import platform
import zipfile
import os
import convertapi
from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter
from PIL import Image
from flask import send_from_directory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB Sınırı


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Dosyalar çok büyük! Maksimum 500 MB yükleyebilirsiniz."}), 413


def get_libreoffice_cmd():
    if platform.system() == "Darwin":
        return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    return "libreoffice"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_files():
    if 'files' not in request.files:
        return jsonify({"error": "Dosya bulunamadı"}), 400

    files = request.files.getlist('files')
    action = request.form.get('action')

    if not files or files[0].filename == '':
        return jsonify({"error": "Geçerli bir dosya seçilmedi"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        memory_file = BytesIO()
        output_filename = "Diva_Sonuc.zip"

        try:
            if action == 'merge_pdf':
                merger = PdfMerger()
                for file in files:
                    merger.append(file)
                merger.write(memory_file)
                merger.close()
                output_filename = "Diva_Birlesik.pdf"
                mimetype = "application/pdf"

            elif action == 'split_pdf':
                # Birden fazla PDF yüklendiyse hepsini ayırıp ZIP içine atalım
                with zipfile.ZipFile(memory_file, "w") as zip_file:
                    for file in files:
                        reader = PdfReader(file)
                        base_name = os.path.splitext(secure_filename(file.filename))[0]
                        for i, page in enumerate(reader.pages):
                            writer = PdfWriter()
                            writer.add_page(page)
                            page_buffer = BytesIO()
                            writer.write(page_buffer)
                            zip_file.writestr(f"{base_name}_Sayfa_{i + 1}.pdf", page_buffer.getvalue())
                output_filename = "Diva_Ayrik_Sayfalar.zip"
                mimetype = "application/zip"

            elif action == 'pdf_to_word':
                # Birden fazla PDF yüklendiyse hepsini Word'e çevirip ZIP yapalım
                if len(files) > 1:
                    with zipfile.ZipFile(memory_file, "w") as zip_file:
                        for file in files:
                            input_path = os.path.join(temp_dir, secure_filename(file.filename))
                            file.save(input_path)
                            out_path = input_path.rsplit('.', 1)[0] + ".docx"

                            cv = Converter(input_path)
                            cv.convert(out_path, start=0, end=None)
                            cv.close()

                            with open(out_path, "rb") as f:
                                zip_file.writestr(os.path.basename(out_path), f.read())
                    output_filename = "Diva_Word_Dosyalari.zip"
                    mimetype = "application/zip"
                else:
                    file = files[0]
                    input_path = os.path.join(temp_dir, secure_filename(file.filename))
                    out_path = input_path.rsplit('.', 1)[0] + ".docx"
                    file.save(input_path)

                    cv = Converter(input_path)
                    cv.convert(out_path, start=0, end=None)
                    cv.close()

                    with open(out_path, "rb") as f:
                        memory_file.write(f.read())
                    output_filename = file.filename.rsplit('.', 1)[0] + "_Diva.docx"
                    mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            elif action == 'img_to_pdf':
                images = []
                for file in files:
                    try:
                        img = Image.open(file).convert('RGB')
                        images.append(img)
                    except Exception as img_err:
                        return jsonify({"error": f"Geçersiz resim dosyası: {file.filename} ({str(img_err)})"}), 400

                if images:
                    images[0].save(memory_file, format='PDF', save_all=True, append_images=images[1:])
                output_filename = "Diva_Resimler.pdf"
                mimetype = "application/pdf"


            elif action == 'office_to_pdf':

                # ConvertAPI anahtarını ortam değişkeninden alır

                convertapi.api_secret = os.environ.get('CONVERTAPI_SECRET', 'BURAYA_SECRET_KEY_YAZABILIRSINIZ')

                try:

                    if len(files) > 1:

                        with zipfile.ZipFile(memory_file, "w") as zip_file:

                            for file in files:
                                input_path = os.path.join(temp_dir, secure_filename(file.filename))

                                file.save(input_path)

                                # Cloud API üzerinden dönüştürme

                                result = convertapi.convert('pdf', {'File': input_path})

                                out_path = os.path.join(temp_dir,
                                                        os.path.splitext(secure_filename(file.filename))[0] + ".pdf")

                                result.save_files(out_path)

                                with open(out_path, "rb") as f:
                                    zip_file.writestr(os.path.basename(out_path), f.read())

                        output_filename = "Diva_Office_PDFler.zip"

                        mimetype = "application/zip"

                    else:

                        file = files[0]

                        input_path = os.path.join(temp_dir, secure_filename(file.filename))

                        file.save(input_path)

                        # Cloud API üzerinden dönüştürme

                        result = convertapi.convert('pdf', {'File': input_path})

                        out_path = os.path.join(temp_dir, os.path.splitext(secure_filename(file.filename))[0] + ".pdf")

                        result.save_files(out_path)

                        with open(out_path, "rb") as f:

                            memory_file.write(f.read())

                        output_filename = os.path.splitext(file.filename)[0] + "_Diva.pdf"

                        mimetype = "application/pdf"


                except Exception as api_err:

                    return jsonify({"error": f"API Dönüştürme Hatası: {str(api_err)}"}), 500
@app.route('/<path:filename>')
def serve_sticker(filename):
    if filename.endswith('.png'):
        return send_from_directory('.', filename)
    return "Bulunamadı", 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)