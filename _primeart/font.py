import struct, binascii
from collections import namedtuple
from PIL import Image, ImageOps

Level = namedtuple('Level', ['char', 'density_abs', 'density', 'rank'])

class Font:
    
    def __init__(self, img_file, dark=False, invert=False, normalize_r=0.3):
        img = Image.open(img_file, 'r')
        img = img.convert('L')
        self.width = img.size[0] // 36
        self.height = img.size[1]
        self.clip_min = 0
        self.clip_max = 255
        self.images = []
        self.images_alp = []
        self.invert = invert
        self.dark = dark
        self.images_rev = {}
        if dark: img = ImageOps.invert(img)
        img = img.convert('1')
        levels = []
        for i in range(0, 10):
            rect = (self.width * i, 0, self.width * (i+1), self.height)
            self.images.append(img.copy().crop(rect))
            self.images_rev[self.img2base64(self.images[i])] = i
            his = self.images[i].histogram()
            density_abs = .0
            for j in range(0, len(his)):
                density_abs += float(j * his[j])
            density_abs /= img.size[0]
            density_abs /= img.size[1]
            l = Level(i, density_abs, None, None)
            levels.append(l)
        levels = sorted(levels, key=lambda l: l.density_abs)
        min = levels[0].density_abs
        max = levels[9].density_abs
        self.levels = [ l._replace(density = (l.density_abs-min) / (max-min)) for l in levels ]
        for i in range(0, 10):
            l = self.levels[i]
            self.levels[i] = l._replace(
                rank = i,
                density = l.density * (1.0-normalize_r) + (float(i) / 9.0) * normalize_r
            )
        size = self.images[0].size
        self.aspect = size[0] / size[1]
        #
        for i in range(0, 26):
            rect = (self.width * (10+i), 0, self.width * (11+i), self.height)
            self.images_alp.append(img.copy().crop(rect))
    
    def img2base64(self, img, ox=0, oy=0):
        bin = bytes()
        for y in range(0, self.height):
            v = 0
            for x in range(0, self.width):
                v <<= 1
                if 128 <= img.getpixel((ox+x, oy+y)): v |= 1
            bin += struct.pack('B', v)
        return binascii.b2a_base64(bin)
    
    def guess(self, img, ox=0, oy=0):
        b64 = self.img2base64(img, ox, oy)
        if not b64 in self.images_rev: return None 
        return self.images_rev[b64]
    
    def dump(self):
        for l in self.levels:
            print('%d: %f' % (l.char, l.density))
    
    def char2density(self, char):
        for i in range(0, 10):
            l = self.levels[i]
            if l.char == char: return l.density
        return None
    
    def density2char(self, density):
        for i in range(0, 9):
            l = self.levels[i]
            h = self.levels[i+1]
            m = (l.density + h.density) / 2.0;
            if density < m: return l.char
        return self.levels[9].char
    
    def pixel2char(self, level):
        v = (level - self.clip_min) / (self.clip_max - self.clip_min)
        v = max(0.0, min(v, 1.0))
        if self.invert: v = 1.0 - v
        return self.density2char(v)
    
    def char2pixel(self, char):
        v = self.char2density(char)
        return v * (self.clip_max - self.clip_min) + self.clip_min
    
    def near_char(self, base, noise):
        if base<0 or 9<base: return None
        l_base = None
        for i in range(0, 10):
            l_base = self.levels[i]
            if l_base.char == base: break
        i = l_base.rank + noise
        if i<0 or 9<i: return None
        return self.levels[i].char
