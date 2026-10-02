from common import *
from script import SCRIPT
import base64,subprocess,math,json
VOICE={"Nithya":"Sulafat","Gandhi":"Charon"}
durs={}
for l in SCRIPT:
    body={"contents":[{"role":"user","parts":[{"text":l["text"]}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE[l["who"]]}}}}}
    for _ in range(4):
        r=vertex("gemini-2.5-flash-tts",body,"us-central1")
        if r.status_code!=429: break
        import time; time.sleep(20)
    d=r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    raw=base64.b64decode(d["data"]); open(f"{l['id']}.pcm","wb").write(raw)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","s16le","-ar","24000","-ac","1","-i",f"{l['id']}.pcm",f"{l['id']}_tts.wav"])
    sec=len(raw)/48000; durs[l["id"]]=sec
    clip=next(c for c in (4,6,8) if c>=sec+0.8) if sec+0.8<=8 else 8
    print(l["id"],l["who"],f"{sec:.1f}s speech -> Veo clip {clip}s",f"({len(l['text'].split())} words)")
    l["tts_sec"]=sec; l["clip"]=clip
json.dump({l["id"]:{"tts_sec":l["tts_sec"],"clip":l["clip"]} for l in SCRIPT},open("durations.json","w"))
print("total TTS speech",round(sum(durs.values()),1),"s; total Veo seconds",sum(l["clip"] for l in SCRIPT))
