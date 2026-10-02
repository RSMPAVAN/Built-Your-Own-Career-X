import json
sel=json.load(open("selection.json"))
FRAME={"L0":"S02_nithya_close","L1":"S01_nithya_medium","L2":"S04_gandhi_close","L3":"S02_nithya_close","L4":"S03_gandhi_medium","L5":"S01_nithya_medium"}
def secs(who,text):
    pace=2.6 if who=="Nithya" else 2.4
    need=len(text.split())/pace+0.5
    return next(c for c in (4,6,8) if c>=need)
LINES=[dict(id=l["id"],who=l["who"],text=l["text"],frame=FRAME[l["id"]],seconds=secs(l["who"],l["text"])) for l in sel["lines"]]
if __name__=="__main__":
    for l in LINES: print(l["id"],l["who"],l["seconds"],"s",l["frame"],"|",l["text"])
    print("clip seconds",sum(l["seconds"] for l in LINES),"| winner",sel["winner"])
