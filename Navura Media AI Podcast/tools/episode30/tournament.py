"""Script tournament: OpenAI and Google both write candidates; hard gates; cross-vendor fact-check; blind two-vendor judging; pick the winner."""
from common import *
import json,random,re,concurrent.futures as cf,time
FACTS={
 "A1":"The Salt March began on 12 March 1930 at Sabarmati Ashram, near Ahmedabad.",
 "A2":"Gandhi set out with 78 volunteers.",
 "A3":"They walked about 240 miles in 24 days to Dandi, on the coast.",
 "A4":"The Salt Act of 1882 gave the British a monopoly over salt and taxed it.",
 "A5":"Making salt was illegal for Indians.",
 "A6":"They reached Dandi on 5 April. On the morning of 6 April 1930 Gandhi picked up natural salt on the shore, breaking the law.",
 "A7":"Gandhi wrote to the Viceroy, Lord Irwin, on 2 March 1930, calling the salt tax the most iniquitous of all from the poor man's standpoint."}
Q1="Next to air and water, salt is perhaps the greatest necessity of life."
Q2="I regard this tax to be the most iniquitous of all from the poor man's standpoint."
ANGLES={"info":"Make it as informative as possible: pack in the most concrete verified facts, stated clearly and simply.","hook":"Open with the single most striking fact straight after the disclosure, then ask the question.",
        "plain":"Warm, simple, natural conversation in plain words, as a curious friend would ask.",
        "arc":"Build tension across the lines: the ask, the necessity, the injustice, then a payoff that lands in the last line."}
WRITER_SYS=("You write the HOST lines of a 30-second AI-reimagined history podcast called Navura Media. Host: Nithya (warm, curious, respectful). Guest: Gandhi, AI-reimagined. The two guest lines are fixed quotes inserted for you:\n"
 f"G1 = \"{Q1}\"\nG2 = \"{Q2}\"\n"
 "Script order: L0 host disclosure, L1 host question, L2 = G1, L3 host line, L4 = G2, L5 host closing line.\n"
 "HARD RULES: use ONLY the supplied facts; invent nothing (no extra dates, numbers, places, people, emotions about events, or anecdotes). Write numbers and years as words (e.g. 'nineteen thirty', 'seventy-eight'); no digits. "
 "Word limits: L0 6 to 8 words, one complete sentence containing the exact words 'Navura' and 'AI-reimagined' (for example: 'This is Navura, an AI-reimagined history conversation.'); L1 10 to 16 words and must lead naturally into G1 and mention why salt; L3 10 to 12 words, must bridge from G1 into G2 using the tax facts; L5 10 to 15 words, closes with the march reaching Dandi and the salt. "
 "Across L1, L3 and L5 you MUST state at least TWO concrete facts from the list, such as seventy-eight volunteers, twenty-four days, two hundred forty miles, Sabarmati, the Salt Act of eighteen eighty-two, or nineteen thirty. Be clear and concrete, never vague or poetic. Avoid awkward or unclear wording. Every host line must be speakable aloud, no abbreviations. Return ONLY JSON: {\"title\":str,\"L0\":str,\"L1\":str,\"L3\":str,\"L5\":str,\"sources\":{\"L1\":[fact ids],\"L3\":[..],\"L5\":[..]}}")
LIMITS={"L0":(6,8),"L1":(12,14),"L3":(10,12),"L5":(10,15)}
KEYS=["seventy-eight","twenty-four days","two hundred forty","two hundred and forty","sabarmati","eighteen eighty-two","nineteen thirty","twelve march","twelfth of march","salt act"]
def gpt(msgs,model="gpt-5.1",temp=None):
    body={"model":model,"messages":msgs,"response_format":{"type":"json_object"}}
    r=requests.post("https://api.openai.com/v1/chat/completions",json=body,timeout=300); r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
GEM_MODEL="gemini-3.8-flash"
def gem(prompt,system=None,model=None):
    model=model or GEM_MODEL
    body={"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json","temperature":1.0}}
    if system: body["systemInstruction"]={"parts":[{"text":system}]}
    for wait in (0,20,40,70):
        time.sleep(wait); r=vertex(model,body,"global")
        if r.status_code not in (429,500,502,503,504): break
    if r.status_code!=200: raise RuntimeError(f"gemini {model} {r.status_code} {r.text[:200]}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
def writer_prompt(angle): return "FACTS:\n"+json.dumps(FACTS,indent=1)+f"\n\nAngle: {ANGLES[angle]}\nWrite the host lines now."
def check_rules(c):
    errs=[]
    for k,(lo,hi) in LIMITS.items():
        t=c.get(k,""); w=len(t.split())
        if not lo<=w<=hi: errs.append(f"{k}: {w} words, must be {lo} to {hi}")
        if re.search(r"\d",t): errs.append(f"{k}: contains digits, write numbers as words")
    if "AI-reimagined" not in c.get("L0","") or "Navura" not in c.get("L0",""): errs.append("L0 must contain the exact words 'Navura' and 'AI-reimagined' in a complete sentence")
    tot=sum(len(c.get(k,"").split()) for k in LIMITS)+len(Q1.split())+len(Q2.split())
    hostl=" ".join(c.get(k,"") for k in ("L1","L3","L5")).lower()
    if sum(1 for k in KEYS if k in hostl)<2: errs.append("host lines L1, L3, L5 must contain at least two concrete facts (e.g. seventy-eight volunteers, twenty-four days, two hundred forty miles, Sabarmati, Salt Act of eighteen eighty-two)")
    if not 64<=tot<=78: errs.append(f"total words {tot}, must be 64 to 78")
    return errs,tot
def write_candidate(vendor,angle):
    tag=f"{vendor}:{angle}"
    for rnd in range(5):
        try:
            if vendor=="openai":
                if rnd==0: msgs=[{"role":"system","content":WRITER_SYS},{"role":"user","content":writer_prompt(angle)}]
                txt=gpt(msgs)
            else:
                txt=gem(writer_prompt(angle) if rnd==0 else prompt2,WRITER_SYS)
            c=json.loads(txt)
        except Exception as e:
            return dict(tag=tag,vendor=vendor,angle=angle,error=str(e)[:200])
        errs,tot=check_rules(c)
        if not errs: return dict(tag=tag,vendor=vendor,angle=angle,cand=c,words=tot,repairs=rnd)
        fb="Fix these problems and return the full JSON again:\n"+"\n".join(errs)
        if vendor=="openai": msgs+= [{"role":"assistant","content":txt},{"role":"user","content":fb}]
        else: prompt2=writer_prompt(angle)+"\n\nYour previous draft:\n"+txt+"\n\n"+fb
    return dict(tag=tag,vendor=vendor,angle=angle,cand=c,words=tot,rule_errors=errs,repairs=5)
def assemble(c):
    return [("L0","Nithya",c["L0"]),("L1","Nithya",c["L1"]),("L2","Gandhi",Q1),("L3","Nithya",c["L3"]),("L4","Gandhi",Q2),("L5","Nithya",c["L5"])]
FACT_SYS=("You are a strict fact-checker. Given the ALLOWED FACTS and the host lines of a script, decide for each host line whether every claim it makes is supported by the allowed facts. "
 "Only flag ADDED or WRONG claims: a date, number, place, person, cause, quantity or event that is not in the facts or contradicts them. Do NOT flag: omitted details, questions, rhetorical framing, the show name or the AI disclosure, or the asking of why salt was chosen. Return ONLY JSON: {\"L1\":{\"supported\":bool,\"issue\":str},\"L3\":{...},\"L5\":{...}}")
def fact_check(by_vendor,c):
    prompt="ALLOWED FACTS:\n"+json.dumps(FACTS,indent=1)+"\n\nHOST LINES:\n"+json.dumps({k:c[k] for k in ("L1","L3","L5")},indent=1)
    if by_vendor=="openai": return json.loads(gpt([{"role":"system","content":FACT_SYS},{"role":"user","content":prompt}]))
    return json.loads(gem(prompt,FACT_SYS))
RUBRIC=("Score each candidate script 1-10 on: informative (states clear, concrete, correct facts a listener learns), hook (the first five seconds grab attention), flow (sounds like a real conversation; the host lines lead naturally into the guest quotes), clarity (simple, speakable, no clumsy phrasing), "
 "fidelity (stays strictly with the facts, nothing invented), payoff (the closing line lands), tone (warm, curious, respectful, suits a tribute). Give one-sentence justification. Return ONLY JSON: {\"scores\":{\"C1\":{\"informative\":n,\"hook\":n,\"flow\":n,\"clarity\":n,\"fidelity\":n,\"payoff\":n,\"tone\":n,\"note\":str},...}}")
def judge(vendor,labeled):
    prompt="Candidates (anonymous):\n"+json.dumps(labeled,indent=1)+"\n\nGuest lines are fixed in all candidates: G1 and G2 (the Gandhi quotes). Judge only the host lines and how they fit around G1 and G2."
    if vendor=="openai": return json.loads(gpt([{"role":"system","content":RUBRIC},{"role":"user","content":prompt}]))["scores"]
    return json.loads(gem(prompt,RUBRIC))["scores"]
def main():
    jobs=[(v,a) for v in ("openai","google") for a in ANGLES]
    with cf.ThreadPoolExecutor(3) as ex: cands=list(ex.map(lambda x: write_candidate(*x),jobs))
    ok=[c for c in cands if "cand" in c and not c.get("rule_errors")]
    print("WRITTEN:",[(c["tag"],c.get("words"),c.get("repairs"),("ERR" if "error" in c else "")) for c in cands])
    # symmetric fact-check: both vendors check every candidate; hard fail only if both flag the same line
    def both(c):
        res={}
        for v in ("openai","google"):
            try: res[v]=fact_check(v,c["cand"])
            except Exception as e: res[v]=None
        return res
    with cf.ThreadPoolExecutor(4) as ex: allfc=list(ex.map(both,ok))
    for c,fc in zip(ok,allfc):
        c["fact_check"]=fc; flags={}
        for v,r in fc.items():
            if r:
                for k in ("L1","L3","L5"):
                    if not r[k]["supported"]: flags.setdefault(k,[]).append((v,r[k]["issue"][:140]))
        c["flags"]=flags; c["n_flags"]=sum(len(x) for x in flags.values()); c["facts_ok"]=not any(len(x)==2 for x in flags.values())
    gated=[c for c in ok if c["facts_ok"]]
    print("PASSED GATES:",[(c["tag"],c["n_flags"]) for c in gated],"| hard-failed:",[(c["tag"],c["flags"]) for c in ok if not c["facts_ok"]])
    if not gated: raise SystemExit("no candidate passed the gates")
    order=gated[:]; random.Random(7).shuffle(order)
    labeled={f"C{i+1}":dict(zip(["L0","L1","L2","L3","L4","L5"],[t for _,_,t in assemble(c["cand"])])) for i,c in enumerate(order)}
    label_of={f"C{i+1}":c["tag"] for i,c in enumerate(order)}
    scores={}
    with cf.ThreadPoolExecutor(2) as ex:
        futs={v:ex.submit(judge,v,labeled) for v in ("openai","google")}
        for v,f in futs.items(): scores[v]=f.result()
    crit=["informative","hook","flow","clarity","fidelity","payoff","tone"]
    rows=[]
    for lab,tag in label_of.items():
        per={v:sum(scores[v][lab][k] for k in crit)/len(crit) for v in scores}
        c=next(x for x in gated if x["tag"]==tag); other="google" if c["vendor"]=="openai" else "openai"
        rows.append(dict(tag=tag,label=lab,openai_judge=round(per["openai"],2),google_judge=round(per["google"],2),mean=round((per["openai"]+per["google"])/2-0.4*c["n_flags"],2),
                         cross_vendor_judge=round(per[other],2),words=c["words"],notes={v:scores[v][lab]["note"] for v in scores}))
    rows.sort(key=lambda r:(-r["mean"],r["words"]))
    win=next(x for x in gated if x["tag"]==rows[0]["tag"])
    print("\nRANKING"); 
    for r in rows: print(f"  {r['tag']:14} mean {r['mean']}  (openai judge {r['openai_judge']}, google judge {r['google_judge']}, cross-vendor {r['cross_vendor_judge']})  words {r['words']}")
    print("\nWINNER:",win["tag"],"|",win["cand"]["title"])
    for lid,who,t in assemble(win["cand"]): print(f"  {lid} {who:7} \"{t}\"")
    json.dump(dict(winner=win["tag"],title=win["cand"]["title"],lines=[dict(id=i,who=w,text=t) for i,w,t in assemble(win["cand"])],sources=win["cand"].get("sources"),ranking=rows,candidates=cands,facts=FACTS,quotes={"Q1":Q1,"Q2":Q2}),open("selection.json","w"),indent=1,default=str)
if __name__=="__main__": main()
