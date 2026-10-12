import sys, glob
from PIL import Image, ImageDraw
d=sys.argv[1]; out=sys.argv[2]; step=float(sys.argv[3])
files=sorted(glob.glob(d+"/g*.png"))
cols,rows=5,8
W,H=384,216
for s in range(0,len(files),cols*rows):
    chunk=files[s:s+cols*rows]
    sheet=Image.new("RGB",(cols*(W+4)+4,rows*(H+18)+4),(50,50,50)); dr=ImageDraw.Draw(sheet)
    for i,f in enumerate(chunk):
        x=4+(i%cols)*(W+4); y=4+(i//cols)*(H+18)
        sheet.paste(Image.open(f).convert("RGB").resize((W,H)),(x,y+14))
        idx=int(f.split("/g")[-1].split(".")[0])-1
        dr.text((x,y),f"{idx*step:.1f}s",fill=(255,255,255))
    sheet.save(f"{out}_{s//(cols*rows)}.png")
