import json, sys, subprocess
from playwright.sync_api import sync_playwright
D=json.load(open('data.json')); FPS=30
mode=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.add_init_script(f"window.DATA={json.dumps(D)};")
    pg.goto("file:///home/claude/trend/page.html"); pg.wait_for_timeout(600)
    if mode=="test":
        for t in map(float,sys.argv[2:]):
            pg.evaluate(f"render({t})"); pg.screenshot(path=f"test_{t:05.2f}.jpg",type="jpeg",quality=80)
    else:
        n=int(D['dur']*FPS)
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
            "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","video_noaudio.mp4"],stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i/FPS})"); ff.stdin.write(pg.screenshot(type="jpeg",quality=92))
            if i%150==0: print(i,n,flush=True)
        ff.stdin.close(); ff.wait()
    b.close()
