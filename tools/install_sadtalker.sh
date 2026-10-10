#!/usr/bin/env bash
# Installs SadTalker (open-source lip-sync, Apache-2.0) on the GitHub runner, CPU only.
# Cached by the workflow, so the slow part happens only on the first run.
# Fix (Oct 2026): basicsr/facexlib/gfpgan need torch while building -> install them with
# --no-build-isolation AFTER torch, numpy and cython are in the venv (that was the "basicsr" error).
set -euo pipefail
D="${SADTALKER_DIR:-$HOME/sadtalker}"
if [ -f "$D/.ok" ]; then echo "SadTalker already installed"; exit 0; fi
rm -rf "$D"
git clone --depth 1 https://github.com/OpenTalker/SadTalker "$D"
python3.10 -m venv "$D/venv"
PY="$D/venv/bin/python"
P="$PY -m pip install -q --no-cache-dir"
$P --upgrade pip "setuptools<70" wheel
$P torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu
$P "numpy==1.23.5" cython
$P --no-build-isolation basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8
grep -v -i -E "^(gradio|torch|torchvision|torchaudio|numpy|basicsr|facexlib|gfpgan)" "$D/requirements.txt" > "$D/req-cpu.txt"
$P --no-build-isolation -r "$D/req-cpu.txt" "numpy==1.23.5"
$PY -c "import basicsr, facexlib, gfpgan, face_alignment, kornia, librosa; print('imports ok')"
(cd "$D" && bash scripts/download_models.sh)
ls "$D/checkpoints" | head
touch "$D/.ok"
echo "SadTalker installed in $D"
