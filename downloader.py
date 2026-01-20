import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Masaüstünde "Filmoloji_Indirilenler" klasörü oluşturur
DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
DOWNLOAD_FOLDER = os.path.join(DESKTOP, "Filmoloji_Indirilenler")

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def dosya_ismini_temizle(isim):
    # Dosya ismindeki yasaklı karakterleri temizler (: / \ * vb.)
    return re.sub(r'[\\/*?:"<>|]', "", isim)

@app.route('/indir')
def start_download():
    url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    
    if not url: return jsonify({"status": "error", "message": "Link yok"}), 400

    clean_name = dosya_ismini_temizle(raw_name)
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{clean_name}.mp4")

    # Eğer ffmpeg.exe yanındaysa onu kullan, yoksa sistemdekini
    ffmpeg_exe = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"

    # --- SİHİRLİ KISIM ---
    # Bu komut yeni bir siyah pencere açar (CREATE_NEW_CONSOLE).
    # Kullanıcı indirmeyi orada "parça parça" izler.
    # Bitince pencere kapanır.
    
    cmd = f'title Filmoloji: {clean_name} && echo İNDİRİLİYOR: {clean_name} && echo Lütfen pencereyi kapatmayin... && "{ffmpeg_exe}" -y -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" -i "{url}" -c copy -bsf:a aac_adtstoasc "{file_path}" && echo. && echo BITTI! Klasor aciliyor... && explorer "{DOWNLOAD_FOLDER}"'

    # Windows'ta yeni pencere açmak için:
    subprocess.Popen(f'start cmd /c "{cmd}"', shell=True)

    return jsonify({
        "status": "success", 
        "message": "İndirme penceresi açıldı! Parçalar birleştiriliyor...",
        "path": file_path
    })

if __name__ == '__main__':
    print(f"Server Aktif! Dosyalar şuraya inecek: {DOWNLOAD_FOLDER}")
    app.run(port=5000)
