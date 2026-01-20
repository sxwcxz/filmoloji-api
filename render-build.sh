#!/usr/bin/env bash
# Hata olursa durdur
set -o errexit

# Python kütüphanelerini kur
pip install -r requirements.txt

# FFmpeg indir ve kur
if [ ! -f ./ffmpeg ]; then
    echo "FFmpeg indiriliyor..."
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xvf ffmpeg-release-amd64-static.tar.xz
    mv ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
    rm -rf ffmpeg-*-amd64-static*
    echo "FFmpeg kuruldu!"
fi