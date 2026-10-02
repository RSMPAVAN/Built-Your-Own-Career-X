import sys,os; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,io,json,time,re,subprocess,concurrent.futures as cf
from PIL import Image
KIT="v2/kit"
def frame(name):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
LINES={l["id"]:l for l in json.load(open("v2/lines_v2.json"))}
NITHYA_TEXT="Why choose salt for this march?"
def nithya():
    base_prompt=LINES["L0"]["veo_prompt"]; old=LINES["L0"]["text"]
    p=base_prompt.replace(f'"{old}"',f'"{NITHYA_TEXT}"'); assert NITHYA_TEXT in p
    model="veo-3.1-generate-001"
    base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
    body={"instances":[{"prompt":p,"image":{"bytesBase64Encoded":base64.b64encode(frame("S02_nithya_close")).decode(),"mimeType":"image/jpeg"}}],"parameters":{"aspectRatio":"16:9","durationSeconds":4,"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p","seed":4242}}
    for tr in range(3):
        r=requests.post(base+":predictLongRunning",json=body,timeout=120)
        if r.status_code!=200: print("nithya submit",r.status_code,r.text[:150]); time.sleep(20); continue
        op=r.json()["name"]; t=time.time()
        while time.time()-t<600:
            time.sleep(10); q=requests.post(base+":fetchPredictOperation",json={"operationName":op},timeout=120).json()
            if q.get("done"): break
        vs=q.get("response",{}).get("videos",[])
        if vs: open("v2/ten/nithya.mp4","wb").write(base64.b64decode(vs[0]["bytesBase64Encoded"])); print("nithya clip saved (Veo Standard, 4 s, about $1.60)"); return True
        print("nithya attempt",tr,"no video:",json.dumps(q.get("response",{}))[:150])
    return False
def gandhi():
    img="data:image/jpeg;base64,"+base64.b64encode(frame("S03_gandhi_medium")).decode()
    aud="data:audio/wav;base64,"+base64.b64encode(open("ep30/gandhi_audio/L2_final.wav","rb").read()).decode()
    body={"prompt":"The elderly Mahatma Gandhi, AI-reimagined, seated at a podcast table with a desk microphone in front of him, calmly answering the host off-screen, natural lip movement matching the audio, subtle head movement and blinking, relaxed peaceful posture. Static camera, warm sunset window light.",
          "image_url":img,"audio_url":aud,"num_frames":120,"frames_per_second":20,"resolution":"720p","num_inference_steps":40}
    EP="https://queue.fal.run/fal-ai/wan/v2.2-14b/speech-to-video"
    r=requests.post(EP,json=body,timeout=180); print("gandhi submit",r.status_code,r.text[:160])
    j=r.json()
    if "status_url" not in j: return False
    t=time.time()
    while time.time()-t<1500:
        time.sleep(10); s=requests.get(j["status_url"],timeout=60).json()
        if s.get("status") in ("COMPLETED","FAILED","ERROR"): break
    res=requests.get(j["response_url"],timeout=120); print("gandhi result",res.status_code,res.text[:400])
    if res.status_code==200 and res.json().get("video"):
        v=requests.get(res.json()["video"]["url"],timeout=300); open("v2/ten/gandhi_raw.mp4","wb").write(v.content); print("gandhi clip saved",len(v.content)); return True
    return False
if __name__=="__main__":
    with cf.ThreadPoolExecutor(2) as ex:
        a=ex.submit(nithya); b=ex.submit(gandhi); print("RESULT nithya",a.result(),"gandhi",b.result())
