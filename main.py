import io
import random
from PIL import Image
import os
import glob

# PARAMS
inputfile = "jude-beck--PzyGU3QPJU-unsplash.jpg"  # filename of input image. supports any filetype PIL does.
outputfile = "out.mp4"  # filename of output video. supports any filetype ffmpeg does (gif too!)
length = 5  # seconds
fps = 15  # frames per second
randomchance = 0.05  # % chance to corrupt byte (0-100) Set lower for bigger images and higher for smaller images.
firstframeuc = True  # if true, the first frame is a carbon copy of the input image. good for discord pfps
size = 512  # if not -1, this caps the width/height of the input image

randomchance /= 100  # % to 0-1
im = Image.open(inputfile).convert("RGB")  # PIL no likey png
if size != -1:
    im.thumbnail((size, size), Image.ANTIALIAS)  # idk apparently this caps the size or maybe forces it idc
stream = io.BytesIO()
im.save(stream, format="JPEG")  # save image as jpeg to bytes

stream.seek(0)
imagebytes = stream.read()  # read stream thing to var
# imagebytes = list(stream.getvalue())

# clear out folder
files = glob.glob('frames/*')
for f in files:
    os.remove(f)
try:  # too lazy to make a better solution ik this SUCK
    os.mkdir("frames")
except:
    pass
if firstframeuc:  # savbe first frame since we can now
    im.save("frames/frame0.jpg", format="JPEG")
frames = length * fps
for frame in range(frames):
    corrupting = True
    while corrupting:  # easy way to do a retry loop if corruption breaks the jpeg
        try:  # if image is invalid, PIL throws an error.
            cimagebytes = bytearray(imagebytes)  # easiest to deal with
            for i, byte in enumerate(imagebytes):
                if random.random() < randomchance:  # random.random() is 0-1
                    # random mode
                    rb = random.randint(0, 255)  # get random byte
                    # relative mode
                    # rb = (cimagebytes[i] + random.randint(-20, 20)) % 255
                    # relative mode capped
                    # rb = min(max(cimagebytes[i] + random.randint(-1, 1),0),255)
                    # print(f"Changing byte {i} from {cimagebytes[i]} to {rb}")
                    cimagebytes[i] = rb  # set corrupted byte
            imc = Image.open(io.BytesIO(cimagebytes), formats=["JPEG", "PNG"])  # import corrupted jpeg to PIL image
            # an error will be thrown if image is invalid
            imc.save(f"frames/frame{frame + 1 if firstframeuc else frame}.jpg")  # save frame
            print(f"Successfully corrupted frame {frame}/{frames} ({round(frame / frames * 100, 1)}%)")
            corrupting = False  # this frame was successful, exit the while loop and go onto the next frame
        except Exception as e:  # better for catch-all in case i fuck shit up in changing code
            print(f"Error in frame {frame}: {e}")
            pass
# convert image sequence to final output. the weird -vf this is because mp4 has to be divisible by 2 and apparently that
# makes it divisible by 2? idk
os.system(f"ffmpeg -r {fps} -i frames/frame%d.jpg -vf scale=-2:min(1080\,if(mod(ih\,2)\,ih-1\,ih)) -y {outputfile}")
