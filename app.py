import os
import tempfile
import platform
import zipfile
import warnings
from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter
from PIL import Image
import convertapi

# Uyarı mesajlarını gizle
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB Sınırı


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Dosyalar çok büyük! Maksimum 500 MB yükleyebilirsiniz."}), 413


@app.route('/<path:filename>')
def serve_sticker(filename):
    if filename.endswith('.png'):
        return send_from_directory('.', filename)
    return "Bulunamadı", 404


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
                if len(files) > 1:
                    with zipfile.ZipFile(memory_file, "w") as zip_file:
                        for file in files:
                            in_pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
                            file.save(in_pdf_path)
                            out_docx_path = os.path.splitext(in_pdf_path)[0] + ".docx"

                            cv = Converter(in_pdf_path)
                            cv.convert(out_docx_path, start=0, end=None)
                            cv.close()

                            with open(out_docx_path, "rb") as f:
                                zip_file.writestr(os.path.basename(out_docx_path), f.read())
                    output_filename = "Diva_Word_Dosyalari.zip"
                    mimetype = "application/zip"
                else:
                    file = files[0]
                    in_pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(in_pdf_path)
                    out_docx_path = os.path.splitext(in_pdf_path)[0] + ".docx"

                    cv = Converter(in_pdf_path)
                    cv.convert(out_docx_path, start=0, end=None)
                    cv.close()

                    with open(out_docx_path, "rb") as f:
                        memory_file.write(f.read())
                    output_filename = os.path.splitext(secure_filename(file.filename))[0] + "_Diva.docx"
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
                api_secret = os.environ.get('CONVERTAPI_SECRET')
                if not api_secret:
                    return jsonify({
                                       "error": "ConvertAPI Secret Key sunucuda tanımlanmamış! Lütfen Render Environment ayarlarını kontrol edin."}), 500

                convertapi.api_secret = api_secret

                if len(files) > 1:
                    with zipfile.ZipFile(memory_file, "w") as zip_file:
                        for file in files:
                            in_office_path = os.path.join(temp_dir, secure_filename(file.filename))
                            file.save(in_office_path)

                            result = convertapi.convert('pdf', {'File': in_office_path})
                            out_pdf_path = os.path.join(temp_dir,
                                                        os.path.splitext(secure_filename(file.filename))[0] + ".pdf")
                            result.save_files(out_pdf_path)

                            with open(out_pdf_path, "rb") as f:
                                zip_file.writestr(os.path.basename(out_pdf_path), f.read())
                    output_filename = "Diva_Office_PDFler.zip"
                    mimetype = "application/zip"
                else:
                    file = files[0]
                    in_office_path = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(in_office_path)

                    result = convertapi.convert('pdf', {'File': in_office_path})
                    out_pdf_path = os.path.join(temp_dir, os.path.splitext(secure_filename(file.filename))[0] + ".pdf")
                    result.save_files(out_pdf_path)

                    with open(out_pdf_path, "rb") as f:
                        memory_file.write(f.read())
                    output_filename = os.path.splitext(secure_filename(file.filename))[0] + "_Diva.pdf"
                    mimetype = "application/pdf"

            else:
                return jsonify({"error": "Bilinmeyen işlem"}), 400

            memory_file.seek(0)
            return send_file(memory_file, download_name=output_filename, as_attachment=True, mimetype=mimetype)

        except Exception as e:
            return jsonify({"error": f"İşlem hatası: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)