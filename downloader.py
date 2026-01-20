from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Ana sayfa testi (Sunucu çalışıyor mu diye bakmak için)
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

    # FFmpeg yolunu bul
    if os.path.exists("./ffmpeg"):
        ffmpeg_cmd = "./ffmpeg"
    else:
        ffmpeg_cmd = "ffmpeg"

    # FFmpeg Komutu (User-Agent eklendi, böylece siteler bizi engellemez)
    command = [
        ffmpeg_cmd,
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', # Tarayıcı taklidi
        '-i', m3u8_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        'pipe:1'
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def generate():
        try:
            while True:
                data = process.stdout.read(1024 * 1024) 
                if not data:
                    break
                yield data
        finally:
            process.terminate()

    return Response(stream_with_context(generate()), 
                    mimetype="video/mp4",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__ == '__main__':
    app.run(debug=True)
