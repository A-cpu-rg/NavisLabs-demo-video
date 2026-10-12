import json, subprocess, sys, numpy as np
ROOT="/Users/abhishekmeena/Desktop/Navis-Launch-Film"
vid=sys.argv[1]
FF="/opt/homebrew/bin/ffmpeg"; FP="/opt/homebrew/bin/ffprobe"
pr=json.loads(subprocess.run([FP,"-v","error","-show_streams","-show_format","-of","json",vid],capture_output=True,text=True).stdout)
for st in pr["streams"]:
    print(st["codec_type"], st.get("codec_name"), st.get("width"), st.get("height"), st.get("r_frame_rate"), st.get("nb_frames"), st.get("duration"), st.get("sample_rate"))
print("format duration", pr["format"]["duration"], "size", int(pr["format"]["size"])//1e6, "MB")
# luma per frame
out=subprocess.run([FF,"-v","error","-i",vid,"-vf","scale=480:270,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-","-f","null","-"],capture_output=True,text=True).stdout
y=[float(l.split("=")[1]) for l in out.splitlines() if "YAVG" in l]
y=np.array(y); print("frames analysed", len(y))
spec=json.load(open(f"{ROOT}/navislabs_v5_film_spec.json"))
cuts=set()
for s in spec["scenes"]: cuts.add(round(s["from_s"]*30))
black=[i for i,v in enumerate(y) if v<17]
# group black runs
runs=[];
for i in black:
    if runs and i==runs[-1][1]+1: runs[-1][1]=i
    else: runs.append([i,i])
print("near-black runs (frame, s):", [(a,b,round(a/30,2),round(b/30,2)) for a,b in runs])
d=np.abs(np.diff(y))
big=[(i+1,round((i+1)/30,2),round(y[i],1),round(y[i+1],1)) for i in np.where(d>18)[0]]
print("luma jumps >18:", big)
# audio
raw=subprocess.run([FF,"-v","error","-i",vid,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout
a=np.frombuffer(raw,dtype=np.float32)
# Peaks per channel (a mono downmix can sum above 1.0 without any channel clipping).
st=np.frombuffer(subprocess.run([FF,"-v","error","-i",vid,"-ac","2","-ar","48000","-f","f32le","-"],capture_output=True).stdout,dtype=np.float32)
peak=float(np.abs(st).max()); clipped=int((np.abs(st)>=0.999).sum())
print("audio seconds", round(len(a)/48000,3), "peak (per channel)", round(peak,3), "clipped samples", clipped)
def rms(t0,t1):
    seg=a[int(t0*48000):int(t1*48000)]; return 20*np.log10(np.sqrt(np.mean(seg**2))+1e-9)
vo=json.load(open(f"{ROOT}/navislabs_v5_voiceover_screen_map.json"))
lines=vo["voiceover"]
vo_rms={}
for l in lines:
    s=l.get("start_s"); e=l.get("end_s")
    vo_rms[l["id"]]=round(float(rms(s,e)),1)
    print(l["id"], s, e, "rms", vo_rms[l["id"]], "dB", "| gap after", round(rms(e+0.05, e+0.25),1))
ln=subprocess.run([FF,"-v","info","-i",vid,"-af","loudnorm=print_format=json","-f","null","-"],capture_output=True,text=True).stderr
j=ln[ln.rfind("{"):ln.rfind("}")+1]; d2=json.loads(j); print("integrated LUFS", d2["input_i"], "true peak", d2["input_tp"], "LRA", d2["input_lra"])
# Optional: write a JSON summary (used by scripts/build-v5-audit.py and the audio pack).
if len(sys.argv) > 2:
    v=[st for st in pr["streams"] if st["codec_type"]=="video"][0]
    summary={
        "file": vid, "size_mb": round(int(pr["format"]["size"])/1e6,1), "duration_s": float(pr["format"]["duration"]),
        "video": {"codec": v.get("codec_name"), "width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"), "frames": len(y), "pix_fmt": v.get("pix_fmt"), "color_space": v.get("color_space")},
        "near_black_runs_s": [[round(float(a)/30,2), round(float(b)/30,2)] for a,b in runs],
        "luma_jumps": [[int(f), float(t)] for f, t, _, _ in big],
        "audio": {"seconds": round(len(a)/48000,3), "peak": round(peak,3), "clipped_samples": clipped,
                  "integrated_lufs": float(d2["input_i"]), "true_peak_dbtp": float(d2["input_tp"]), "lra": float(d2["input_lra"])},
        "vo_rms_db": vo_rms,
        "vo_silent_lines": [k for k, r in vo_rms.items() if r < -45],
    }
    json.dump(summary, open(sys.argv[2], "w"), indent=1)
    print("wrote", sys.argv[2])
