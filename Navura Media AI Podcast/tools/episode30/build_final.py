import json,subprocess,textwrap,re,os
R="/home/user/Built-Your-Own-Career-X/Navura Media AI Podcast"; KIT=f"{R}/assets/gandhi_kit"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FONTB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
L={l["id"]:l for l in json.load(open("lines_with_prompts.json"))}
RES=json.load(open("clips2/result.json"))
W,H,FPS=1280,720,24
def sh(cmd): 
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd)[:200]+"\n"+r.stderr[-600:])
    return r.stderr
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
def txtfile(name,text,width=None):
    if width: text="\n".join(textwrap.wrap(text,width))
    p=f"build/{name}.txt"; open(p,"w").write(text); return p
def dt(textfile,size,y,x="(w-text_w)/2",color="white",box=0.55,bold=False,t0=None,t1=None):
    s=f"drawtext=fontfile={FONTB if bold else FONT}:textfile={textfile}:fontcolor={color}:fontsize={size}:box=1:boxcolor=black@{box}:boxborderw=10:line_spacing=6:x={x}:y={y}"
    if t0 is not None: s+=f":enable='between(t,{t0},{t1})'"
    return s
def gain_for(p,target=-21.0):
    err=sh(["ffmpeg","-i",p,"-af","volumedetect","-f","null","-"]); m=re.search(r"mean_volume: (-?[\d.]+) dB",err)
    return max(-8,min(8,target-float(m.group(1)))) if m else 0
def finish(vsrc_args,vf,audio_in,audio_filter,out,tdur):
    cmd=["ffmpeg","-y","-loglevel","error"]+vsrc_args+audio_in+["-vf",vf,"-af",audio_filter,"-t",f"{tdur:.3f}","-r",str(FPS),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-ac","2","-b:a","160k",out]
    sh(cmd)
def clip_segment(i):
    l=L[i]; r=RES[i]; ss=max(0,r["start"]-0.15); end=r["end"]+0.35; t=min(end-ss,l["seconds"]-ss)
    raw=f"clips2/{i}.mp4"; g=gain_for(raw)
    cap=txtfile(f"cap_{i}",l["text"],54)
    vf=f"scale={W}:{H},"+dt(cap,30,"h-th-92")
    finish(["-ss",f"{ss:.3f}","-i",raw],vf,[],f"volume={g:.1f}dB,afade=t=in:d=0.03,afade=t=out:st={t-0.05:.3f}:d=0.05",f"build/seg_{i}.mp4",t)
    return f"build/seg_{i}.mp4",t
def still_pan(still,d,idx,name):
    out=f"build/{name}_{idx}.mp4"
    vf=f"scale=1920:-2,zoompan=z='1+0.00055*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    sh(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate",str(FPS),"-t",f"{d:.3f}","-i",f"{KIT}/{still}.jpg","-vf",vf,"-r",str(FPS),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p",out]); return out
def gandhi_segment(i,stills,lower,src):
    l=L[i]; wav=f"gandhi_audio/{i}_final.wav"; a=dur(wav); total=a+0.45
    ds=[round(total*f,3) for f in stills[1]]; ds[-1]=round(total-sum(ds[:-1]),3)
    parts=[still_pan(n,d,k,f"g{i}") for k,(n,d) in enumerate(zip(stills[0],ds))]
    open(f"build/list_{i}.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"build/list_{i}.txt","-c","copy",f"build/gv_{i}.mp4"])
    cap=txtfile(f"cap_{i}",l["text"],54); lt1=txtfile(f"lt1_{i}",lower); lt2=txtfile(f"lt2_{i}",src,70)
    vf=dt(lt1,22,"28","28",bold=True)+","+dt(lt2,18,"72","28",box=0.45)+","+dt(cap,30,"h-th-92")
    g=gain_for(wav)
    finish(["-i",f"build/gv_{i}.mp4"],vf,["-i",wav],f"volume={g:.1f}dB,apad,afade=t=in:d=0.04,afade=t=out:st={total-0.08:.3f}:d=0.08",f"build/seg_{i}.mp4",total)
    return f"build/seg_{i}.mp4",total
def card(name,still,d,lines):
    pan=still_pan(still,d,0,name); fs=[]; y=H//2-90
    vf=""
    for k,(t,size,bold) in enumerate(lines):
        p=txtfile(f"{name}_{k}",t,60); vf+=("," if vf else "")+dt(p,size,f"{int(H*0.28)+k*58}",bold=bold)
    sh(["ffmpeg","-y","-loglevel","error","-i",pan,"-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.004:sample_rate=48000","-vf",vf,"-af",f"afade=t=in:d=0.2,afade=t=out:st={d-0.3}:d=0.3","-t",f"{d}","-r",str(FPS),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-ac","2",f"build/{name}.mp4"])
    return f"build/{name}.mp4",d
segs=[]
segs.append(card("intro","S10_empty_wide",1.2,[("The Salt March, 1930",44,True),("Navura Media",28,False)]))
segs.append(clip_segment("L0")); segs.append(clip_segment("L1"))
segs.append(gandhi_segment("L2",(["S04_gandhi_close","S06_ots_to_nithya"],[0.6,0.4]),"Gandhi, AI-reimagined  |  AI-generated voice","Attributed to Gandhi, Salt March period, 1930"))
segs.append(clip_segment("L3"))
segs.append(gandhi_segment("L4",(["S03_gandhi_medium","S02_nithya_close"],[0.62,0.38]),"Gandhi, AI-reimagined  |  AI-generated voice","Gandhi, letter to Viceroy Lord Irwin, 2 March 1930"))
segs.append(clip_segment("L5"))
segs.append(card("outro","S09_cutaway_window",3.0,[("AI-reimagined conversation",36,True),("Gandhi's image and voice are AI-generated.",24,False),("Facts: Britannica, Wikipedia. Quotes: Gandhi, 1930.",22,False)]))
open("build/concat.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p,_ in segs))
sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","build/concat.txt","-c","copy","build/joined.mp4"])
tag=txtfile("tag","AI-reimagined conversation  |  Navura Media")
vf=dt(tag,20,"h-th-26","26",box=0.45)
sh(["ffmpeg","-y","-loglevel","error","-i","build/joined.mp4","-vf",vf,"-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","build/ep30_final.mp4"])
print("segments:",[(os.path.basename(p),round(t,2)) for p,t in segs]); print("total",round(sum(t for _,t in segs),2),"s; file",dur("build/ep30_final.mp4"),"s")
