import json, re, sys
sys.path.insert(0, "/home/claude/zoho-shorts")
from autopilot import flow
HAIR = ["thick dark hair in a neat side part", "thick dark hair in a textured quiff", "thick dark hair slicked back neatly",
        "thick wavy dark hair pushed back", "thick dark hair combed up with volume", "thick dark hair in a classic side-swept style",
        "thick dark hair with a soft modern fringe", "thick dark hair in a tidy pompadour", "thick slightly curly dark hair, neatly shaped",
        "thick dark hair in a clean side part with volume"]
LOOKS = [
 ("a black fine-knit turtleneck", "in a modern glass office at night with soft city lights blurred behind him", "a short trimmed beard", "no glasses"),
 ("a navy blazer over a plain white t-shirt", "in a minimal studio with warm wood panels and green plants softly blurred behind him", "light stubble", "thin gold-rim glasses"),
 ("an olive bomber jacket over a grey t-shirt", "on a rooftop at golden hour with a soft city skyline blurred behind him", "a full short beard", "no glasses"),
 ("a crisp white linen shirt with the top button open", "in a bright modern coworking space with large windows softly blurred behind him", "a neat short beard", "no glasses"),
 ("a charcoal grey suit with a light blue shirt, no tie", "in a high-rise boardroom with floor-to-ceiling windows softly blurred behind him", "a trimmed beard", "black rectangular glasses"),
 ("a dark denim shirt with sleeves rolled up", "in a creative studio with soft purple and blue neon lights blurred behind him", "light stubble", "no glasses"),
 ("a beige cable-knit sweater", "in a cozy study with tall wooden bookshelves softly blurred behind him", "a short full beard", "round tortoiseshell glasses"),
 ("a grey zip hoodie over a black t-shirt", "in a modern tech lab with blue-lit server racks softly blurred behind him", "a short beard", "no glasses"),
 ("a maroon polo shirt", "in a calm studio with soft acoustic panels and warm lamps blurred behind him", "a neat trimmed beard", "no glasses"),
 ("a light blue oxford shirt with sleeves rolled up", "on a terrace overlooking the sea at sunset, softly blurred behind him", "light stubble", "thin black glasses"),
]
G = [
 "he holds up one hand like a stop sign, then turns it into an open palm toward the camera",
 "he counts on his fingers, one, two, three, with a confident smile",
 "he leans forward and taps the table edge twice as if making a point",
 "he raises both eyebrows and tilts his head as if asking a big question",
 "he spreads both hands wide apart as if showing something huge",
 "he crosses his arms, then uncrosses them and points one finger at the camera",
 "he touches his chin, thinking, then nods slowly",
 "he makes a small downward chopping motion with one flat hand on each key word",
 "he points to his left side as if showing a chart next to him",
 "he shrugs with open palms, half smiling",
 "he rubs his hands together as if about to reveal a secret",
 "he holds one hand flat and lifts it in steps like a rising chart",
 "he lowers one flat hand quickly like a falling chart, with a serious face",
 "he puts one hand on his chest, sincere",
 "he shakes his head slightly and wags one finger",
 "he snaps his fingers and points at the camera",
 "he holds up two fingers, then three fingers",
 "he makes a balancing gesture with both hands like weighing two options",
 "he glances to the side, then back to the camera with a knowing look",
 "he claps his hands together once softly, then opens them",
 "he gestures toward the bottom of the frame with one open hand",
 "he leans back slightly and folds his hands in front of him",
 "he draws a quick circle in the air with one finger",
 "he raises one hand high and the other low to show a big gap",
 "he gives a thumbs up with a warm smile",
 "he points up with one finger as if remembering something important",
 "he holds both palms facing each other as if holding a box",
 "he waves one hand dismissively, then gets serious",
 "he taps his temple with one finger, then points to the camera",
 "he nods firmly while making a small fist pump",
]
SH = [
 dict(id="jh01-reasons", title="Why Jensen Huang Came Back to Nvidia: 5 Reasons #Shorts",
  lines=["Nvidia's board said no to its founder. Days later, it said yes. Here are the five reasons.",
         "Government input eased the security worry, the stock lost almost half its value, and no successor was ready.",
         "And three directors reportedly wanted him back all along. Was it the right call? Comment below."]),
 dict(id="jh02-spy", title="Jensen Huang and the 'Spy' Story: What We Actually Know #Shorts",
  lines=["Everyone is asking about the so-called spy in this story. Here is what is actually confirmed.",
         "The Justice Department says no conclusion has been reached, and intelligence officials are reportedly divided.",
         "The real case is about chip exports through one Singapore company. That probe is still open."]),
 dict(id="jh03-stock", title="Did Nvidia Bring Back Jensen Huang to Save the Stock? #Shorts",
  lines=["Was bringing the founder back just a move to rescue the stock? Let's check the numbers.",
         "The stock had lost almost half its value. The day he returned, it jumped thirty one percent.",
         "The board says it acted for shareholders, but a stock jump does not end the investigations."]),
 dict(id="jh04-investors", title="Did Investors Force Nvidia to Bring Back Jensen Huang? #Shorts",
  lines=["Did big investors force the founder back? Not legally, but the pressure was huge.",
         "Two funds urged the board to keep his return on the table, and one billionaire called the board panicked.",
         "He never had a controlling stake, so in the end, only the board could decide."]),
 dict(id="jh05-why-not-leave", title="Why Didn't Jensen Huang Just Join Another Company? #Shorts",
  lines=["Why didn't the founder simply start over somewhere else? His own moves give us clues.",
         "Within five days, he offered to come back, and reports say he discussed a comeback with close confidants.",
         "Nvidia is the company he built for thirty three years. Our guess: he never wanted another one."]),
 dict(id="jh06-own-words", title="Jensen Huang's Own Words During His 11 Days Away #Shorts",
  lines=["What did the founder actually say during his eleven days away? Three statements stand out.",
         "He admitted serious mistakes in his personal life, and said he would cooperate with the investigation.",
         "Then he said he would be honoured to return. Six days later, he was back."]),
 dict(id="jh07-washington", title="Jensen Huang's Return: How Big Was Washington's Role? #Shorts",
  lines=["How big was Washington's role in bringing the founder back? Much bigger than usual.",
         "The board says senior government officials gave input, and the White House says it helped make the deal.",
         "But not everyone in Washington agreed. One top official had wanted an outsider as the new boss."]),
 dict(id="jh08-what-changes", title="Jensen Huang Is Back: 3 Things That Change at Nvidia Now #Shorts",
  lines=["The founder is back, but Nvidia is not the same company it was two weeks ago.",
         "A new security committee, a first ever board chair, and the finance chief back in her old job.",
         "And from December first, Congress gets its questions answered. Follow for what happens next."]),
 dict(id="jh09-congress", title="Jensen Huang Faces Congress on Dec 1: What They Want to Know #Shorts",
  lines=["On December first, the founder faces three House committees behind closed doors. Here's why.",
         "Lawmakers want answers about a potential breach of national security linked to chip exports.",
         "The next day, Nvidia's top lawyer is due to appear too. This story is far from over."]),
 dict(id="jh10-numbers", title="Jensen Huang's Exit and Return in 5 Numbers #Shorts",
  lines=["Five numbers tell the whole story of the founder's exit and return.",
         "Thirty three years at the top. Five days to a public no. Eleven days to a yes.",
         "A thirty one percent jump in one day, and three House committees waiting on December first."]),
]
out = []
gi = 0
for k, s in enumerate(SH):
    cloth, place, beard, glasses = LOOKS[k]
    look = (f"wearing {cloth}, {place}; in this whole video he has {HAIR[k]}, {beard}, {glasses} - "
            f"exactly the same in every shot of this video")
    s["look"] = look; s["clips"] = []
    for i, t in enumerate(s["lines"]):
        g = G[gi % len(G)]; gi += 1
        p = flow.prompt(t, ["HOOK", "MID", "END"][i], look=look, angle=i % 3)
        p = re.sub(r"not stiff; .*?\. Vertical", f"not stiff; {g}. Vertical", p, count=1)
        assert g in p and t in p and "Huang" not in t and "Trump" not in t
        s["clips"].append({"text": t, "gesture": g, "prompt": p, "words": len(t.split())})
    out.append(s)
json.dump(out, open("jh.json", "w"), ensure_ascii=False, indent=1)
for s in out: print(s["id"], [c["words"] for c in s["clips"]])
