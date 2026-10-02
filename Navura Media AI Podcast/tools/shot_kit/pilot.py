from common import *
import base64,time,json,io,sys,concurrent.futures as cf
from PIL import Image
KIT=f"{REPO}/assets/gandhi_kit"
def frame(name):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
    im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
STYLE="Photorealistic cinematic look, warm sunset window light with teal and amber accents, shallow depth of field, static camera, no cuts, no subtitles or text on screen, no music."
SHOTS={
 "P1_nithya":dict(img="S02_nithya_close",dur=4,prompt=("Close-up of Nithya, the podcast host, seated in the Navura Media studio at sunset, looking toward her guest just off-screen to her left. "
   "She asks warmly and curiously, in clear Indian English: \"Mahatma, why salt? Why did you choose salt to challenge an empire?\" Natural lip movement matching the words, subtle head movement, blinking, a small raise of the eyebrows on 'why salt'. "
   +STYLE+" Audio: only her voice, warm and clear, with quiet studio room tone.")),
 "P2_gandhi":dict(img="S04_gandhi_close",dur=6,prompt=("Close-up of the elderly Mahatma Gandhi seated in the Navura Media studio at sunset, looking toward the host just off-screen to his right, with a gentle smile. "
   "After a brief pause he answers softly and slowly, in a calm, gentle, elderly Indian voice: \"Next to air and water, salt is perhaps the greatest necessity of life.\" Natural lip movement matching the words, a slight nod at the end, then a calm pause. "
   +STYLE+" Audio: only his voice, soft and unhurried, with quiet studio room tone."))}
def job(key,model):
    s=SHOTS[key]; img=base64.b64encode(frame(s["img"])).decode()
    base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
    body={"instances":[{"prompt":s["prompt"],"image":{"bytesBase64Encoded":img,"mimeType":"image/jpeg"}}],
          "parameters":{"aspectRatio":"16:9","durationSeconds":s["dur"],"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p"}}
    for wait in (0,30,60,90):
        time.sleep(wait); r=requests.post(base+":predictLongRunning",json=body,timeout=120)
        if r.status_code!=429: break
    if r.status_code!=200: return key,"submit",r.status_code,r.text[:400]
    op=r.json()["name"]; t=time.time()
    while time.time()-t<900:
        time.sleep(10); q=requests.post(base+":fetchPredictOperation",json={"operationName":op},timeout=120).json()
        if q.get("done"): break
    if "error" in q: return key,"error",json.dumps(q["error"])[:500],""
    vs=q.get("response",{}).get("videos",[])
    if not vs: return key,"nodata",json.dumps(q.get("response",{}))[:400],""
    open(f"pilot/{key}.mp4","wb").write(base64.b64decode(vs[0]["bytesBase64Encoded"])); return key,"ok",round(time.time()-t),model
if __name__=="__main__":
    model=sys.argv[1] if len(sys.argv)>1 else "veo-3.1-fast-generate-001"
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(job,k,model) for k in SHOTS]: print(f.result())
