import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,io,json
from PIL import Image
sel=json.load(open("ep30/selection.json"))
FR={"L0":["S02_nithya_close"],"L1":["S01_nithya_medium","S02_nithya_close"],"L2":["S03_gandhi_medium","S04_gandhi_close"],"L3":["S02_nithya_close","S01_nithya_medium"],"L4":["S04_gandhi_close","S03_gandhi_medium"],"L5":["S01_nithya_medium","S02_nithya_close"]}
def secs(who,text):
    pace=2.6 if who=="Nithya" else 2.4
    need=len(text.split())/pace+0.5
    return next(c for c in (4,6,8) if c>=need)
LINES=[dict(id=l["id"],who=l["who"],text=l["text"],frames=FR[l["id"]],seconds=secs(l["who"],l["text"])) for l in sel["lines"]]
ALL=sorted({f for l in LINES for f in l["frames"]})
def b64(n):
    im=Image.open(f"v2/kit/{n}.jpg").convert("RGB"); im=im.resize((768,int(im.height*768/im.width))); b=io.BytesIO(); im.save(b,"JPEG",quality=85); return base64.b64encode(b.getvalue()).decode()
SYS=("You write Veo 3.1 image-to-video prompts for the Navura Media podcast. For each script line you receive, look at its FIRST reference still and write ONE prompt as labelled sections in one paragraph, in this exact structure: "
"Shot (framing exactly as the still), Subject and image consistency (who, wardrobe, the NM desk microphone on the table in front of them, studio details visible in the still), Action (natural podcast conversation: the speaker talks directly to the other person off-screen, lips clearly speaking the words, small natural head and hand movements, blinking), Dialogue (the EXACT line in double quotes, then voice direction), Camera (static), Lighting and style (match the still), Audio (only that speaker's voice plus quiet room tone), Negatives. "
"The prompts must describe the character as 'Nithya, the podcast host' or 'the elderly Mahatma Gandhi, AI-reimagined' and always say it is a calm real podcast conversation recorded in a studio. Pronunciation hints go in the Dialogue section after the quote: Navura = 'nah-VOO-rah', Sabarmati = 'SAH-bur-mah-tee', Dandi = 'DAHN-dee' (not Dundee), Gandhi = 'GAHN-dee'. "
"Voices: Gandhi is a calm, gentle, elderly Indian man, soft and unhurried, a brief pause before speaking; Nithya is a warm, clear, curious Indian English female voice at a natural conversational pace. Never add other speakers, text, music or scene changes. Mics stay on the table; no overhead arms. Return ONLY JSON: {\"prompts\":{\"L0\":str,...}}")
LOCK=" Camera: static locked-off frame, no camera movement, no cuts. Keep the studio, faces, wardrobe and the desk microphone identical to the reference still. No subtitles or on-screen text, no music."
user=[{"type":"text","text":"Script lines:\n"+json.dumps([{"id":l["id"],"who":l["who"],"first_frame":l["frames"][0],"text":l["text"]} for l in LINES],indent=1)+"\n\nReference stills attached in this order: "+", ".join(ALL)}]
for n in ALL: user.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64(n)}})
msgs=[{"role":"system","content":SYS},{"role":"user","content":user}]
for rnd in range(3):
    r=requests.post("https://api.openai.com/v1/chat/completions",json={"model":"gpt-5.1","messages":msgs,"response_format":{"type":"json_object"}},timeout=300); r.raise_for_status()
    txt=r.json()["choices"][0]["message"]["content"]; P=json.loads(txt)["prompts"]
    errs=[f"{l['id']}: prompt must contain the exact line in double quotes" for l in LINES if f'"{l["text"]}"' not in P.get(l["id"],"")]
    errs+=[f"{l['id']}: missing section label(s)" for l in LINES if not all(k in P.get(l["id"],"") for k in ("Shot","Dialogue","Camera","Audio","Negatives"))]
    print("round",rnd,errs)
    if not errs: break
    msgs+=[{"role":"assistant","content":txt},{"role":"user","content":"Fix and return the full JSON:\n"+"\n".join(errs)}]
for l in LINES: l["veo_prompt"]=P[l["id"]].rstrip()+LOCK
json.dump(LINES,open("v2/lines_v2.json","w"),indent=1)
for l in LINES: print(l["id"],l["who"],l["seconds"],"s",l["frames"],"|",l["text"])
print("\nL2 prompt:\n",next(l for l in LINES if l["id"]=="L2")["veo_prompt"][:1400])
