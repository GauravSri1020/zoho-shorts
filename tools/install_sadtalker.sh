#!/usr/bin/env bash
# Installs SadTalker (open-source lip-sync, Apache-2.0) on the GitHub runner, CPU only.
# Cached by the workflow, so the slow part happens only on the first run.
set -euo pipefail
D="${SADTALKER_DIR:-$HOME/sadtalker}"
if [ -f "$D/.ok" ]; then echo "SadTalker already installed"; exit 0; fi
rm -rf "$D"
git clone --depth 1 https://github.com/OpenTalker/SadTalker "$D"
python3.10 -m venv "$D/venv"
P="$D/venv/bin/pip"
$P install -q --upgrade pip
$P install -q torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu
grep -v -i -E "^(gradio|torch|torchvision|torchaudio)" "$D/requirements.txt" > "$D/req-cpu.txt"
$P install -q -r "$D/req-cpu.txt"
(cd "$D" && bash scripts/download_models.sh)
touch "$D/.ok"
echo "SadTalker installed in $D"
