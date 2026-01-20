from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "✅ Filmoloji Cloud Downloader Aktif!"

@app.route('/indir')
def download_video():
    m3u8_url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    
    # Dosya ismini güvenli hale getir ve uzantı ekle
    filename = f"{raw_name}.mp4"

    if not m3u8_url:
        return "URL Yok", 400

    # FFmpeg yolunu bul (Render veya Local)
    ffmpeg_cmd = "./ffmpeg" if os.path.exists("./ffmpeg") else "ffmpeg"

    # --- PROFESYONEL AYARLAR ---
    # -movflags frag_keyframe+empty_moov: Bu komut ÇOK ÖNEMLİ. 
    # Videonun tamamlanmasını beklemeden indirilmeye başlamasını sağlar.
    command = [
        ffmpeg_cmd,
        '-reconnect', '1',
        '-reconnect_streamed', '1',
        '-reconnect_delay_max', '5',
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-headers', 'Referer: https://google.com/\r\n',
        '-i', m3u8_url,
        '-c', 'copy',            # Görüntüyü bozmadan kopyala (Hızlı)
        '-bsf:a', 'aac_adtstoasc',
        '-f', 'mp4',             # Format MP4
        '-movflags', 'frag_keyframe+empty_moov', # <--- SİHİRLİ KOMUT
        'pipe:1'                 # Çıktıyı boru hattına ver
    ]

    # İşlemi başlat
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def generate():
        try:
            while True:
                # 4MB'lık paketler halinde oku (Buffer)
                data = process.stdout.read(4096 * 1024)
                
                if not data:
                    # Veri bittiyse işlemi sonlandır
                    break
                
                yield data
        finally:
            # Bağlantı koparsa FFmpeg'i öldür (Sunucuyu yormasın)
            if process.poll() is None:
                process.terminate()

    # Tarayıcıya "Bu bir dosyadır, indir" diyoruz
    return Response(stream_with_context(generate()), 
                    mimetype="video/mp4",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
