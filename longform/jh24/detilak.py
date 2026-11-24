"""detilak.py in.mp4 out.mp4 -- removes a red mark (tilak) between the brows.
Per frame: face box (Haar, smoothed). In a soft ellipse over the glabella/forehead centre, any pixel whose
red chroma (Cr) is above the surrounding skin is given the skin's chroma and smoothed brightness."""
import cv2, sys, glob, subprocess, numpy as np
casc = cv2.CascadeClassifier(glob.glob('/tmp/cvx/**/haarcascade_frontalface_default.xml', recursive=True)[0])
src, dst = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(3)); H = int(cap.get(4))
p = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-',
     '-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
box=None; n=0; touched=0
while True:
    ok,f = cap.read()
    if not ok: break
    n+=1
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    fs = casc.detectMultiScale(g, 1.1, 5, minSize=(int(W*0.12),)*2)
    if len(fs):
        b = np.array(max(fs, key=lambda r:r[2]*r[3]), float)
        if box is None or abs(b[1]-box[1]) < box[3]*0.5: box = b if box is None else box*0.5 + b*0.5
    if box is not None:
        x,y,w,h = box
        cx, cy = x+w*0.5, y+h*0.26
        import os; ax, ay = w*0.13, h*float(os.environ.get("AY","0.20"))
        X0,X1 = int(max(0,cx-ax*2)), int(min(W,cx+ax*2)); Y0,Y1 = int(max(0,cy-ay*2)), int(min(H,cy+ay*2))
        roi = f[Y0:Y1, X0:X1]
        yy,xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
        d = ((xx-cx)/ax)**2 + ((yy-cy)/ay)**2
        inner = np.clip((1.3-d)/0.6, 0, 1)           # soft ellipse
        ring = (d>1.4)&(d<3.2)
        ycc = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        Y,Cr,Cb = ycc[...,0],ycc[...,1],ycc[...,2]
        okr = ring & (Y > np.median(Y[ring])*0.75)
        if okr.sum() > 30:
            cr0, cb0 = np.median(Cr[okr]), np.median(Cb[okr])
            ex = np.clip((Cr-cr0-3)/7.0, 0, 1)
            m = cv2.GaussianBlur(ex*inner, (0,0), 1.5)
            m = np.clip(m*1.5, 0, 1)
            if m.max() > 0.1:
                touched += 1
                Yb = cv2.GaussianBlur(Y, (0,0), 5)
                Ys = Y*(1-0.85*m) + np.maximum(Y,Yb)*(0.85*m)
                out = np.stack([Ys, Cr*(1-m)+cr0*m, Cb*(1-m)+cb0*m], -1)
                f[Y0:Y1, X0:X1] = cv2.cvtColor(np.clip(out,0,255).astype(np.uint8), cv2.COLOR_YCrCb2BGR)
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
print(f"{src.split('/')[-1]} frames={n} touched={touched}")
