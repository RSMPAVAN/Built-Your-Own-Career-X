from common import *
from script import SCRIPT
import base64,time,json,io,sys,re,difflib,concurrent.futures as cf
from PIL import Image
KIT=f"{REPO}/assets/gandhi_kit"
CLIP={"L0":4,"L1":6,"L2":6,"L3":6,"L4":8,"L5":6}
def frame(name):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
STYLE="Photorealistic cinematic look, warm sunset window light with teal and amber accents, shallow depth of field, static camera, no cuts, no subtitles or text on screen, no music."
def prompt(l):
    shot="Close-up" if "close" in l["frame"] else "Medium shot"
    if l["who"]=="Nithya":
        return (f"{shot} of Nithya, the podcast host, seated in the Navura Media studio at sunset, looking toward her guest just off-screen. She says warmly, in clear Indian English, at an unhurried natural pace: \"{l['text']}\" "
                "Natural lip movement matching the words, subtle head movement and blinking, small expressive hand movements. "+STYLE+" Audio: only her voice, warm and clear, with quiet studio room tone.")
    return (f"{shot} of the elderly Mahatma Gandhi seated in the Navura Media studio at sunset, listening to the host just off-screen with a gentle smile. After a brief pause he says softly and slowly, in a calm, gentle, elderly Indian voice: \"{l['text']}\" "
            "Natural lip movement matching the words, a slight nod at the end, then a calm pause. "+STYLE+" Audio: only his voice, soft and unhurried, with quiet studio room tone.")
def norm(t): return re.sub(r"[^a-z0-9 ]","",re.sub(r"-"," ",t.lower())).split()
def veo(l,model):
    img=base64.b64encode(frame(l["frame"])).decode()
    base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
    body={"instances":[{"prompt":prompt(l),"image":{"bytesBase64Encoded":img,"mimeType":"image/jpeg"}}],"parameters":{"aspectRatio":"16:9","durationSeconds":CLIP[l["id"]],"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p"}}
    for wait in (0,30,60,90):
        time.sleep(wait); r=requests.post(base+":predictLongRunning",json=body,timeout=120)
        if r.status_code!=429: break
    if r.status_code!=200: return None,f"submit {r.status_code} {r.text[:200]}"
    op=r.json()["name"]; t=time.time()
    while time.time()-t<900:
        time.sleep(10); q=requests.post(base+":fetchPredictOperation",json={"operationName":op},timeout=120).json()
        if q.get("done"): break
    if "error" in q: return None,"error "+json.dumps(q["error"])[:200]
    vs=q.get("response",{}).get("videos",[])
    if not vs: return None,"filtered "+json.dumps(q.get("response",{}))[:160]
    return base64.b64decode(vs[0]["bytesBase64Encoded"]),"ok"
def transcribe(path):
    with open(path,"rb") as f:
        r=requests.post("https://api.openai.com/v1/audio/transcriptions",data={"model":"whisper-1","response_format":"verbose_json","timestamp_granularities[]":"word"},files={"file":(path,f,"audio/wav")},timeout=120)
    return r.json()
def run(l):
    log=[]; models=["veo-3.1-fast-generate-001","veo-3.1-generate-001"] if l["who"]=="Gandhi" else ["veo-3.1-fast-generate-001","veo-3.1-fast-generate-001"]
    for attempt,m in enumerate(models):
        data,st=veo(l,m); log.append((m,st))
        if not data: continue
        fn=f"clips/{l['id']}.mp4"; open(fn,"wb").write(data)
        import subprocess; subprocess.run(["ffmpeg","-y","-loglevel","error","-i",fn,"-vn","-ac","1","-ar","16000",f"clips/{l['id']}.wav"])
        tr=transcribe(f"clips/{l['id']}.wav"); said=norm(tr.get("text","")); want=norm(l["text"])
        score=difflib.SequenceMatcher(None,said,want).ratio()
        words=tr.get("words",[]); end=max([w["end"] for w in words]) if words else None; start=min([w["start"] for w in words]) if words else None
        log.append(("check",round(score,2),tr.get("text","")))
        if score>=0.9: return l["id"],dict(ok=True,model=m,score=score,start=start,end=end,log=log)
    return l["id"],dict(ok=False,log=log)
if __name__=="__main__":
    import os; os.makedirs("clips",exist_ok=True)
    res={}
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(run,l) for l in SCRIPT]:
            k,v=f.result(); res[k]=v; print(k,v["ok"],v.get("model"),v.get("score"),v.get("start"),v.get("end")); 
            if not v["ok"]: print("  ",v["log"])
    json.dump(res,open("clips/result.json","w"),indent=1,default=str)
