import json, re
T=json.load(open('timing.json'))
words=[]
def weight(w):
    core=re.sub(r'[^\w$%.]','',w)
    if re.search(r'\d',core):
        return {'$2.7':11,'2008':10,'23%':11,'12%':9,'$115.8':22,'103%':16}.get(core.rstrip('.'),10)
    return max(2,len(core))+1.2
for ln in T['lines']:
    toks=ln['cap'].split()
    ws=[weight(t) for t in toks]; tot=sum(ws); t=ln['start']; d=ln['end']-ln['start']
    for tok,w in zip(toks,ws):
        dd=d*w/tot; words.append({'w':tok,'t0':round(t,3),'t1':round(t+dd,3),'line':ln['i']}); t+=dd
def at(line,sub):
    for w in words:
        if w['line']==line and sub.lower() in w['w'].lower(): return w['t0']
    raise KeyError(sub)
hits={'gone':at(0,'October')+0.25,'w23':at(1,'23%'),'trigger':at(2,'Reuters'),'fell':at(2,'fell'),'d12':at(2,'12%'),
      'rev':at(3,'$115.8'),'p103':at(3,'103%'),'sales':at(4,'sales'),'crash':at(4,'crash'),'neq':at(5,'charge'),
      'nobody':at(5,'Nobody'),'follow':at(6,'Follow')}
lines=[{'i':l['i'],'s':l['start'],'e':l['end']} for l in T['lines']]
json.dump({'dur':T['dur'],'words':words,'hits':hits,'lines':lines},open('data.json','w'),indent=0)
print(hits)
