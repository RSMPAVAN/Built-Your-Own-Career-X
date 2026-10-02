from common import *
import base64,json,io,concurrent.futures as cf
from PIL import Image
b64=lambda b: base64.b64encode(b).decode()
def jpg(im,w=None):
    im=im.convert("RGB")
    if w and im.width>w: im=im.resize((w,int(im.height*w/im.width)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=90); return b.getvalue()
ANCHOR=Image.open(f"{REPO}/tests/2026-10-02/8_two_shot_clean_2K.png")
GANDHI=ANCHOR.crop((1950,430,2650,1150))
refs={"anchor":jpg(ANCHOR,1280),"n_face":jpg(Image.open(f"{REPO}/w7.png"),1024),"n_saree":jpg(Image.open(f"{REPO}/w1.png"),1024),"gandhi":jpg(GANDHI.resize((700,720)),700)}
LOOK=("Realistic cinematic render look, same as image 1: natural proportions, realistic skin, normal-sized eyes, crisp, clean and neat, warm sunset window light with teal and amber accent lighting, "
"shallow depth of field on close shots. No text overlays, no watermark, no stray light streaks or reflections on the glass, microphones always attached to their boom arms.")
INTRO=("Image 1 is the approved two-shot of the Navura Media podcast studio (the look to match exactly). Image 2 is a frontal face reference of the host Nithya. Image 3 shows Nithya in her teal and gold saree. "
"Image 4 is a reference of the elderly guest Mahatma Gandhi as seen in image 1. Keep both people's faces identical to the references, Nithya in the teal and gold saree, Gandhi in white shawl and dhoti, same studio, NM logo on mics and mugs. ")
SHOTS={
 "S01_nithya_medium":"Create a medium shot of Nithya seated in the left chair, from the camera position across the table, slightly angled; she is mid-conversation, mouth slightly open as if speaking, one hand gesturing; NM microphone on its boom arm near her; sunset window behind. Only Nithya in frame.",
 "S02_nithya_close":"Create a close-up of Nithya from the chest up, facing slightly to her left toward her guest, warm attentive expression, mouth softly closed in a slight smile; edge of the NM microphone visible; the sunset window softly blurred behind. Only Nithya in frame.",
 "S03_gandhi_medium":"Create a medium shot of Gandhi seated in the right chair, from across the table, gentle smile, hands resting on the table, NM microphone on its boom arm near him, sunset window behind. Only Gandhi in frame.",
 "S04_gandhi_close":"Create a close-up of Gandhi from the chest up, facing slightly to his right toward Nithya, calm attentive expression, mouth softly closed; edge of the NM microphone visible; the sunset window softly blurred behind. Only Gandhi in frame.",
 "S05_ots_to_gandhi":"Create an over-the-shoulder shot from behind Nithya: the back of her head, dark hair and a shoulder in the soft-focus left foreground, Gandhi facing the camera in sharp focus, listening with a gentle smile, window behind him.",
 "S06_ots_to_nithya":"Create an over-the-shoulder shot from behind Gandhi: the back of his bald head and white shawl in the soft-focus right foreground, Nithya facing the camera in sharp focus, speaking warmly, window behind her.",
 "S07_insert_mug":"Create a close-up insert of an NM logo mug on the polished wooden table, shallow depth of field, studio and sunset window softly blurred behind. No people.",
 "S08_insert_mic":"Create a close-up insert of an NM logo microphone on its boom arm, shallow depth of field, sunset window with bridge softly blurred behind. No people.",
 "S09_cutaway_window":"Create a wide cutaway of the studio window showing the sunset sky, the cable-stayed bridge and the river, with the edge of the wooden table and the top of a chair in the foreground. No people.",
 "S10_empty_wide":"Create the wide empty studio: same camera position and composition as image 1 but with both people removed, both chairs empty, tidy table with two NM mugs, both microphones on their boom arms. No people."}
def gen(key,extra=""):
    parts=[{"text":INTRO+SHOTS[key]+" "+LOOK+extra}]+[{"inlineData":{"mimeType":"image/jpeg","data":b64(refs[k])}} for k in ("anchor","n_face","n_saree","gandhi")]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE","TEXT"],"imageConfig":{"aspectRatio":"16:9","imageSize":"2K"}}}
    import time
    for wait in (0,20,40,70,100):
        time.sleep(wait)
        r=vertex("gemini-3.1-flash-image",body,"global")
        if r.status_code!=429: break
    if r.status_code!=200: return None,r.text[:200]
    j=r.json()
    for c in j.get("candidates",[]):
        for p in c.get("content",{}).get("parts",[]):
            d=p.get("inlineData")
            if d and d["mimeType"].startswith("image"): return base64.b64decode(d["data"]),""
    return None,"no image: "+str([c.get("finishReason") for c in j.get("candidates",[])])
QA_PROMPT=("You are a strict visual QA reviewer for a podcast shot. Image 1 is the candidate. Image 2 is the approved two-shot (style anchor). Image 3 is Nithya (face). Image 4 is Gandhi (face). "
 "Shot brief: {brief}\nReturn ONLY JSON: {{\"nithya_match\":1-5 or null if she is not in frame,\"gandhi_match\":1-5 or null if he is not in frame,\"style_match\":1-5,\"mic_attached\":true/false/null,\"stray_text_or_watermark\":true/false,\"hands_or_face_artifacts\":true/false,\"follows_brief\":true/false,\"notes\":\"short\"}}")
def qa(key,img):
    parts=[{"text":QA_PROMPT.format(brief=SHOTS[key])}]+[{"inlineData":{"mimeType":"image/jpeg","data":b64(jpg(Image.open(io.BytesIO(img)),1024))}}]+[{"inlineData":{"mimeType":"image/jpeg","data":b64(refs[k] if k!="anchor" else jpg(ANCHOR,1024))}} for k in ("anchor","n_face","gandhi")]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseMimeType":"application/json","temperature":0}}
    import time
    for wait in (0,15,30,60):
        time.sleep(wait)
        r=vertex("gemini-3.5-flash",body,"global")
        if r.status_code!=429: break
    try: return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e: return {"error":str(e),"raw":r.text[:200]}
def ok(q):
    if "error" in q: return False
    good=lambda v: v is None or v>=4
    return good(q.get("nithya_match")) and good(q.get("gandhi_match")) and (q.get("style_match") or 0)>=4 and q.get("mic_attached") is not False and not q.get("stray_text_or_watermark") and not q.get("hands_or_face_artifacts") and q.get("follows_brief")
def run(key):
    log=[]; best=None
    for attempt in range(2):
        extra="" if attempt==0 else " Fix these problems from the previous attempt: "+(log[-1]["qa"].get("notes","") if log else "")
        img,err=gen(key,extra)
        if img is None: log.append({"attempt":attempt,"error":err,"qa":{}}); continue
        q=qa(key,img); log.append({"attempt":attempt,"qa":q})
        score=(q.get("style_match") or 0)+(q.get("nithya_match") or 5)+(q.get("gandhi_match") or 5)
        if best is None or score>best[0]: best=(score,img)
        if ok(q): break
    if best: Image.open(io.BytesIO(best[1])).convert("RGB").save(f"kit/{key}.jpg",quality=92); 
    return key,bool(best),log
if __name__=="__main__":
    import sys
    keys=sys.argv[1:] or list(SHOTS)
    res={}
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(run,k) for k in keys]:
            k,saved,log=f.result(); res[k]=log; print(k,"saved" if saved else "FAILED",[ (l["attempt"],"ok" if ok(l["qa"]) else "retry/fail") for l in log])
    json.dump(res,open("kit/qa_log2.json","w"),indent=1)
