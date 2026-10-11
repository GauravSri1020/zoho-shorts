"""Runs ON KAGGLE (free GPU). Pushed by autopilot/kaggle_gpu.py - do not run on GitHub.

Input  (private Kaggle dataset): base.mp4 (a talking clip of the presenter), audio.wav (the Short's AI voice),
                                 run.txt (id of the GitHub run, echoed back so stale outputs are never used)
Output (/kaggle/working):        result.mp4 (base clip, looped to the voice length, lips re-synced to the voice
                                 with LatentSync 1.5), run.txt, log.txt
"""
import glob
import os
import shutil
import subprocess
import time

WORK = "/kaggle/working"
LS_DIR = "/kaggle/temp_ls"                       # outside /kaggle/working so it is not downloaded back
LS_COMMIT = "a229c3948406bc2cf6eaf4873e662e70c6a04746"
LOG = open(os.path.join(WORK, "log.txt"), "w")


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def sh(cmd, cwd=None, check=True):
    log(f"$ {cmd}")
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    LOG.write(out[-6000:] + "\n")
    LOG.flush()
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {cmd}\n{out[-3000:]}")
    return out


def find_input(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    if not hits:
        raise RuntimeError(f"{name} not found under /kaggle/input")
    return hits[0]


def main():
    base, audio, run = find_input("base.mp4"), find_input("audio.wav"), find_input("run.txt")
    shutil.copy(run, os.path.join(WORK, "run.txt"))
    log(f"run {open(run).read().strip()} | base {base} | audio {audio}")
    sh("nvidia-smi --query-gpu=name,memory.total --format=csv", check=False)
    sh(f"python -c 'import sys, torch; print(sys.version, torch.__version__, torch.cuda.is_available())'", check=False)

    # 1. code (pinned commit)
    if not os.path.isdir(LS_DIR):
        os.makedirs(LS_DIR)
        sh("git init -q && git remote add origin https://github.com/bytedance/LatentSync.git && "
           f"git fetch -q --depth 1 origin {LS_COMMIT} && git checkout -q FETCH_HEAD", cwd=LS_DIR)
    # T4 (compute 7.5) runs float16 fine; upstream only enables it for > 7.x
    sh("sed -i 's/get_device_capability()\\[0\\] > 7/get_device_capability()[0] >= 7/' scripts/inference.py",
       cwd=LS_DIR)

    # 2. python packages (Kaggle already has torch / torchvision / opencv / librosa / numpy)
    sh("pip install -q diffusers==0.32.2 einops omegaconf python_speech_features kornia DeepCache==0.1.1 "
       "imageio imageio-ffmpeg ffmpeg-python soundfile transformers==4.48.3 huggingface_hub==0.27.1 accelerate", check=True)
    try:
        sh("pip install -q decord==0.6.0")
        sh("python -c 'import decord'")
    except RuntimeError:
        sh("pip install -q eva-decord")           # decord wheels for newer Python versions
    sh("pip install -q onnxruntime-gpu", check=False)
    sh("pip install -q insightface==0.7.3")

    # 3. weights (LatentSync 1.5 = 256 px, needs ~8 GB VRAM -> fits a T4)
    sh("python -c \"from huggingface_hub import hf_hub_download as d; "
       "d('ByteDance/LatentSync-1.5', 'latentsync_unet.pt', local_dir='checkpoints'); "
       "d('ByteDance/LatentSync-1.5', 'whisper/tiny.pt', local_dir='checkpoints')\"", cwd=LS_DIR)

    # 4. lip-sync
    out = os.path.join(WORK, "result.mp4")
    t0 = time.time()
    sh(f"python -m scripts.inference --unet_config_path configs/unet/stage2.yaml "
       f"--inference_ckpt_path checkpoints/latentsync_unet.pt --inference_steps 20 --guidance_scale 1.5 "
       f"--enable_deepcache --video_path {base} --audio_path {audio} --video_out_path {out} "
       f"--temp_dir {LS_DIR}/tmp", cwd=LS_DIR)
    if not os.path.exists(out) or os.path.getsize(out) < 10000:
        raise RuntimeError("LatentSync produced no video")
    log(f"done in {time.time() - t0:.0f}s -> {out} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    try:
        main()
        open(os.path.join(WORK, "status.txt"), "w").write("ok\n")
    except Exception as e:
        log(f"FAILED: {e}")
        open(os.path.join(WORK, "status.txt"), "w").write(f"error: {str(e)[:2000]}\n")
        # exit 0 on purpose: Kaggle keeps the outputs (status.txt, log.txt) and GitHub reads the reason
    finally:
        LOG.close()
