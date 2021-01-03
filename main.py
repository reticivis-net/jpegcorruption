import io
import random
from PIL import Image
import os
import glob

# PARAMS
randomchance = 0.05  # % chance to corrupt byte
length = 5  # seconds
fps = 15  # frames per second
filename = "lotuspfp.png"  # filename of image
size = 512, 512  # max size of image (smaller means faster but also higher % required to corrupt well)

randomchance /= 100
im = Image.open(filename).convert("RGB")
im.thumbnail(size, Image.ANTIALIAS)
stream = io.BytesIO()
im.save(stream, format="JPEG")

stream.seek(0)
imagebytes = stream.read()
# imagebytes = list(stream.getvalue())
files = glob.glob('frames/*')
for f in files:
    os.remove(f)
try:
    os.mkdir("frames")
except:
    pass
im.save("frames/frame0.jpg", format="JPEG")
frames = length * fps
for frame in range(frames):
    result = None
    while result is None:
        try:
            cimagebytes = bytearray(imagebytes)
            for i, byte in enumerate(imagebytes):
                if random.random() < randomchance:
                    # random mode
                    rb = random.randint(0, 255)
                    # relative mode
                    # rb = (cimagebytes[i] + random.randint(-20, 20)) % 255
                    # relative mode capped
                    # rb = min(max(cimagebytes[i] + random.randint(-1, 1),0),255)
                    # print(f"Changing byte {i} from {cimagebytes[i]} to {rb}")
                    cimagebytes[i] = rb
            # cimagebytes = bytes(cimagebytes)
            imc = Image.open(io.BytesIO(cimagebytes), formats=["JPEG", "PNG"])
            imc.save(f"frames/frame{frame+1}.jpg")
            print(f"Successfully corrupted frame {frame}/{frames} ({round(frame / frames * 100, 1)}%)")
            result = True
        except Exception as e:
            print(f"Error in frame {frame}: {e}")
            pass
os.system(
    f"ffmpeg -r {fps} -i frames/frame%d.jpg -vf scale=-2:min(1080\,if(mod(ih\,2)\,ih-1\,ih)) -y out.gif")
