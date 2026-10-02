from common import *
from final_script import LINES
import base64,io,json
from PIL import Image
KIT=f"{REPO}/assets/gandhi_kit"
FR=sorted({l["frame"] for l in LINES})
def b64(n):
    im=Image.open(f"{KIT}/{n}.jpg").convert("RGB"); im=im.resize((768,int(im.height*768/im.width))); b=io.BytesIO(); im.save(b,"JPEG",quality=85); return base64.b64encode(b.getvalue()).decode()
SYS=("You write Veo 3.1 image-to-video prompts for the Navura Media podcast. For each script line you receive, look at its reference still and write ONE prompt in this exact structure, as labelled sections in one paragraph: "
"Shot (framing exactly as the still), Subject and image consistency (who, wardrobe, studio details visible in the still), Action (small natural movement that suits the line; no big gestures; speaker's lips visibly speak), Dialogue (the EXACT line in double quotes, then voice direction: pace, warmth, accent), Camera (static), Lighting and style (match the still), Audio (only that speaker's voice plus quiet room tone), Negatives. "
"Pronunciation hints go inside Dialogue after the quote: Navura = 'nah-VOO-rah', Sabarmati = 'SAH-bur-mah-tee', Dandi = 'DUN-dee', Gandhi = 'GAHN-dee'. For Gandhi lines the voice is a calm, gentle, elderly Indian man, soft and unhurried, with a brief pause before speaking; for Nithya a warm, clear, curious Indian English female voice at a natural pace. "
"Never add other speakers, text, music or scene changes. Return ONLY JSON: {\"prompts\":{\"L0\":str,...}}")
LOCK=" Camera: static locked-off frame, no camera movement, no cuts. Keep the studio, faces and wardrobe identical to the reference still. No subtitles or on-screen text, no music."
user=[{"type":"text","text":"Script lines (id, speaker, frame id, exact text):\n"+json.dumps([{k:l[k] for k in ("id","who","frame","text")} for l in LINES],indent=1)+"\n\nReference stills attached in this order: "+", ".join(FR)}]
for n in FR: user.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64(n)}})
msgs=[{"role":"system","content":SYS},{"role":"user","content":user}]
for rnd in range(3):
    r=requests.post("https://api.openai.com/v1/chat/completions",json={"model":"gpt-5.1","messages":msgs,"response_format":{"type":"json_object"}},timeout=300); r.raise_for_status()
    txt=r.json()["choices"][0]["message"]["content"]; P=json.loads(txt)["prompts"]
    errs=[f"{l['id']}: prompt must contain the exact line in double quotes" for l in LINES if f'"{l["text"]}"' not in P.get(l["id"],"")]
    errs+=[f"{l['id']}: missing section label(s)" for l in LINES if not all(k in P.get(l["id"],"") for k in ("Shot","Dialogue","Camera","Audio","Negatives"))]
    print("round",rnd,"errors",errs)
    if not errs: break
    msgs+=[{"role":"assistant","content":txt},{"role":"user","content":"Fix and return the full JSON:\n"+"\n".join(errs)}]
for l in LINES: l["veo_prompt"]=P[l["id"]].rstrip()+LOCK
json.dump(LINES,open("lines_with_prompts.json","w"),indent=1)
print("\nL2 prompt:\n",next(l for l in LINES if l["id"]=="L2")["veo_prompt"])
