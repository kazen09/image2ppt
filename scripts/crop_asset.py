import argparse
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--src',required=True);p.add_argument('--out',required=True);p.add_argument('--box',type=int,nargs=4,metavar=('X','Y','W','H'),required=True);p.add_argument('--padding',type=int,default=0);a=p.parse_args()
im=Image.open(a.src); x,y,w,h=a.box; t=a.padding
im.crop((max(0,x-t),max(0,y-t),min(im.width,x+w+t),min(im.height,y+h+t))).save(a.out)
print(a.out)
