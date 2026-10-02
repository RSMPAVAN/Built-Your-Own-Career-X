import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
import base64,json,io,time,re
from PIL import Image
b64=lambda b: base64.b64encode(b).decode()
def jpg(im,w=1600):
    im=im.convert("RGB")
    if im.width>w: im=im.resize((w,int(im.height*w/im.width)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=92); return b.getvalue()
studio=jpg(Image.open(f"{REPO}/assets/gandhi_kit/S10_empty_wide.jpg"))
PROMPT=("Edit this empty podcast studio image. Remove BOTH overhead boom-arm microphones completely: the two boom arms, their wall or desk mounts, and the hanging microphones. "
"In their place put one professional broadcast microphone standing on the table in front of each chair, on a short desk stand with a round base, angled toward where the person sits, placed on the table near the table's near edge on that side, with the glowing 'NM' logo clearly visible on each microphone. Keep the two NM mugs in the middle of the table. "
"Keep everything else identical: the room, both black office chairs, the walnut table, the acoustic panels, the amber and teal lights, the big window with the sunset, bridge and river, the camera angle and composition. The room stays empty of people. No text overlays.")
QA="You are a strict QA reviewer. Image 1 should be an empty podcast studio. Check: overhead boom arms or hanging microphones still present? microphones standing on the table in front of each chair with visible NM logo? any watermark or star mark? room otherwise the same (window, chairs, table, mugs)? Return ONLY JSON: {\"boom_arms_present\":bool,\"two_table_mics_with_NM\":bool,\"watermark\":bool,\"room_unchanged\":bool,\"people_present\":bool,\"notes\":str}"
def gen(extra=""):
    body={"contents":[{"role":"user","parts":[{"text":PROMPT+extra},{"inlineData":{"mimeType":"image/jpeg","data":b64(studio)}}]}],"generationConfig":{"responseModalities":["IMAGE","TEXT"],"imageConfig":{"aspectRatio":"16:9","imageSize":"2K"}}}
    for w in (0,20,40,70):
        time.sleep(w); r=vertex("gemini-3.1-flash-image",body,"global")
        if r.status_code!=429: break
    if r.status_code!=200: print("  http",r.status_code,r.text[:200]); return None
    j=r.json()
    if "candidates" not in j: print("  no candidates:",json.dumps(j)[:300]); return None
    for p in j["candidates"][0].get("content",{}).get("parts",[]):
        if p.get("inlineData"): return base64.b64decode(p["inlineData"]["data"])
    print("  no image; finish:",j["candidates"][0].get("finishReason"))
def qa(img):
    body={"contents":[{"role":"user","parts":[{"text":QA},{"inlineData":{"mimeType":"image/jpeg","data":b64(jpg(Image.open(io.BytesIO(img)),1280))}}]}],"generationConfig":{"responseMimeType":"application/json","temperature":0}}
    r=vertex("gemini-3.5-flash",body,"global")
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
extra=""
for i in range(4):
    img=gen(extra)
    if not img: continue
    q=qa(img); print(i,q)
    open(f"v2/plate_try{i}.png","wb").write(img)
    if not q["boom_arms_present"] and q["two_table_mics_with_NM"] and not q["watermark"] and q["room_unchanged"] and not q["people_present"]:
        open("v2/plate_v2.png","wb").write(img); print("ACCEPTED",i); break
    notes=" ".join(x for x in re.split(r"(?<=[.!?]) ",q["notes"]) if not re.search(r"water|star|mark",x,re.I)); extra=" Previous attempt problems: "+notes
