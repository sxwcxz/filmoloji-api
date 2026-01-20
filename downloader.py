from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app) # Tüm sitelerden erişime izin ver

@app.route('/indir')
def download_video():
    m3u8_url = request.args.get('url')
    raw_name = request.args.get('name', 'film')
    filename = f"{raw_name}.mp4"

    if not m3u8_url:
        return "URL Yok", 400

    # FFmpeg nerede? (Bizim script indirdi mi yoksa sistemde var mı?)
    if os.path.exists("./ffmpeg"):
        ffmpeg_cmd = "./ffmpeg"
    else:
        ffmpeg_cmd = "ffmpeg"

    command = [
        ffmpeg_cmd,
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