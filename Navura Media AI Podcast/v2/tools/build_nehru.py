import json,subprocess,textwrap,re,os
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="v2/ep_nehru/build"; C="v2/ep_nehru/clips"
LINES={l["id"]:l for l in json.load(open("v2/ep_nehru/lines_with_prompts.json"))}
RES=json.load(open(f"{C}/result.json"))
W,H,FPS=1280,720,24
def sh(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(" ".join(c)[:200]+"\n"+r.stderr[-500:])
    return r.stderr
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
def tf(n,t,w=None):
    if w: t="\n".join(textwrap.wrap(t,w))
    p=f"{B}/{n}.txt"; open(p,"w").write(t); return p
def dt(f,size,y,x="(w-text_w)/2",box=0.5,alpha=1.0,en=None):
    s=f"drawtext=fontfile={FONT}:textfile={f}:fontcolor=white@{alpha}:fontsize={size}:box=1:boxcolor=black@{box}:boxborderw=7:line_spacing=5:x={x}:y={y}"
    if en: s+=f":enable='between(t,{en[0]},{en[1]})'"
    return s
def gain(p,target=-21.0):
    e=sh(["ffmpeg","-i",p,"-af","volumedetect","-f","null","-"]); m=re.search(r"mean_volume: (-?[\d.]+) dB",e)
    return max(-8,min(8,target-float(m.group(1)))) if m else 0
def enc(inp,vf,af,out,t):
    sh(["ffmpeg","-y","-loglevel","error"]+inp+["-vf",vf,"-af",af,"-t",f"{t:.3f}","-r",str(FPS),"-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-ac","2","-b:a","192k",out])
def pan(still,d,name,zoom=0.0006):
    out=f"{B}/{name}.mp4"
    sh(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate",str(FPS),"-t",f"{d:.3f}","-i",still,"-vf",f"scale=1920:-2,zoompan=z='1+{zoom}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p","-r",str(FPS),"-c:v","libx264","-crf","17","-pix_fmt","yuv420p",out]); return out
LT="Jawaharlal Nehru, AI-reimagined  |  AI-generated voice and image"
SRC="Attributed to Nehru"
def clip(i,lower=False,cutaway=None):
    """cutaway=(still, seconds): the last N seconds show a reaction shot while this speaker's voice continues."""
    l=LINES[i]; r=RES[i]; raw=f"{C}/{i}.mp4"; ss=max(0,r["start"]-0.12); t=min(r["end"]+0.35,dur(raw))-ss; g=gain(raw)
    cap=dt(tf(f"cap_{i}",l["text"],62),24,"h-th-70",box=0.45)
    af=f"volume={g:.1f}dB,afade=t=in:d=0.03,afade=t=out:st={max(0,t-0.06):.3f}:d=0.06"
    ex=""
    if lower: ex=","+dt(tf(f"lt1_{i}",LT),15,"22","22",box=0.4)+","+dt(tf(f"lt2_{i}",SRC),13,"50","22",box=0.35)
    if not cutaway:
        enc(["-ss",f"{ss:.3f}","-i",raw],f"scale={W}:{H},"+cap+ex,af,f"{B}/seg_{i}.mp4",t); return f"{B}/seg_{i}.mp4",t
    still,cs=cutaway; main=t-cs
    enc(["-ss",f"{ss:.3f}","-i",raw],f"scale={W}:{H}",af,f"{B}/a_{i}.mp4",t)                                    # full audio, clip video
    sh(["ffmpeg","-y","-loglevel","error","-i",f"{B}/a_{i}.mp4","-t",f"{main:.3f}","-vf",f"scale={W}:{H}","-an","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-r",str(FPS),f"{B}/v1_{i}.mp4"])
    v2=pan(still,cs,f"v2_{i}")
    open(f"{B}/l_{i}.txt","w").write(f"file '{os.path.abspath(B)}/v1_{i}.mp4'\nfile '{os.path.abspath(v2)}'\n")
    sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{B}/l_{i}.txt","-c","copy",f"{B}/vv_{i}.mp4"])
    sh(["ffmpeg","-y","-loglevel","error","-i",f"{B}/vv_{i}.mp4","-i",f"{B}/a_{i}.mp4","-map","0:v","-map","1:a","-vf",cap+ex,"-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest",f"{B}/seg_{i}.mp4"])
    return f"{B}/seg_{i}.mp4",t
def card(name,still,d,text,size=16):
    p=pan(still,d,name+"_pan",0.0005)
    enc(["-i",p,"-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.004:sample_rate=48000"],dt(tf(name,text,80),size,"110",box=0.4),f"afade=t=in:d=0.2,afade=t=out:st={max(0.1,d-0.3):.2f}:d=0.3",f"{B}/{name}.mp4",d)
    return f"{B}/{name}.mp4",d
K="v2/nehru_kit"
segs=[card("intro",f"{K}/N1_two_shot.jpg",1.5,"Children's Day  |  Navura Media",26)]
segs.append(clip("L0")); segs.append(clip("L1"))
segs.append(clip("L4",lower=True,cutaway=(f"{K}/N4_ots_to_nithya.jpg",1.6)))
segs.append(clip("L5"))
segs.append(card("outro",f"{K}/N1_two_shot.jpg",1.8,"AI-reimagined conversation. Nehru's image and voice are AI-generated. Quote attributed to Jawaharlal Nehru.",13))
open(f"{B}/concat.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p,_ in segs))
sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{B}/concat.txt","-c","copy",f"{B}/joined.mp4"])
sh(["ffmpeg","-y","-loglevel","error","-i",f"{B}/joined.mp4","-vf",dt(tf("tag","AI-reimagined conversation  |  Navura Media"),11,"h-th-16","20",box=0.35,alpha=0.85),"-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",f"{B}/nehru_childrens_day.mp4"])
print([(os.path.basename(p),round(t,2)) for p,t in segs],"total",round(sum(t for _,t in segs),1),"s; file",round(dur(f"{B}/nehru_childrens_day.mp4"),1),"s")
