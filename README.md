# Prime Number Art

Converts an image into ASCII art using prime numbers only.

https://gist.githubusercontent.com/but80/b38f97c77a971769e9f0/raw/d82f59b9d7515d3eb19c1de1f6141cf715748b21/shiki.txt
http://www.nicovideo.jp/watch/sm28470240

## Requirements

- Python 3.4

## Usage

```bash
cd primeart
virtualenv .                # If necessary
source bin/activate         #   on Mac/Un*x
.\Scripts\activate          #   on Windows
pip install -r packages.txt
python primeart.py
```

## Options

```
USAGE: primeart.py [options] <image file>
    -h, --help: Show this help
    -d, --dark: Dark theme (white FG on black BG)
    -i, --invert: Invert image
    -e, --no-dither: Do not use dither
    -n, --allow-non-prime: Allow non-prime (to check draft)
    -w<width>, --width=<width>: Use fixed width (in chars)
    -P<file or dir>, --primes-in=<file or dir>: Prime numbers not to use (repeatable)
    -p<file>, --primes-out=<file>: Dump all used prime numbers
    -o<file>, --image-out=<file>: Create image
    -a<dir>, --animate-outdir=<dir>: Create animation
    -c<j>,<i>,<n>,<m> --crop=<j>,<i>,<n>,<m>:
        Divide source image into n*m segments and crop around (j,i)
        Example: -c 4,3,2,1
                 +---+---+---+---+
                 |   |   |   |   |
                 +---+---+---+---+
                 |   |   |2,1|   |
                 +---+---+---+---+
                 |   |   |   |   |
                 +---+---+---+---+
```

## Example

```bash
wget -O demo.png http://dic.nicovideo.jp/oekaki/648535.png
python primeart.py -d -w 160 -o demo-p.png demo.png
```
