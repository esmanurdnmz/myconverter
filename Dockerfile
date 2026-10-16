# Resmi Python imajını temel alıyoruz
FROM python:3.11-slim

# Sistem paketlerini güncelliyor ve LibreOffice'i kuruyoruz
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gereksinimleri kopyalayıp yüklüyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarının tamamını kopyalıyoruz
COPY . .

# Flask'ın çalışacağı portu belirtiyoruz
EXPOSE 5000

# Uygulamayı başlatıyoruz
CMD ["python", "app.py"]