from osbase2 import *
import json,math
def secs(l):
    pace,over=(2.6,0.5) if l["who"]=="Nithya" else (2.4,0.5)
    need=len(l["text"].split())/pace+over
    return next((c for c in (4,6,8) if c>=need),None)
LOCK=" Camera: static locked-off frame, no camera movement, no cuts. Keep the studio, faces and wardrobe identical to the reference still. No subtitles or on-screen text, no music."
def validate(out):
    errs=[]; tot=0
    for l in out["lines"]:
        w=len(l["text"].split()); tot+=w
        if w>16: errs.append(f"{l['id']}: {w} words, max 16")
        if secs(l) is None: errs.append(f"{l['id']}: too long to fit an 8 s clip")
        if l["who"]=="Gandhi" and l["text"] not in QUOTES.values(): errs.append(f"{l['id']}: guest line must be an exact quote")
        if l["frame"] not in FRAMES: errs.append(f"{l['id']}: bad frame id")
        if l["who"]=="Gandhi" and "S0" in l["frame"] and "gandhi" not in l["frame"]: errs.append(f"{l['id']}: guest line must use a Gandhi frame")
        if l["who"]=="Nithya" and "nithya" not in l["frame"]: errs.append(f"{l['id']}: host line must use a Nithya frame")
        if l["text"] not in l.get("veo_prompt",""): errs.append(f"{l['id']}: Veo prompt must contain the exact line in quotes")
    if not 52<=tot<=66: errs.append(f"total spoken words {tot}, must be 52 to 66")
    first=" ".join(l["text"] for l in out["lines"][:2]).lower()
    if "ai" not in first.split() and "a.i." not in first and "ai-" not in first: errs.append("opening must include a spoken AI disclosure using the words 'AI-reimagined'")
    return errs,tot
msgs=[{"role":"system","content":SYSTEM},{"role":"user","content":user}]
for rnd in range(5):
    r=requests.post("https://api.openai.com/v1/chat/completions",json={"model":"gpt-5.1","messages":msgs,"response_format":{"type":"json_object"}},timeout=300)
    assert r.status_code==200,r.text[:300]
    txt=r.json()["choices"][0]["message"]["content"]; out=json.loads(txt)
    errs,tot=validate(out); print(f"round {rnd}: words={tot} errors={len(errs)}")
    for e in errs: print("   -",e)
    if not errs: break
    msgs+=[{"role":"assistant","content":txt},{"role":"user","content":"Fix these problems and return the full JSON again:\n"+"\n".join(errs)}]
for l in out["lines"]:
    l["seconds"]=secs(l); l["veo_prompt"]=l["veo_prompt"].rstrip()+LOCK
out["checked"]={"errors_left":errs,"total_words":tot,"clip_seconds":sum(l["seconds"] for l in out["lines"])}
out["facts"]=FACTS; out["quotes"]=QUOTES
json.dump(out,open("script_openai_v3.json","w"),indent=1)
print("\nTITLE:",out["title"],"| words",tot,"| clip seconds",out["checked"]["clip_seconds"],"| errors left",len(errs))
for l in out["lines"]: print(f"{l['id']} {l['who']:7} {l['seconds']}s {len(l['text'].split()):2}w {l['frame']:18} src={l['source']}\n    \"{l['text']}\"")
print("\nEXAMPLE VEO PROMPT (L"+out["lines"][2]["id"][1:]+"):\n",out["lines"][2]["veo_prompt"])
