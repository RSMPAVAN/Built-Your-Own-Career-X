import os, base64, json, requests, io
from PIL import Image
os.environ.setdefault("REQUESTS_CA_BUNDLE","/root/.ccr/ca-bundle.crt")
REPO="/home/user/Built-Your-Own-Career-X/Navura Media AI Podcast"
PROJ="navuramedia-509306"
def small(path, w=1280):
    im=Image.open(path).convert("RGB"); r=w/im.width
    im=im.resize((w,int(im.height*r)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=90); return b.getvalue()
def vertex(model, body, loc="us-central1", method="generateContent"):
    host="aiplatform.googleapis.com" if loc=="global" else f"{loc}-aiplatform.googleapis.com"
    u=f"https://{host}/v1/projects/{PROJ}/locations/{loc}/publishers/google/models/{model}:{method}"
    r=requests.post(u,json=body,timeout=300)
    return r
def save_images(resp_json, prefix):
    out=[]
    for i,c in enumerate(resp_json.get("candidates",[])):
        for j,p in enumerate(c.get("content",{}).get("parts",[])):
            d=p.get("inlineData")
            if d and d["mimeType"].startswith("image"):
                f=f"{prefix}_{i}{j}.png"; open(f,"wb").write(base64.b64decode(d["data"])); out.append(f)
            elif "text" in p: print("  text:",p["text"][:300])
    return out
