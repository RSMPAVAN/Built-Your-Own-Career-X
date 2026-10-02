"""v2 video: every line (both characters) is a Veo clip with native speech and lip-sync. Same unmodified inputs are retried when the safety filter blocks (blocked calls are free). Cost-capped; every clip transcript-checked."""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,time,json,io,re,difflib,subprocess,threading,os,concurrent.futures as cf
from PIL import Image
KIT="v2/kit"
LINES=json.load(open("v2/lines_v2.json"))
CAP=float(os.environ.get("CAP","14")); spent=0.0; lock=threading.Lock()
RATE={"veo-3.1-fast-generate-001":0.10,"veo-3.1-generate-001":0.40}
SEED={"Nithya":4242,"Gandhi":1930}
def frame(name):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
def veo(l,frame_name,model):
    img=base64.b64encode(frame(frame_name)).decode()
    base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
    body={"instances":[{"prompt":l["veo_prompt"],"image":{"bytesBase64Encoded":img,"mimeType":"image/jpeg"}}],"parameters":{"aspectRatio":"16:9","durationSeconds":l["seconds"],"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p","seed":SEED[l["who"]]}}
    for wait in (0,30,60,90):
        time.sleep(wait); r=requests.post(base+":predictLongRunning",json=body,timeout=120)
        if r.status_code!=429: break
    if r.status_code!=200:
        if "seed" in r.text.lower() and r.status_code==400: body["parameters"].pop("seed"); r=requests.post(base+":predictLongRunning",json=body,timeout=120)
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
def transcribe(path,model="whisper-1"):
    with open(path,"rb") as f:
        data={"model":model}
        if model=="whisper-1": data.update({"response_format":"verbose_json","timestamp_granularities[]":"word"})
        r=requests.post("https://api.openai.com/v1/audio/transcriptions",data=data,files={"file":(path,f,"audio/wav")},timeout=120)
    return r.json()
def check(l,tr):
    a,b=norm(tr.get("text","")),norm(l["text"]); score=difflib.SequenceMatcher(None,a,b).ratio(); toks=a.split(); bad=[]
    for k,thr in KEYS.items():
        if k in b.split() and not any(difflib.SequenceMatcher(None,k,t).ratio()>=thr for t in toks): bad.append(k)
    return score,bad
def run(l):
    frames=l["frames"]; plan=[]
    models=["veo-3.1-fast-generate-001","veo-3.1-generate-001"] if l["who"]=="Gandhi" else ["veo-3.1-fast-generate-001"]
    for i in range(int(os.environ.get("TRIES","8")) if l["who"]=="Gandhi" else 3):
        plan.append((frames[(i//2)%len(frames)],models[i%len(models)]))
    log=[]
    for fr,m in plan:
        cost=RATE[m]*l["seconds"]
        with lock:
            if spent+cost>CAP: log.append(("cap reached",)); break
        data,st=veo(l,fr,m)
        if not data: log.append((fr,m,st)); continue
        with lock: globals()["spent"]+=cost
        fn=f"v2/clips/{l['id']}.mp4"; open(fn,"wb").write(data)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",fn,"-vn","-ac","1","-ar","16000",f"v2/clips/{l['id']}.wav"])
        tr=transcribe(f"v2/clips/{l['id']}.wav"); score,bad=check(l,tr); w=tr.get("words",[])
        alt=transcribe(f"v2/clips/{l['id']}.wav","gpt-4o-transcribe").get("text","")
        log.append((fr,m,"generated",round(cost,2),round(score,3),bad,tr.get("text",""),alt))
        if score>=0.93 and not bad:
            return l["id"],dict(ok=True,model=m,frame=fr,start=min(x["start"] for x in w),end=max(x["end"] for x in w),log=log)
    return l["id"],dict(ok=False,log=log)
if __name__=="__main__":
    os.makedirs("v2/clips",exist_ok=True); res={}
    only=sys.argv[1:]
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(run,l) for l in LINES if not only or l["id"] in only]:
            k,v=f.result(); res[k]=v; print(k,"OK" if v["ok"] else "FAILED",v.get("model"),v.get("frame"),v.get("start"),v.get("end"))
            for x in v["log"]: print("    ",x)
    print(f"\nestimated Veo spend this run: ${spent:.2f}")
    old=json.load(open("v2/clips/result.json")) if os.path.exists("v2/clips/result.json") else {}
    old.update(res); json.dump(old,open("v2/clips/result.json","w"),indent=1,default=str)
