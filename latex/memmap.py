#!/usr/bin/python
"""
memmap: turns .memmap files into latex for inclusion in our LaTeX documents


A memmap file consists of a series of memory maps, of the form:


A single word:

0x0000 : explanation

A range of words:

0x0000-0x0005 : explanation

Some bits:

0x0012[0:4] : these bits let you set hair color (0 - 31)

Note that normally bits will follow a word, such that you'd have

0x0741    : Face attributes bitfield
0x0741[0] : Bit to set whether male or female
0x0741[1:7] : eyebrow caterpillar index, little endian

note that all fields above are strings, not numbers, such that you could have
0x0870 - 0x2000+2n : 

Comment lines begin with a #

Note that our tex output is a tabular environment. Dance dance convolution!


The convention is to create foo.bar.baz.memmap, and process it to foo.bar.baz.memmap.tex


"""

import StringIO
import re
import sys

class TexMemMap(object):

    def __init__(self):
        self.header = "\\begin{MemMap}"
        self.body = ""
        self.title = ""
        self.footer = "\end{MemMap}"

    def generate(self):
        print self.header
        print self.body
        print self.footer
    def genTitle(self, string):
        self.header += "{%s}" % string.strip()
        
    def genSimple(self, addr, expl):
        self.body +=  "\MemMapSimple{%s}{%s}\n" % (addr, expl)
    
    def genRange(self, saddr, eaddr, expl):
        self.body += "\MemMapRange{%s}{%s}{%s}\n" % (saddr, eaddr,  expl)

    def genWithBits(self, addr, bits, expl):
        self.body +=  "\MemMapWithBits{%s}{%s}{%s}\n" % (addr, bits,  expl)

def memmap2tex(memmap, mmOutput):
    # takes in a full memmap string

    # our pre-build regexps:
    reSingle = re.compile("^([\w\s]+):(.+)")
    reRange = re.compile("^(.+)-(.+):(.+)")
    reWithBits = re.compile("^(.+)\[(.+)\]\s*:(.+)")

    # we read a line at a time, try and match the regexp, and go!
    
    sio = StringIO.StringIO(memmap); 
    firstline = True
    
    for sl in sio.readlines():
        if firstline:
            mmOutput.genTitle(sl)
            firstline = False
        else:
            if not re.match("^#", sl):
                # not a comment, let's go:
                result = reSingle.match(sl.strip())
                if result:
                    # this was a simple:
                    mmOutput.genSimple(result.group(1).strip(),
                                    result.group(2).strip())

                result = reRange.match(sl)
                if result:
                    mmOutput.genRange(result.group(1).strip(),
                                   result.group(2).strip(),
                                   result.group(3).strip())

                result = reWithBits.match(sl)
                if result:
                    mmOutput.genWithBits(result.group(1).strip(),
                                      result.group(2).strip(),
                                      result.group(3).strip());
            
            
def test():
    simpletest = """This is an example memory map
    0x0000 : Address 1
    0x0001:Address 2
    0x0741: More addresses, yayayyaayyayaayayayyayayayya
    0x0000-0x2000 :  a big range
    0x0314[3:7] : these are nice bits
    """

    tm = TexMemMap()
    
    memmap2tex(simpletest, tm)
    tm.generate()

def main():

    fstr = file(sys.argv[1]).read()
    
    tm = TexMemMap()
    
    memmap2tex(fstr, tm)
    tm.generate()



if __name__ == "__main__":
    main()
