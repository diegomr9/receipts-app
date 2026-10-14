# Creates sample receipt images and uploads them via the running app (tests OCR + upload).
import requests, sys
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 28) if __import__("os").path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf") else ImageFont.load_default()
samples = [("SAMPLE - Cafe Central Restaurant", "2026-10-02", ["Lunch menu x2   31.00","Coffee          4.50"], "TOTAL EUR 35.50"),
           ("SAMPLE - City Taxi Co", "2026-10-05", ["Airport ride   42.00"], "TOTAL EUR 42.00"),
           ("SAMPLE - Grand Hotel Madrid", "2026-10-07", ["1 night room  120.00","City tax        3.00"], "TOTAL EUR 123.00")]
for i,(m,d,items,tot) in enumerate(samples):
    im = Image.new("RGB",(700,520),"white"); dr = ImageDraw.Draw(im); y=30
    for line in [m, "Date: "+d, "-"*30]+items+["-"*30, tot]:
        dr.text((30,y), line, fill="black", font=F); y+=50
    p=f"/tmp/sample{i}.png"; im.save(p)
    requests.post("http://localhost:8000/upload", files={"file":(f"sample{i}.png",open(p,"rb"),"image/png")})
print("seeded")
