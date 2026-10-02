import sys,os,subprocess,json,textwrap,re; sys.path.insert(0,"/tmp/claude-0/-home-user-Built-Your-Own-Career-X/f6804c5a-1a67-58a8-a0a2-9046fc10ad41/scratchpad/t")
from common import *
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def sh(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(" ".join(c)[:160]+"\n"+r.stderr[-500:])
    return r.stderr
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
def tf(n,t,w=None):
    if w: t="\n".join(textwrap.wrap(t,w))
    p=f"v2/ten/{n}.txt"; open(p,"w").write(t); return p
def dt(f,size,y,x="(w-text_w)/2",box=0.45,alpha=1.0): return f"drawtext=fontfile={FONT}:textfile={f}:fontcolor=white@{alpha}:fontsize={size}:box=1:boxcolor=black@{box}:boxborderw=7:x={x}:y={y}"
# Gandhi: raw clip -> 24 fps interpolated, our AI voice muxed
sh(["ffmpeg","-y","-loglevel","error","-i","v2/ten/gandhi_raw.mp4","-i","ep30/gandhi_audio/L2_final.wav","-map","0:v","-map","1:a","-vf","scale=1280:720:flags=lanczos,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","v2/ten/gandhi_raw_24fps_with_voice.mp4"])
# Nithya: trim to speech end
sh(["ffmpeg","-y","-loglevel","error","-i","v2/ten/nithya.mp4","-vn","-ac","1","-ar","16000","v2/ten/nithya.wav"])
with open("v2/ten/nithya.wav","rb") as f:
    tr=requests.post("https://api.openai.com/v1/audio/transcriptions",data={"model":"whisper-1","response_format":"verbose_json","timestamp_granularities[]":"word"},files={"file":("n.wav",f,"audio/wav")},timeout=120).json()
w=tr.get("words",[]); ss=max(0,w[0]["start"]-0.12); end=min(dur("v2/ten/nithya.mp4"),w[-1]["end"]+0.35)
print("nithya says:",tr.get("text"),"| speech",round(w[0]["start"],2),"-",round(w[-1]["end"],2))
def seg(inp,out,start,length,caption,lower=None):
    vf="scale=1280:720,"+dt(tf("cap_"+out.split('/')[-1],caption,62),24,"h-th-70")
    if lower: vf+=","+dt(tf("lt_"+out.split('/')[-1],lower),15,"22","22",box=0.4)
    sh(["ffmpeg","-y","-loglevel","error","-ss",f"{start:.3f}","-i",inp,"-vf",vf,"-t",f"{length:.3f}","-r","24","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-ac","2","-b:a","192k","-af","afade=t=in:d=0.03,afade=t=out:st="+f"{max(0,length-0.06):.3f}:d=0.06",out])
seg("v2/ten/nithya.mp4","v2/ten/seg_n.mp4",ss,end-ss,"Why choose salt for this march?")
seg("v2/ten/gandhi_raw_24fps_with_voice.mp4","v2/ten/seg_g.mp4",0,dur("v2/ten/gandhi_raw_24fps_with_voice.mp4"),"Next to air and water, salt is perhaps the greatest necessity of life.","Gandhi, AI-reimagined  |  AI-generated voice and image")
open("v2/ten/list.txt","w").write(f"file '{os.path.abspath('v2/ten/seg_n.mp4')}'\nfile '{os.path.abspath('v2/ten/seg_g.mp4')}'\n")
sh(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","v2/ten/list.txt","-c","copy","v2/ten/joined.mp4"])
sh(["ffmpeg","-y","-loglevel","error","-i","v2/ten/joined.mp4","-vf",dt(tf("tag","AI-reimagined conversation  |  Navura Media"),11,"h-th-16","20",box=0.35,alpha=0.85),"-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","v2/ten/ten_sec_final.mp4"])
print("final",round(dur("v2/ten/ten_sec_final.mp4"),1),"s")
