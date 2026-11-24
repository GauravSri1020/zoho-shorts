import cv2, sys, glob, numpy as np
casc = cv2.CascadeClassifier(glob.glob('/tmp/cvx/**/haarcascade_frontalface_default.xml', recursive=True)[0])
idx=int(sys.argv[1]); out=sys.argv[2]; tiles=[]
for p in sys.argv[3:]:
    cap=cv2.VideoCapture(p); cap.set(1,idx); ok,f=cap.read()
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY); fs=casc.detectMultiScale(g,1.12,5,minSize=(90,90))
    x,y,w,h=max(fs,key=lambda r:r[2]*r[3]) if len(fs) else (200,300,300,300)
    cr=f[y+int(h*0.05):y+int(h*0.55), x+int(w*0.15):x+int(w*0.85)]; t=cv2.resize(cr,(240,170))
    cv2.putText(t,p.split('/')[-1][:6],(4,18),0,0.55,(0,255,255),2); tiles.append(t)
while len(tiles)%6: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out,np.vstack([np.hstack(tiles[i:i+6]) for i in range(0,len(tiles),6)]))
