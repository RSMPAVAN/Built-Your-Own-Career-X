import sys,os; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,io,json
from PIL import Image
LINES=json.load(open("v2/ep_nehru/lines.json"))
def secs(who,text):
    need=len(text.split())/(2.6 if who=="Nithya" else 2.4)+0.5
    return next(c for c in (4,6,8) if c>=need)
for l in LINES: l["seconds"]=secs(l["who"],l["text"])
ALL=sorted({f for l in LINES for f in l["frames"]})
def b64(p):
    im=Image.open(p).convert("RGB"); im=im.resize((768,int(im.height*768/im.width))); b=io.BytesIO(); im.save(b,"JPEG",quality=85); return base64.b64encode(b.getvalue()).decode()
SYS=("You write Veo 3.1 image-to-video prompts for the Navura Media podcast. For each script line, look at its FIRST reference still and write ONE prompt as labelled sections in one paragraph, exactly: "
"Shot (framing exactly as the still), Subject and image consistency (who, wardrobe, the NM desk microphone on the table in front of them, studio details visible in the still), Action (a calm real podcast conversation: the speaker talks directly to the other person off-screen, lips clearly speaking the words, small natural head and hand movements, blinking, listening cues), Dialogue (the EXACT line in double quotes, then voice direction), Camera (static), Lighting and style (match the still), Audio (only that speaker's voice plus quiet room tone), Negatives. "
"Describe the characters as 'Nithya, the podcast host' or 'Jawaharlal Nehru, AI-reimagined, in his white achkan with a red rose and white cap'. Pronunciation hints go in the Dialogue section after the quote: Nehru = 'NEH-roo', Chacha = 'CHA-cha', Navura = 'nah-VOO-rah'. "
"Voices: Nehru is a calm, dignified, warm, thoughtful elderly Indian gentleman with a cultured accent, unhurried; Nithya is a warm, clear, curious Indian English female voice at a natural conversational pace. No other speakers, text, music or scene changes. Mics stay on the table. Return ONLY JSON: {\"prompts\":{\"L0\":str,...}}")
LOCK=" Camera: static locked-off frame, no camera movement, no cuts. Keep the studio, faces, wardrobe and the desk microphone identical to the reference still. No subtitles or on-screen text, no music."
user=[{"type":"text","text":"Script lines:\n"+json.dumps([{"id":l["id"],"who":l["who"],"first_frame":l["frames"][0],"text":l["text"]} for l in LINES],indent=1)+"\n\nReference stills attached in this order: "+", ".join(ALL)}]
for p in ALL: user.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64(p)}})
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
json.dump(LINES,open("v2/ep_nehru/lines_with_prompts.json","w"),indent=1)
for l in LINES: print(l["id"],l["who"],l["seconds"],"s |",l["text"])
print("generated seconds",sum(l["seconds"] for l in LINES))
