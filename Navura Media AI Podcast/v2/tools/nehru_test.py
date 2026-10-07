import sys,os; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,io,json,time,subprocess,difflib,re
from PIL import Image
b64=lambda b: base64.b64encode(b).decode()
def jpg(path,w=1280):
    im=Image.open(path).convert("RGB")
    if im.width>w: im=im.resize((w,int(im.height*w/im.width)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=90); return b.getvalue()
plate=jpg("v2/plate_v2.png"); hero=jpg("v2/kit/H0_hero_two_shot.jpg")
prompt=("Image 1 is the approved empty Navura Media podcast studio (keep room, table, chairs, NM desk microphones, mugs and window exactly). Image 2 is the approved two-shot style reference (match its realistic cinematic look and mic style). "
"Create a close-up of a podcast guest seated in the right-hand chair: an AI-reimagined portrayal of Jawaharlal Nehru, India's first Prime Minister, in his familiar white achkan jacket with a red rose and a white Gandhi cap, a calm, thoughtful, kindly expression, hands resting on the table. His desk microphone is in front of him. Realistic cinematic render, warm sunset window behind. Only the guest in frame. No text, no overhead boom arms.")
body={"contents":[{"role":"user","parts":[{"text":prompt},{"inlineData":{"mimeType":"image/jpeg","data":b64(plate)}},{"inlineData":{"mimeType":"image/jpeg","data":b64(hero)}}]}],"generationConfig":{"responseModalities":["IMAGE","TEXT"],"imageConfig":{"aspectRatio":"16:9","imageSize":"2K"}}}
img=None
for w in (0,20,40):
    time.sleep(w); r=vertex("gemini-3.1-flash-image",body,"global")
    if r.status_code==200 and "candidates" in r.json():
        for p in r.json()["candidates"][0].get("content",{}).get("parts",[]):
            if p.get("inlineData"): img=base64.b64decode(p["inlineData"]["data"])
        if img: break
    print("image attempt",r.status_code,str(r.json().get("promptFeedback") if r.status_code==200 else r.text[:150]))
if not img: raise SystemExit("no guest image produced")
open("v2/nehru/nehru_guest.png","wb").write(img); print("guest still saved")
# Veo test: 4 s, Fast, native speech
im=Image.open("v2/nehru/nehru_guest.png").convert("RGB"); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
im=im.crop((0,top,w,top+nh)).resize((1280,720)); b=io.BytesIO(); im.save(b,"JPEG",quality=92)
line="Welcome. Let us talk about the future."
vp=("Close-up of Jawaharlal Nehru, AI-reimagined, seated as a guest at the Navura Media podcast table with a desk microphone, a calm real podcast conversation recorded in a studio at sunset. He looks toward the host just off-screen and says warmly, in a calm, dignified, thoughtful voice: \""+line+"\" Natural lip movement matching the words, small head movement, blinking. Static camera. Audio: only his voice and quiet room tone. No text on screen.")
model="veo-3.1-fast-generate-001"
base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJ}/locations/us-central1/publishers/google/models/{model}"
rq={"instances":[{"prompt":vp,"image":{"bytesBase64Encoded":b64(b.getvalue()),"mimeType":"image/jpeg"}}],"parameters":{"aspectRatio":"16:9","durationSeconds":4,"sampleCount":1,"generateAudio":True,"personGeneration":"allow_adult","resolution":"720p"}}
r=requests.post(base+":predictLongRunning",json=rq,timeout=120); print("veo submit",r.status_code)
op=r.json()["name"]; t=time.time()
while time.time()-t<600:
    time.sleep(10); q=requests.post(base+":fetchPredictOperation",json={"operationName":op},timeout=120).json()
    if q.get("done"): break
vs=q.get("response",{}).get("videos",[])
if not vs: print("VEO RESULT: no video |",json.dumps(q.get("response",{}))[:300], q.get("error"))
else:
    open("v2/nehru/nehru_clip.mp4","wb").write(base64.b64decode(vs[0]["bytesBase64Encoded"])); print("VEO RESULT: video generated (about $0.40)")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i","v2/nehru/nehru_clip.mp4","-vn","-ac","1","-ar","16000","v2/nehru/nehru.wav"])
    with open("v2/nehru/nehru.wav","rb") as f: tr=requests.post("https://api.openai.com/v1/audio/transcriptions",data={"model":"whisper-1","language":"en"},files={"file":("p.wav",f,"audio/wav")},timeout=120).json().get("text","")
    print("heard:",tr)
