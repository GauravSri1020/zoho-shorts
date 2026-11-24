#!/bin/bash
# qa.sh <file.mp4> -> prints duration, black/freeze/silence events, loudness; makes /tmp/cs_<name>.png
f=$1; n=$(basename $f .mp4)
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
echo "== $n dur=$d"
ffmpeg -v info -i $f -vf "blackdetect=d=0.1:pix_th=0.08,freezedetect=n=0.003:d=1.5" -af "silencedetect=n=-45dB:d=1.2,ebur128" -f null - 2>&1 | grep -E "black_start|freeze_start|silence_start|^\s+I:" | head -20
ffmpeg -v error -y -i $f -vf "fps=1/2.2,scale=216:-1,tile=8x3" -frames:v 1 /tmp/cs_$n.png
