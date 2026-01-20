#!/usr/bin/env bash
set -o errexit

# Python kütüphanelerini kur
pip install -r requirements.txt

# FFmpeg indir, kur ve İZİN VER
if [ ! -f ./ffmpeg ]; then
    echo "FFmpeg indiriliyor..."
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xvf ffmpeg-release-amd64-static.tar.xz
    mv ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
    chmod +x ./ffmpeg  # <-- EN ÖNEMLİ KISIM BURASI (Çalıştırma izni)
    rm -rf ffmpeg-*-amd64-static*
    echo "FFmpeg kuruldu ve izin verildi!"
fi
