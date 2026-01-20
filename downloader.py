from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app) # Tüm sitelerden erişime izin ver

# Ana sayfa kontrolü (Sunucu yaşıyor mu?)
@app.route('/')
def home():
    return "✅ Filmoloji İndirme Sunucusu AKTİF! (Kullanmak için /indir yolunu kullanın)"

@app.route('/indir')
def download_video():
    m3u8_url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    filename = f"{raw_name}.mp4"

    if not m3u8_url:
        return "❌ Hata: Link (URL) gönderilmedi.", 400

    # FFmpeg yolunu belirle (Render'da mı yoksa Localde mi?)
    if os.path.exists("./ffmpeg"):
        ffmpeg_cmd = "./ffmpeg"
    else:
        ffmpeg_cmd = "ffmpeg"

    # FFmpeg Komutu
    # -user_agent: Sitelerin bizi bot sanıp engellememesi için.
    # -c copy: Görüntüyü bozmadan (re-encode yapmadan) kopyalar. Hızlıdır.
    command = [
        ffmpeg_cmd,
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-i', m3u8_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        'pipe:1'
    ]

    # İşlemi başlat
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def generate():
        try:
            while True:
                data = process.stdout.read(1024 * 1024) # 1MB'lık parçalar
                if not data:
                    break
                yield data
        finally:
            process.terminate()

    # mimetype="application/octet-stream" sayesinde tarayıcı bunu
    # video olarak oynatmaz, DOSYA OLARAK indirir.
    return Response(stream_with_context(generate()), 
                    mimetype="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__ == '__main__':
    app.run(debug=True)
