import json
d={s['id']:s for s in json.load(open('jh.json'))}
SRC="Sources: NVIDIA filings · AP · NPR · CNBC · FT · Reuters · not financial advice"
AC=[("#ffd23f","#5b5bff"),("#ff6b6b","#4f46e5"),("#4ade80","#0ea5e9"),("#f472b6","#6366f1"),("#38bdf8","#a855f7"),
    ("#fb923c","#2563eb"),("#facc15","#db2777"),("#34d399","#7c3aed"),("#f87171","#0891b2"),("#a3e635","#9333ea")]
S={
"jh01-reasons":dict(hook="<small>JENSEN HUANG</small>HE'S BACK. <em>WHY?</em>",cta="RIGHT CALL? COMMENT 👇",cta_from=(2,"Comment"),
  scene=dict(clip=0,frm="Here",to=(2,"Was"),head="WHY HE <em>CAME BACK</em>",sub="5 reasons · our read",q="Why did Nvidia bring back Jensen Huang?",mode="steps",
   items=[["🛡️","Board: US gov input, 'no security risk'"],["📉","Stock had lost almost half its value"],["🪑","No successor was ready"],["🗳️","3 directors reportedly backed him"],["📣","Investors, petition, White House"]],
   note="Our analysis, based on reports",stickers=["📉","🏛️","🤝","🗳️"]),hl=["board","founder","yes","no","stock","successor","directors","five"]),
"jh02-spy":dict(hook="<small>JENSEN HUANG</small>THE <em>'SPY'</em> STORY",cta="FOLLOW FOR UPDATES ➜",cta_from=(2,"That"),
  scene=dict(clip=0,frm="Here",to=(2,"That"),head="THE <em>'SPY'</em> STORY",sub="what is actually confirmed",q="Was there really a spy in the Jensen Huang story?",mode="steps",
   items=[["⚖️","DOJ: 'no conclusions reached' on her"],["🕵️","US intelligence reportedly divided"],["🇨🇳","Beijing denies she was a spy"],["📦","Real case: Megaspeed export probe"],["⏳","Still open. Nothing proven."]],
   note="Sources: Reuters, AP, CNN",stickers=["🕵️","⚖️","📦","❓"]),hl=["spy","justice","conclusion","divided","exports","singapore","open"]),
"jh03-stock":dict(hook="<small>JENSEN HUANG</small>WAS IT JUST <em>THE STOCK?</em>",cta="PROBES STILL OPEN ⚠️",cta_from=(2,"but"),
  scene=dict(clip=0,frm="Let's",to=(2,"but"),head="THE <em>STOCK</em> STORY",sub="NVDA in 4 numbers",q="Did Nvidia bring back Jensen Huang to save the stock?",mode="numbers",
   items=[["$239","record close · 6 Oct"],["~$125","close before his return"],["+31.5%","the day he returned"],["$165","close · 23 Nov"]],
   note="Board: 'best interests of our stockholders'",stickers=["📈","💰","📉","🤔"]),hl=["stock","half","thirty","percent","shareholders","investigations"]),
"jh04-investors":dict(hook="<small>JENSEN HUANG</small>DID INVESTORS <em>FORCE IT?</em>",cta="WHO REALLY DECIDED? 👇",cta_from=(2,"only"),
  scene=dict(clip=0,frm="Not",to=(2,"only"),head="THE <em>PRESSURE</em>",sub="who pushed for his return",q="Did investors force Nvidia to bring back Jensen Huang?",mode="steps",
   items=[["📝","Petition: 'Stand with Jensen'"],["🏦","2 funds: keep 'all options on the table'"],["🗣️","Bill Ackman: board 'panicked'"],["🔑","He never had a controlling stake"],["🗳️","Only the board could decide"]],
   note="Sources: FT, CNBC, Fox Business",stickers=["🏦","📝","🗣️","🔑"]),hl=["investors","force","pressure","funds","billionaire","panicked","board","stake"]),
"jh05-why-not-leave":dict(hook="<small>JENSEN HUANG</small>WHY NOT <em>A NEW JOB?</em>",cta="WOULD YOU GO BACK? 👇",cta_from=(2,"Our"),
  scene=dict(clip=0,frm="His",to=(2,"Our"),head="WHY HE <em>STAYED</em>",sub="his moves, day by day",q="Why didn't Jensen Huang join another company?",mode="timeline",
   items=[["12 Nov","Resigns as CEO"],["15 Nov","FT: discussed comeback with confidants"],["17 Nov","Posts: 'honoured' to return"],["23 Nov","Back as CEO"]],
   note="Our guess: Nvidia is his life's work",stickers=["🏠","❤️","📅","🔁"]),hl=["founder","five","days","comeback","thirty","years","guess"]),
"jh06-own-words":dict(hook="<small>JENSEN HUANG</small>IN HIS <em>OWN WORDS</em>",cta="6 DAYS LATER: BACK ✅",cta_from=(2,"Six"),
  scene=dict(clip=0,frm="Three",to=(2,"Six"),head="HIS <em>OWN WORDS</em>",sub="11 days away",q="What did Jensen Huang say while he was out?",mode="steps",
   items=[["💬","'Serious mistakes in my personal life'"],["🤝","Will cooperate with the investigation"],["🏛️","Agreed to answer Congress"],["🙏","'Honoured' to return if asked"]],
   note="Sources: his statements via NPR, AP",stickers=["💬","🙏","🏛️","✍️"]),hl=["founder","mistakes","cooperate","honoured","eleven","six"]),
"jh07-washington":dict(hook="<small>JENSEN HUANG</small>WASHINGTON'S <em>ROLE</em>",cta="FOLLOW FOR MORE ➜",cta_from=(2,"One"),
  scene=dict(clip=0,frm="Much",to=(2,"One"),head="WASHINGTON'S <em>ROLE</em>",sub="what was said, by whom",q="What role did Washington play in Jensen Huang's return?",mode="steps",
   items=[["🏛️","Board: input from 'senior levels' of US gov"],["🤝","Trump to CNBC: 'I made the deal'"],["🗣️","VP Vance reportedly lobbied directors"],["💼","Treasury Sec. Bessent wanted an outsider"]],
   note="Sources: NVIDIA filing, CNBC, AP, SCMP",stickers=["🏛️","🤝","🇺🇸","💼"]),hl=["washington","government","white","house","deal","outsider"]),
"jh08-what-changes":dict(hook="<small>JENSEN HUANG</small>WHAT <em>CHANGES</em> NOW",cta="FOLLOW FOR WHAT'S NEXT ➜",cta_from=(2,"Follow"),
  scene=dict(clip=0,frm="but",to=(2,"Follow"),head="WHAT <em>CHANGES</em>",sub="Nvidia after the U-turn",q="What changes at Nvidia with Jensen Huang back?",mode="steps",
   items=[["🛡️","New national security + export committee"],["🪑","Harvey Jones: first-ever board chair"],["💼","Colette Kress: back to CFO"],["📅","1 Dec: Congress interview"]],
   note="Sources: NVIDIA filings, Anadolu, AP",stickers=["🛡️","🪑","💼","📅"]),hl=["founder","security","committee","chair","finance","december","congress"]),
"jh09-congress":dict(hook="<small>JENSEN HUANG</small>VS <em>CONGRESS</em>",cta="FAR FROM OVER 👀",cta_from=(2,"This"),
  scene=dict(clip=0,frm="Here's",to=(2,"This"),head="THE <em>HEARINGS</em>",sub="what Congress wants to know",q="Why is Jensen Huang facing Congress on Dec 1?",mode="timeline",
   items=[["1 Dec","Huang: closed-door, 3 House committees"],["2 Dec","General counsel Tim Teter"],["Focus","'Potential breach of national security'"],["Ongoing","DOJ Megaspeed export probe"]],
   note="Sources: AP, Digital Trends, PBS",stickers=["🏛️","🎙️","📜","⚖️"]),hl=["december","three","house","committees","national","security","exports","lawyer"]),
"jh10-numbers":dict(hook="<small>JENSEN HUANG</small>THE STORY IN <em>5 NUMBERS</em>",cta="WHICH NUMBER SHOCKED YOU? 👇",cta_from=(2,"and"),
  scene=dict(clip=1,frm="Thirty",to=(2,"and"),head="IN <em>5 NUMBERS</em>",sub="exit → return",q="Jensen Huang's exit and return, in numbers?",mode="numbers",
   items=[["33","years as CEO"],["5","days to a public 'no'"],["11","days to a 'yes'"],["+31.5%","NVDA in one day"],["3","House committees · 1 Dec"]],
   note="Sources: NVIDIA filings, AP, Gotrade",stickers=["🔢","⏱️","📈","🏛️"]),hl=["five","numbers","thirty","eleven","one","three"]),
}
out={}
for k,(sid,v) in enumerate(S.items()):
    sc=v['scene']; s=d[sid]; texts=[c['text'] for c in s['clips']]
    for (ci,w) in [(sc['clip'],sc['frm']),sc['to'],v['cta_from']]:
        assert any(w.lower() in t.lower() for t in texts[ci].split()), (sid,ci,w)
    out[sid]={"clips":texts,"title":s['title'],"hl":v['hl'],"hook":v['hook'],"cta":v['cta'],"cta_from":v['cta_from'][1],"cta_clip":v['cta_from'][0],
      "pill":"JENSEN HUANG · NVIDIA","ticker":"NVDA <b>▲ 31.5%</b>","src":SRC,"accent":AC[k][0],"accent2":AC[k][1],"pip":{"x":540,"y":1172,"r":112},
      "scenes":[{"clip":sc['clip'],"from":sc['frm'],"to":sc['to'][1],"to_clip":sc['to'][0],"kind":"mac","head":sc['head'],"sub":sc['sub'],"q":sc['q'],
                 "mode":sc['mode'],"items":sc['items'],"note":sc['note'],"stickers":sc['stickers']}]}
json.dump(out,open('spec.json','w'),ensure_ascii=False,indent=1); print(len(out),"ok")
