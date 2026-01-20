import os
import subprocess
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# İndirilenlerin kaydedileceği klasör
DOWNLOAD_FOLDER = "Indirilenler"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def indir_arkaplanda(url, filename):
    print(f"--> İNDİRME BAŞLATILIYOR: {filename}")
    
    # Dosya yolu
    output_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    # FFmpeg Komutu (Direkt dosyaya kaydet)
    command = [
        "ffmpeg", 
        '-y', # Varsa üzerine yaz
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        '-i', url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        output_path
    ]

    # İşlemi başlat ve bitene kadar bekle
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ İNDİRME TAMAMLANDI: {output_path}")
        # İndirme bitince klasörü aç (Opsiyonel - Windows için)
        os.startfile(os.path.abspath(DOWNLOAD_FOLDER))
    else:
        print(f"❌ HATA OLUŞTU:\n{result.stderr}")

@app.route('/indir')
def download_request():
    m3u8_url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    filename = f"{raw_name}.mp4"

    if not m3u8_url:
        return jsonify({"durum": "hata", "mesaj": "Link yok"}), 400

    # İndirmeyi ayrı bir "Thread" (iş parçacığı) olarak başlat
    # Böylece sunucu donmaz, arayüze hemen cevap döner.
    thread = threading.Thread(target=indir_arkaplanda, args=(m3u8_url, filename))
    thread.start()

    return jsonify({
        "durum": "basladi", 
        "mesaj": f"İndirme arka planda başlatıldı! '{DOWNLOAD_FOLDER}' klasörüne bak.",
        "dosya_adi": filename
    })

if __name__ == '__main__':
    print(f"Sistem Hazır! Dosyalar '{DOWNLOAD_FOLDER}' klasörüne inecek.")
    app.run(port=5000)
