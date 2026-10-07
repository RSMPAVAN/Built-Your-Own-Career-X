"""One pipeline for every character: voice -> base clip (once, cached) -> lip-sync per line -> verify -> assemble.
Provider calls are isolated in small functions so a stage can be swapped (Veo, Kling, Wan, own GPU) without touching the rest."""
import os,sys,json,io,time,base64,hashlib,subprocess,re,difflib
import requests
from PIL import Image
os.environ.setdefault("REQUESTS_CA_BUNDLE","/root/.ccr/ca-bundle.crt")
HERE=os.path.dirname(os.path.abspath(__file__)); V2=os.path.dirname(HERE)
CFG=json.load(open(f"{HERE}/config.json")); CACHE=f"{HERE}/cache"; os.makedirs(CACHE,exist_ok=True)
LEDGER=f"{CACHE}/ledger.json"
PROJ="navuramedia-509306"
def ledger_add(item,usd):
    L=json.load(open(LEDGER)) if os.path.exists(LEDGER) else []
    L.append({"item":item,"est_usd":usd,"t":time.strftime("%Y-%m-%d %H:%M:%S")}); json.dump(L,open(LEDGER,"w"),indent=1)
    return sum(x["est_usd"] for x in L)
def key(*parts): return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]
def frame_data_uri(still):
    im=Image.open(f"{V2}/assets/kit/{still}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=90)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
def fal(endpoint,body,timeout=1500,tries=3):
    last=None
    for attempt in range(tries):
        try:
            r=requests.post(f"https://queue.fal.run/{endpoint}",json=body,timeout=180); j=r.json()
            if "status_url" not in j: raise RuntimeError(f"{endpoint} submit {r.status_code} {str(j)[:300]}")
            t=time.time()
            while time.time()-t<timeout:
                time.sleep(8); s=requests.get(j["status_url"],timeout=60).json()
                if s.get("status") in ("COMPLETED","FAILED","ERROR"): break
            res=requests.get(j["response_url"],timeout=120); out=res.json()
            if res.status_code!=200 or "video" not in out: raise RuntimeError(f"{endpoint} failed {res.status_code} {str(out)[:300]}")
            return out
        except RuntimeError as e:
            last=e
            if any(x in str(e) for x in ("504","503","502","unavailable","timeout")) and attempt<tries-1: time.sleep(20*(attempt+1)); continue
            raise
    raise last
# ---- stage 1: voice ----
def tts(character,text):
    v=CFG["characters"][character]["voice"]; f=f"{CACHE}/tts_{key(character,v['engine'],v['name'],text)}.wav"
    if os.path.exists(f): return f
    if v["engine"]=="openai":
        r=requests.post("https://api.openai.com/v1/audio/speech",json={"model":"gpt-4o-mini-tts","voice":v["name"],"input":text,"instructions":v["style"],"response_format":"wav"},timeout=120); r.raise_for_status(); open(f,"wb").write(r.content)
    else:
        body={"contents":[{"role":"user","parts":[{"text":v["style"]+text}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":v["name"]}}}}}
        url=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/gemini-2.5-pro-tts:generateContent"
        for _ in range(4):
            r=requests.post(url,json=body,timeout=180)
            if r.status_code==200: break
            time.sleep(15)
        r.raise_for_status(); raw=base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]); open(f+".pcm","wb").write(raw)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","s16le","-ar","24000","-ac","1","-i",f+".pcm","-af","silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse",f],check=True)
    return f
def norm(t): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]","",re.sub(r"[-–—]"," ",t.lower()))).strip()
def verify_audio(path,text):
    with open(path,"rb") as fh: t=requests.post("https://api.openai.com/v1/audio/transcriptions",data={"model":"whisper-1","language":"en"},files={"file":(path,fh,"audio/wav")},timeout=120).json().get("text","")
    return round(difflib.SequenceMatcher(None,norm(t),norm(text)).ratio(),3),t
# ---- stage 2: base clip, once per character (cached) ----
def base_clip(character,seconds=6):
    c=CFG["characters"][character]; k=key(character,c["still"],c["base_prompt"],seconds); f=f"{CACHE}/base_{character}_{k}.json"
    if os.path.exists(f): return json.load(open(f))["url"]
    total=ledger_add(f"base clip {character} {seconds}s",CFG["price_estimates_usd"]["seedance_base_6s"])
    if total>CFG["budget_guard_usd"]: raise SystemExit(f"budget guard: estimated spend {total:.2f} > {CFG['budget_guard_usd']}")
    out=fal(CFG["fal_models"]["base_clip"],{"prompt":c["base_prompt"],"image_url":frame_data_uri(c["still"]),"duration":str(seconds),"resolution":"720p","aspect_ratio":"16:9","generate_audio":False})
    json.dump({"url":out["video"]["url"]},open(f,"w")); return out["video"]["url"]
# ---- stage 3: lip-sync one line ----
def lipsync(character,text,base_url,audio_path):
    k=key(character,text,base_url,audio_path); f=f"{CACHE}/line_{k}.json"
    if os.path.exists(f): return json.load(open(f))["url"]
    total=ledger_add(f"lipsync {character}: {text[:30]}",CFG["price_estimates_usd"]["lipsync_pro_per_line"])
    if total>CFG["budget_guard_usd"]: raise SystemExit(f"budget guard: estimated spend {total:.2f} > {CFG['budget_guard_usd']}")
    aud="data:audio/wav;base64,"+base64.b64encode(open(audio_path,"rb").read()).decode()
    out=fal(CFG["fal_models"]["lipsync"],{"video_url":base_url,"audio_url":aud,"model":"lipsync-2-pro","sync_mode":"bounce"})
    json.dump({"url":out["video"]["url"]},open(f,"w")); return out["video"]["url"]
# ---- stage 4: assemble the conversation into one video (runs on fal so it also works where files cannot be downloaded) ----
def assemble(results,name="conversation"):
    ledger_add("merge videos",0.02)
    out=fal("fal-ai/ffmpeg-api/merge-videos",{"video_urls":[r["video"] for r in results]})
    return out["video"]["url"]
def run_line(character,text):
    audio=tts(character,text); sc,heard=verify_audio(audio,text)
    if sc<0.95: raise RuntimeError(f"voice check failed ({sc}): heard '{heard}'")
    ledger_add(f"tts {character}",CFG["price_estimates_usd"]["tts_per_line"])
    base=base_clip(character); url=lipsync(character,text,base,audio)
    return {"character":character,"text":text,"voice_check":sc,"audio":audio,"base_clip":base,"video":url}
if __name__=="__main__":
    script=json.load(open(sys.argv[1])); results=[]
    from concurrent.futures import ThreadPoolExecutor
    chars=sorted({l["character"] for l in script})
    with ThreadPoolExecutor(2) as ex: list(ex.map(base_clip,chars))   # base clips once per character, in parallel
    for l in script:
        r=run_line(l["character"],l["text"]); results.append(r); print(json.dumps({k:r[k] for k in ("character","text","voice_check","video")}),flush=True)
    final=assemble(results); print("ONE VIDEO:",final,flush=True)
    json.dump({"lines":results,"final":final},open(f"{HERE}/last_run.json","w"),indent=1)
    print("estimated spend this run (ledger total):",round(sum(x["est_usd"] for x in json.load(open(LEDGER))),2))
