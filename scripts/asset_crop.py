"""Crop icon exactly, without edge detection, thresholding, masks or inpainting."""
import argparse
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('--box',nargs=4,type=int,required=True,metavar=('X','Y','W','H'));p.add_argument('--out',required=True);a=p.parse_args()
im=Image.open(a.image).convert('RGBA');x,y,w,h=a.box
if w<=0 or h<=0 or x<0 or y<0 or x+w>im.width or y+h>im.height:raise SystemExit('crop box outside source')
im.crop((x,y,x+w,y+h)).save(a.out);print(a.out)
