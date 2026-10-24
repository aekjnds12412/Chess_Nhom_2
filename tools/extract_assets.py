"""Slice the user-provided sprite sheet without redrawing the artwork."""
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[1]
sheet=Image.open(root/'assets/original.png').convert('RGBA')
# Each original sprite has its own occupied-pixel bounding box. A common
# baseline keeps the short pawns and taller kings correctly scaled on the board.
regions={
 'r':(394,50,440,126), 'n':(470,50,522,126),
 'b':(550,50,602,126), 'q':(630,48,680,126),
 'k':(710,48,759,126), 'p':(390,136,442,208),
}
for color,offset in [('w',0),('b',160)]:
    for kind,(x0,y0,x1,y1) in regions.items():
        sprite=sheet.crop((x0,y0+offset,x1,y1+offset))
        pixels=sprite.load()
        for y in range(sprite.height):
            for x in range(sprite.width):
                r,g,b,a=pixels[x,y]
                if r<10 and g<10 and b<10:
                    pixels[x,y]=(0,0,0,0)
        bounds=sprite.getbbox()
        if bounds:
            sprite=sprite.crop(bounds)
        frame=Image.new('RGBA',(64,80))
        frame.alpha_composite(sprite,((64-sprite.width)//2,74-sprite.height))
        frame.save(root/f'assets/{color}{kind}.png')
print('Extracted 12 sprites from assets/original.png')
