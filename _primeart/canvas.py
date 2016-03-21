from collections import namedtuple
from PIL import Image, ImageDraw
import sys, os, shutil

class Canvas:
    
    def __init__(self, font, cols, rows, animate_dir=None, abs_pos=False):
        self.font = font
        self.pitch = self.font.width
        self.line_height = self.font.height
        self.animate_dir = animate_dir
        if animate_dir is not None: os.makedirs(animate_dir)
        self.bgcolor = 'black' if self.font.dark else 'white'
        self.cols = cols
        self.rows = rows
        self.row = 0
        self.column = 0
        self.column_prev = 0
        self.abs_pos = abs_pos
        self.__clear_buffer()
        #
        w = self.cols * self.pitch
        h = self.rows * self.line_height
        self.buffer_total = Image.new('1', (w, h), self.bgcolor)
        if self.abs_pos: print("\033[2J")
    
    def __clear_buffer(self):
        w = self.cols * self.pitch
        h = self.line_height
        self.buffer = Image.new('1', (w, h), self.bgcolor)
        self.sequence = 0
    
    def print_back(self, s, omit_after=None):
        if omit_after is not None:
            l = len(s) - omit_after
            r = self.cols - self.column_prev - omit_after
            if r < l:
                s = s[0:omit_after]
                if 2 <= r: s += '..'
        if self.abs_pos:
            sys.stdout.write("\033[%d;%dH\033[K%s" % (self.row+1, self.column_prev+1, s))
        else:
            if self.column_prev < self.column:
                sys.stdout.write("\033[%dD\033[K%s" % (self.column - self.column_prev, s))
            else:
                sys.stdout.write(s)
        sys.stdout.flush()
        self.column = self.column_prev
        x = self.column * self.pitch
        draw = ImageDraw.Draw(self.buffer)
        draw.rectangle((x, 0, self.buffer.size[0], self.line_height), self.bgcolor)
        for i in range(0, len(s)):
            n = s[i]
            if '0'<=n and n<='9':
                self.buffer.paste(self.font.images[int(n)], (x, 0))
            elif 'a'<=n and n<='z':
                self.buffer.paste(self.font.images_alp[ord(n) - ord('a')], (x, 0))
            x += self.pitch
        self.column += len(s)
    
    def print_commit(self, s, omit_after=None):
        self.column_prev = self.column
        self.print_back(s, omit_after)
    
    def new_line(self):
        y = self.row * self.line_height
        self.buffer_total.paste(self.buffer, (0, y))
        #
        self.row += 1
        self.column = 0
        self.column_prev = 0
        self.__clear_buffer()
        print("")
    
    def cancel_line(self):
        if not self.abs_pos:
            sys.stdout.write("\033[%dD\033[K" % self.column)
        self.column = self.column_prev = 0
        self.__clear_buffer()
        if self.animate_dir is not None:
            shutil.rmtree('%s/row%05d' % (self.animate_dir, self.row))
    
    def save(self):
        if self.animate_dir is None: return
        if self.sequence == 0:
            os.makedirs('%s/row%05d' % (self.animate_dir, self.row))
        self.buffer.save('%s/row%05d/seq%05d.png' % (self.animate_dir, self.row, self.sequence))
        self.sequence += 1
    
    def save_total(self, filename):
        self.buffer_total.save(filename)
