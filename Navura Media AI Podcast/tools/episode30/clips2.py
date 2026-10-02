from common import *
import base64,time,json,io,re,difflib,subprocess,threading,concurrent.futures as cf
from PIL import Image
KIT=f"{REPO}/assets/gandhi_kit"
LINES=json.load(open("lines_with_prompts.json"))
CAP=10.0; spent=0.0; lock=threading.Lock(); events=[]
RATE={"veo-3.1-fast-generate-001":0.10,"veo-3.1-generate-001":0.40}
def frame(name):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
def veo(l,model):
    img=base64.b64encode(frame(l["frame"])).decode()
    base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
    body={"instances":[{"prompt":l["veo_prompt"],"image":{"bytesBase64Encoded":img,"mimeType":"image/jpeg"}}],"parameters":{"aspectRatio":"16:9","durationSeconds":l["seconds"],"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p"}}
    for wait in (0,30,60,90):
        time.sleep(wait); r=requests.post(base+":predictLongRunning",json=body,timeout=120)
        if r.status_code!=429: break
    if r.status_code!=200: return None,f"submit {r.status_code} {r.text[:120]}"
    op=r.json()["name"]; t=time.time()
    while time.time()-t<900:
        time.sleep(10); q=requests.post(base+":fetchPredictOperation",json={"operationName":op},timeout=120).json()
        if q.get("done"): break
    if "error" in q: return None,"error "+json.dumps(q["error"])[:140]
    vs=q.get("response",{}).get("videos",[])
    if not vs: return None,"filtered"
    return base64.b64decode(vs[0]["bytesBase64Encoded"]),"ok"
NUM=[("seventy eight","78"),("eighteen eighty two","1882"),("two hundred and forty","240"),("two hundred forty","240"),("twenty four","24")]
def norm(t):
    t=re.sub(r"[-–—]"," ",t.lower()); t=re.sub(r"[^a-z0-9 ]","",t); t=re.sub(r"\s+"," ",t).strip()
    for a,b in NUM: t=t.replace(a,b)
    return t
KEYS={"dandi":0.99,"sabarmati":0.8,"navura":0.7}
def transcribe(path):
    with open(path,"rb") as f:
        r=requests.post("https://api.openai.com/v1/audio/transcriptions",data={"model":"whisper-1","response_format":"verbose_json","timestamp_granularities[]":"word","prompt":"Navura, Sabarmati, Dandi, Gandhi"},files={"file":(path,f,"audio/wav")},timeout=120)
    return r.json()
def check(l,tr):
    a,b=norm(tr.get("text","")),norm(l["text"]); score=difflib.SequenceMatcher(None,a,b).ratio()
    toks=a.split(); bad=[]
    for k,thr in KEYS.items():
        if k in b.split() and not any(difflib.SequenceMatcher(None,k,t).ratio()>=thr for t in toks): bad.append(k)
    return score,bad
def run(l):
    plan=["veo-3.1-fast-generate-001","veo-3.1-generate-001","veo-3.1-fast-generate-001","veo-3.1-generate-001"] if l["who"]=="Gandhi" else ["veo-3.1-fast-generate-001"]*3
    log=[]
    for m in plan:
        cost=RATE[m]*l["seconds"]
        with lock:
            if spent+cost>CAP: log.append(("cap reached",)); break
        data,st=veo(l,m)
        if not data: log.append((m,st)); continue
        with lock: globals()["spent"]+=cost
        fn=f"clips2/{l['id']}.mp4"; open(fn,"wb").write(data)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",fn,"-vn","-ac","1","-ar","16000",f"clips2/{l['id']}.wav"])
        tr=transcribe(f"clips2/{l['id']}.wav"); score,bad=check(l,tr); w=tr.get("words",[])
        log.append((m,"generated",round(cost,2),round(score,3),bad,tr.get("text","")))
        if score>=0.93 and not bad:
            return l["id"],dict(ok=True,model=m,start=min(x["start"] for x in w),end=max(x["end"] for x in w),log=log)
    return l["id"],dict(ok=False,log=log)
if __name__=="__main__":
    res={}
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(run,l) for l in LINES]:
            k,v=f.result(); res[k]=v; print(k,"OK" if v["ok"] else "FAILED",v.get("model"),v.get("start"),v.get("end")); [print("    ",x) for x in v["log"]]
    print(f"\nestimated Veo spend this run: ${spent:.2f}")
    json.dump(res,open("clips2/result.json","w"),indent=1,default=str)
