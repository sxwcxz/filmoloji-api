from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "✅ Filmoloji Sunucusu Aktif! v3.0 (Loglu Versiyon)"

@app.route('/indir')
def download_video():
    m3u8_url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    filename = f"{raw_name}.mp4"

    if not m3u8_url:
        return "URL Yok", 400

    # FFmpeg yolu
    ffmpeg_cmd = "./ffmpeg" if os.path.exists("./ffmpeg") else "ffmpeg"

    print(f"--- İNDİRME BAŞLIYOR: {filename} ---", file=sys.stderr)
    print(f"Kaynak URL: {m3u8_url}", file=sys.stderr)

    # Güçlendirilmiş FFmpeg Komutu
    command = [
        ffmpeg_cmd,
        '-reconnect', '1',             # Bağlantı koparsa tekrar dene
        '-reconnect_at_eof', '1',      # Bitince tekrar dene (garanti olsun)
        '-reconnect_streamed', '1',    # Akış koparsa tekrar dene
        '-reconnect_delay_max', '2',   # Bekleme süresi
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        '-headers', f'Referer: https://www.google.com/\r\n', # Bazı siteler Referer ister
        '-i', m3u8_url,
        '-c', 'copy',                  # Görüntüyü bozmadan kopyala (HIZLI)
        '-bsf:a', 'aac_adtstoasc',     # Ses düzeltmesi
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov', # Stream için gerekli
        'pipe:1'
    ]

    # Hata çıktılarını da (stderr) yakalıyoruz
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def generate():
        try:
            # İşlem başladığı an
            while True:
                # Videoyu parça parça oku
                data = process.stdout.read(1024 * 1024) # 1MB chunk
                
                # Eğer veri gelmiyorsa ve işlem bittiyse döngüden çık
                if not data:
                    # Hata var mı kontrol et
                    if process.poll() is not None:
                        break
                    continue
                
                yield data
        except Exception as e:
            print(f"HATA OLUŞTU: {str(e)}", file=sys.stderr)
        finally:
            # İşlem bittiğinde hataları loga yaz (0 byte inme sebebini görmek için)
            stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
            if stderr_output:
                print(f"FFMPEG LOG (SON 500 Karakter):\n...{stderr_output[-500:]}", file=sys.stderr)
            process.terminate()

    return Response(stream_with_context(generate()), 
                    mimetype="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__ == '__main__':
    app.run(debug=True)
