#!/usr/bin/env python

import os, sys, math, getopt
from PIL import Image
from _primeart.font import Font
from _primeart.search_prime import first_prime_factor

def usage():
    print('USAGE: %s [options] <image file>' % sys.argv[0])
    print('    -h, --help: Show this help')
    print('    -d, --dark: Dark theme (white FG on black BG)')
    print('    -i, --invert: Invert image')
    print('    -p<file>, --primes-out=<file>: Dump all used prime numbers')
    print('    -o<file>, --text-out=<file>: Output text file')

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hdio:p:',
            [
                'help',
                'dark',
                'invert',
                'text-out=',
                'primes-out='
            ]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    dark = False
    invert = False
    text_out = None
    primes_out = None
    
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-d', '--dark'):
            dark = True
        elif o in ('-i', '--invert'):
            invert = True
        elif o in ('-o', '--text-out'):
            text_out = a
        elif o in ('-p', '--primes-out'):
            primes_out = a
        else:
            assert False, 'unhandled option'

    if len(args) < 1:
        usage()
        sys.exit(1)

    img_file = args[0]

    font = Font('font/LatArCyrHeb-16.png', dark, invert)
    img = Image.open(img_file, 'r')
    img = img.convert('L')

    text = []
    primes = []
    for y in range(0, img.size[1], font.height):
        s = ''
        for x in range(0, img.size[0], font.width):
            i = font.guess(img, x, y)
            s += (' ' if i is None else str(i))
        for ps in s.split(' '):
            if ps == '': continue
            p = int(ps)
            f = first_prime_factor(p)
            if f==p:
                print('%d is prime' % (p))
            else:
                print('ERROR: %d is divisible by ' % (p, f))
                sys.exit(2)
            primes.append(ps)
        text.append(s)
        if len(primes) == 0:
            print('Something bad. Please retry with the other options.')
            sys.exit(3)

    if text_out is not None:
        text.append('')
        with open(text_out, 'w') as file:
            file.write("\n".join(text))

    if primes_out is not None:
        primes.append('')
        with open(primes_out, 'w') as file:
            file.write("\n".join(primes))
