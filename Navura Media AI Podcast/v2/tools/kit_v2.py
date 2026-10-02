import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,json,io,re,time,concurrent.futures as cf
from PIL import Image
b64=lambda b: base64.b64encode(b).decode()
def jpg(im,w=None):
    im=im.convert("RGB")
    if w and im.width>w: im=im.resize((w,int(im.height*w/im.width)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=90); return b.getvalue()
PLATE=Image.open("v2/plate_v2.png")
OLD_HERO=Image.open(f"{REPO}/tests/2026-10-02/8_two_shot_clean_2K.png")
GANDHI_OLD=OLD_HERO.crop((1950,430,2650,1150))
refs={"plate":jpg(PLATE,1280),"n_face":jpg(Image.open(f"{REPO}/w7.png"),1024),"n_saree":jpg(Image.open(f"{REPO}/w1.png"),1024),"gandhi":jpg(GANDHI_OLD.resize((700,720)),700),"old_hero":jpg(OLD_HERO,1280)}
MIC=("The microphones are professional broadcast mics standing on short desk stands ON THE TABLE in front of each person, angled toward their mouth, with the NM logo visible. NO overhead boom arms, no hanging microphones, nothing attached to the walls or ceiling. The mic never covers the person's mouth or face. ")
LOOK=("Realistic cinematic render look: natural proportions, realistic skin, normal-sized eyes, crisp, clean and neat, warm sunset window light with teal and amber accent lighting, shallow depth of field on close shots. No text overlays, no stray light streaks on the glass.")
INTRO=("Image 1 is the approved empty Navura Media podcast studio (match its room, table, chairs, mics, mugs and window exactly). Image 2 is a frontal face reference of the host Nithya. Image 3 shows Nithya in her teal and gold saree. Image 4 is a reference of the elderly guest Mahatma Gandhi. "
       "Keep both people's faces identical to the references: Nithya in the teal and gold saree, Gandhi in a white shawl and dhoti. ")
def gen(prompt,images,size="2K"):
    parts=[{"text":prompt}]+[{"inlineData":{"mimeType":"image/jpeg","data":b64(i)}} for i in images]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE","TEXT"],"imageConfig":{"aspectRatio":"16:9","imageSize":size}}}
    for w in (0,20,40,70,100):
        time.sleep(w); r=vertex("gemini-3.1-flash-image",body,"global")
        if r.status_code not in (429,500,502,503): break
    if r.status_code!=200: return None,f"http {r.status_code}"
    j=r.json()
    if "candidates" not in j: return None,"blocked "+json.dumps(j.get("promptFeedback"))[:150]
    for p in j["candidates"][0].get("content",{}).get("parts",[]):
        if p.get("inlineData"): return base64.b64decode(p["inlineData"]["data"]),"ok"
    return None,"no image"
QAP=("You are a strict visual QA reviewer for a podcast shot. Image 1 is the candidate. Image 2 is the approved empty studio. Image 3 is Nithya (face). Image 4 is Gandhi (face). Shot brief: {brief}\n"
 "Return ONLY JSON: {{\"nithya_match\":1-5 or null if she is not in frame,\"gandhi_match\":1-5 or null if he is not in frame,\"style_match\":1-5,\"overhead_boom_or_hanging_mic\":true/false,\"mic_on_table_in_front\":true/false/null (null if no mic should be visible),\"mic_covers_face\":true/false,\"stray_text_or_watermark\":true/false,\"hands_or_face_artifacts\":true/false,\"follows_brief\":true/false,\"notes\":\"short\"}}")
def qa(brief,img,extra_refs):
    parts=[{"text":QAP.format(brief=brief)},{"inlineData":{"mimeType":"image/jpeg","data":b64(jpg(Image.open(io.BytesIO(img)),1024))}}]+[{"inlineData":{"mimeType":"image/jpeg","data":b64(x)}} for x in extra_refs]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseMimeType":"application/json","temperature":0}}
    for w in (0,15,30,60):
        time.sleep(w); r=vertex("gemini-3.5-flash",body,"global")
        if r.status_code not in (429,500,502,503): break
    try: return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e: return {"error":str(e)}
def ok(q):
    if "error" in q: return False
    g=lambda v: v is None or v>=4
    return g(q.get("nithya_match")) and g(q.get("gandhi_match")) and (q.get("style_match") or 0)>=4 and not q.get("overhead_boom_or_hanging_mic") and q.get("mic_on_table_in_front") is not False and not q.get("mic_covers_face") and not q.get("stray_text_or_watermark") and not q.get("hands_or_face_artifacts") and q.get("follows_brief")
def clean_notes(n): return " ".join(x for x in re.split(r"(?<=[.!?]) ",n or "") if not re.search(r"water|star",x,re.I))
def produce(name,brief,images,qa_refs,tries=3):
    best=None; extra=""
    for a in range(tries):
        img,st=gen(INTRO+brief+" "+MIC+LOOK+extra,images)
        if not img: print(name,a,st); continue
        q=qa(brief,img,qa_refs); score=(q.get("style_match") or 0)+(q.get("nithya_match") or 5)+(q.get("gandhi_match") or 5)-(5 if q.get("overhead_boom_or_hanging_mic") else 0)
        print(name,a,"OK" if ok(q) else "retry",{k:q.get(k) for k in ("nithya_match","gandhi_match","style_match","overhead_boom_or_hanging_mic","mic_on_table_in_front","mic_covers_face","follows_brief")},clean_notes(q.get("notes",""))[:140])
        if best is None or score>best[0]: best=(score,img)
        if ok(q): break
        extra=" Fix these problems from the previous attempt: "+clean_notes(q.get("notes",""))
    if best: Image.open(io.BytesIO(best[1])).convert("RGB").save(f"v2/kit/{name}.jpg",quality=93)
    return best is not None
if __name__=="__main__" and sys.argv[1:]==["hero"]:
    brief=("Create the wide two-shot of the finished set: Nithya seated in the left chair and Gandhi seated in the right chair, facing each other across the walnut table, both slightly turned toward the camera, relaxed and engaged, hands resting on the table. Same camera angle and composition as the studio image. "
           "Each person has the desk microphone in front of them on the table at the near edge, slightly to the side so it does not hide the face.")
    produce("H0_hero_two_shot",brief,[refs["plate"],refs["n_face"],refs["n_saree"],refs["gandhi"],refs["old_hero"]],[refs["plate"],refs["n_face"],refs["gandhi"]])
