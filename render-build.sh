#!/usr/bin/env bash
# Hata olursa durdur (En güvenli yöntem)
set -e

# Python kütüphanelerini kur
pip install -r requirements.txt

# FFmpeg kontrolü ve kurulumu
if [ ! -f ./ffmpeg ]; then
    echo "FFmpeg indiriliyor..."
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xvf ffmpeg-release-amd64-static.tar.xz
    mv ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
    
    # İZİN VERMEK ÇOK ÖNEMLİ
    chmod +x ./ffmpeg
    
    # Temizlik yap
    rm -rf ffmpeg-*-amd64-static*
    echo "FFmpeg kuruldu ve hazir!"
fi
