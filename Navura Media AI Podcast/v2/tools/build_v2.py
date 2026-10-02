import json,subprocess,textwrap,re,os,sys
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LINES={l["id"]:l for l in json.load(open("v2/lines_v2.json"))}
RES=json.load(open("v2/clips/result.json"))
W,H,FPS=1280,720,24
def sh(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd)[:200]+"\n"+r.stderr[-600:])
    return r.stderr
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
def txtfile(name,text,width=None):
    if width: text="\n".join(textwrap.wrap(text,width))
    p=f"v2/build/{name}.txt"; open(p,"w").write(text); return p
def dt(textfile,size,y,x="(w-text_w)/2",color="white",box=0.5,alpha=1.0):
    return f"drawtext=fontfile={FONT}:textfile={textfile}:fontcolor={color}@{alpha}:fontsize={size}:box=1:boxcolor=black@{box}:boxborderw=7:line_spacing=5:x={x}:y={y}"
def gain_for(p,target=-21.0):
    err=sh(["ffmpeg","-i",p,"-af","volumedetect","-f","null","-"]); m=re.search(r"mean_volume: (-?[\d.]+) dB",err)
    return max(-8,min(8,target-float(m.group(1)))) if m else 0
def enc(extra_in,vf,af,out,t):
    sh(["ffmpeg","-y","-loglevel","error"]+extra_in+["-vf",vf,"-af",af,"-t",f"{t:.3f}","-r",str(FPS),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-ac","2","-b:a","160k",out])
def clip_segment(i):
    l=LINES[i]; r=RES[i]; raw=f"v2/clips/{i}.mp4"; ss=max(0,r["start"]-0.12); t=min(r["end"]+0.35,dur(raw))-ss; g=gain_for(raw)
    vf=f"scale={W}:{H},"+dt(txtfile(f"cap_{i}",l["text"],62),24,"h-th-70",box=0.45)
    if l["who"]=="Gandhi":
        vf+=","+dt(txtfile(f"lt1_{i}","Gandhi, AI-reimagined  |  AI-generated voice and image"),15,"22","22",box=0.4)+","+dt(txtfile(f"lt2_{i}",SOURCE[i]),13,"50","22",box=0.35)
    enc(["-ss",f"{ss:.3f}","-i",raw],vf,f"volume={g:.1f}dB,afade=t=in:d=0.03,afade=t=out:st={max(0,t-0.06):.3f}:d=0.06",f"v2/build/seg_{i}.mp4",t)
    return f"v2/build/seg_{i}.mp4",t
SOURCE={"L2":"Attributed to Gandhi, Salt March period, 1930","L4":"Gandhi, letter to Viceroy Lord Irwin, 2 March 1930"}
def still_pan(still,d,name):
    out=f"v2/build/{name}.mp4"
    vf=f"scale=1920:-2,zoompan=z='1+0.0005*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    sh(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate",str(FPS),"-t",f"{d:.3f}","-i",f"v2/kit/{still}.jpg","-vf",vf,"-r",str(FPS),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p",out]); return out
def card(name,d,lines):
    pan=still_pan("H0_hero_two_shot",d,name+"_pan"); vf=""
    for k,(t,size,y) in enumerate(lines):
        vf+=("," if vf else "")+dt(txtfile(f"{name}_{k}",t,80),size,str(y),box=0.4)
    enc(["-i",pan,"-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.004:sample_rate=48000"],vf,f"afade=t=in:d=0.2,afade=t=out:st={d-0.3}:d=0.3",f"v2/build/{name}.mp4",d)
    return f"v2/build/{name}.mp4",d
segs=[card("intro",1.4,[("The Salt March, 1930  |  Navura Media",28,110)])]
AVAIL=[i for i in ["L0","L1","L2","L3","L4","L5"] if RES.get(i,{}).get("ok")]
for i in AVAIL: segs.append(clip_segment(i))
segs.append(card("outro",2.6,[("AI-reimagined conversation. Gandhi's image and voice are AI-generated.",16,110),("Facts: Britannica, Wikipedia. Quotes: Gandhi, 1930.",14,140)]))
open("v2/build/concat.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p,_ in segs))
sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","v2/build/concat.txt","-c","copy","v2/build/joined.mp4"])
tag=txtfile("tag","AI-reimagined conversation  |  Navura Media")
sh(["ffmpeg","-y","-loglevel","error","-i","v2/build/joined.mp4","-vf",dt(tag,11,"h-th-16","20",box=0.35,alpha=0.85),"-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","v2/build/ep30_v2.mp4"])
print([(os.path.basename(p),round(t,2)) for p,t in segs],"total",round(sum(t for _,t in segs),1),"file",round(dur("v2/build/ep30_v2.mp4"),1))
