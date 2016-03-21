#!/usr/bin/env python

import os, sys, random, math, getopt, json
from PIL import Image
from colorama import init
from _primeart.font import Font
from _primeart.canvas import Canvas
from _primeart.search_prime import add_noise, first_prime_factor

BLANK_DENSITY = 0.3
MAX_WIDTH = 15
NOISE_LIMIT = 2

used_primes = set()

def arr2num(a):
    v = 0
    for i in a: v = v*10 + i
    return v

def search_prime_line(line, y, canvas, allow_non_prime=False, ignore_factor_under=0):
    ff = 0
    x = 0
    w0 = len(line)
    count = 0
    result_pixel = []
    while 0 < len(line):
        w_candidates = []
        n = len(line)
        w = min(MAX_WIDTH, n)
        while 1 <= w:
            if (n <= w+1 or canvas.font.char2density(line[w+1]) <= BLANK_DENSITY) and w != n-1:
                score = math.sqrt(w)
                if w+1 < n:
                    score += int(round(3.0 * (BLANK_DENSITY - canvas.font.char2density(line[w+1])) / BLANK_DENSITY))
                for j in range(0, int(math.ceil(score))):
                    w_candidates.append(w)
            w -= 1
        if len(w_candidates)==0:
            for w in range(1, MAX_WIDTH+1):
                for j in range(0, int(math.ceil(math.sqrt(w)))):
                    w_candidates.append(w)
        ok = False
        while not ok:
            if 0 < len(w_candidates):
                w = random.choice(w_candidates)
            else:
                w += 1
                if n-3 <= w and w < n: w = n
                if n < w or MAX_WIDTH < w: return (None, None)
            w_candidates = [ v for v in w_candidates if v != w ]
            target = line[0:w]
            for r in add_noise(target, canvas.font, NOISE_LIMIT):
                if r[0]==0: continue
                rs = ''.join([ str(v) for v in r ])
                rn = arr2num(r)
                if rn in used_primes: continue
                factor = first_prime_factor(rn)
                if factor is None: continue
                if factor != rn and not allow_non_prime:
                    if ignore_factor_under <= factor:
                        canvas.print_back('%s is divisible by %d' % (rs, factor), len(rs)+1)
                        canvas.save()
                    continue
                used_primes.add(rn)
                canvas.print_back('%s ' % rs)
                canvas.print_commit('is prime', 0)
                canvas.save()
                canvas.save()
                canvas.save()
                canvas.save()
                canvas.save()
                result_pixel += [ canvas.font.char2pixel(v) for v in r ]
                result_pixel += [ 0 if canvas.font.dark else 255 ]
                count += 1
                x += len(rs) + 1
                ok = True
                break
        line = [] if n <= w else line[w+1:]
        ff = 1-ff
    return (count, result_pixel)

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def usage():
    print('USAGE: %s [options] <image file>' % sys.argv[0])
    print('    -h, --help: Show this help')
    print('    -d, --dark: Dark theme (white FG on black BG)')
    print('    -i, --invert: Invert image')
    print('    -e, --no-dither: Do not use dither')
    print('    -n, --allow-non-prime: Allow non-prime (to check draft)')
    print('    -w<width>, --width=<width>: Use fixed width (in chars)')
    print('    -P<file or dir>, --primes-in=<file or dir>: Prime numbers not to use (repeatable)')
    print('    -p<file>, --primes-out=<file>: Dump all used prime numbers')
    print('    -o<file>, --image-out=<file>: Create image')
    print('    -a<dir>, --animate-outdir=<dir>: Create animation')
    print('    -c<j>,<i>,<n>,<m> --crop=<j>,<i>,<n>,<m>:')
    print('        Divide source image into n*m segments and crop around (j,i)')
    print('        Example: -c 4,3,2,1')
    print('                 +---+---+---+---+')
    print('                 |   |   |   |   |')
    print('                 +---+---+---+---+')
    print('                 |   |   |2,1|   |')
    print('                 +---+---+---+---+')
    print('                 |   |   |   |   |')
    print('                 +---+---+---+---+')

if __name__ == "__main__":
    
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hdienm:w:P:p:o:a:c:',
            [
                'help',
                'dark',
                'invert',
                'no-dither',
                'allow-non-prime',
                'width=',
                'primes-in=',
                'primes-out=',
                'image-out=',
                'animate-outdir=',
                'crop='
            ]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)
    
    dark = False
    invert = False
    dither = True
    allow_non_prime = False
    width = os.get_terminal_size().columns - 1
    primes_in = []
    primes_out = None
    image_out = None
    animate_dir = None
    crop = None
    
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-d', '--dark'):
            dark = True
        elif o in ('-i', '--invert'):
            invert = True
        elif o in ('-e', '--no-dither'):
            dither = False
        elif o in ('-n', '--allow-non-prime'):
            allow_non_prime = True
        elif o in ('-w', '--width'):
            width = int(a)
        elif o in ('-P', '--primes-in'):
            if os.path.isdir(a):
                for f in os.listdir(a):
                    primes_in.append(os.path.join(a, f))
            else:
                primes_in.append(a)
        elif o in ('-p', '--primes-out'):
            primes_out = a
        elif o in ('-o', '--image-out'):
            image_out = a
        elif o in ('-a', '--animate-outdir'):
            animate_dir = a
        elif o in ('-c', '--crop'):
            crop = [ int(v) for v in a.split(',') ]
        else:
            assert False, 'unhandled option'
    
    if len(args) < 1:
        usage()
        sys.exit(1)
    
    img_file = args[0]
    if not dark: invert = not invert
    font = Font('font/LatArCyrHeb-16.png', dark, invert)
    
    primes_not_to_use = set()
    for infile in primes_in:
        with open(infile, 'r') as file:
            ps = set([ int(p) for p in file.readlines() if is_int(p) ])
            primes_not_to_use = primes_not_to_use.union(ps)
        used_primes = primes_not_to_use
    
    img = Image.open(img_file, 'r')
    img = img.convert('L')
    height = int(round(font.aspect * width * img.size[1] / img.size[0]))
    img = img.resize((width, height), Image.BICUBIC)
    if crop is not None:
        width  //= crop[2]
        height //= crop[3]
        xs = width  * crop[0]
        ys = height * crop[1]
        img = img.crop((xs, ys, xs+width, ys+height))
    
    init()
    print('-' * width)
    canvas = Canvas(font, width, height, animate_dir)
    
    for y in range(0, img.size[1]):
        line = []
        for x in range(0, img.size[0]):
            num = font.pixel2char(img.getpixel((x, y)))
            line.append(num)
        count = None
        pixel = None
        used_primes_save = used_primes.copy()
        sequence_save = canvas.sequence
        while count is None:
            used_primes = used_primes_save
            canvas.sequence = sequence_save
            (count, pixel) = search_prime_line(line, y, canvas, allow_non_prime, 5+len(used_primes)//10)
            if count is None: canvas.cancel_line()
        canvas.print_back('')
        canvas.new_line()
        
        # Dither algorhythm based on https://github.com/noopkat/floyd-steinberg
        if dither and y < height - 1:
            for x in range(0, width):
                e = (img.getpixel((x, y)) - pixel[x]) / 23.0
                # right neighbor += e * 7.0
                if 0 < x:
                    img.putpixel((x-1, y+1), max(0, min(img.getpixel((x-1, y+1)) + round(e * 3.0), 255)))
                if True:
                    img.putpixel((x  , y+1), max(0, min(img.getpixel((x  , y+1)) + round(e * 5.0), 255)))
                if x < img.size[0] - 1:
                    img.putpixel((x+1, y+1), max(0, min(img.getpixel((x+1, y+1)) + round(e      ), 255)))

    used_primes = used_primes.difference(primes_not_to_use)

    if image_out is not None:
        canvas.save_total(image_out)
    
    if primes_out is not None:
        with open(primes_out, 'w') as file:
            for p in sorted(used_primes): file.write('%d\n' % p)
    
    print('-' * width)
    print('Prime count: %d' % len(used_primes))
    print('Min prime: %d' % min(used_primes))
    print('Max prime: %d' % max(used_primes))
