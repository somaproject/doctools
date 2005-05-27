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


"""

import StringIO
import re


class TexMemMap(object):

    def __init__(self, id):
        self.header = "\\begin{memmap}{%s}" % id
        self.body = ""
        self.id = id
        self.footer = "\end{memmap}"

    def generate(self):
        return self.header + '\n' \
               + self.body +  '\n' \
               + self.footer

        
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

    for sl in sio.readlines():

        if not re.match("^#", sl):
            # not a comment, let's go:
            result = reSingle.match(sl)
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
    simpletest = """
    0x0000 : Address 1
    0x0001:Address 2
    0x0741: More addresses, yayayyaayyayaayayayyayayayya
    0x0000-0x2000 :  a big range!
    0x0314[3:7] : these are nice bits
    """

    tm = TexMemMap()
    
    memmap2tex(simpletest, tm)
    tm.generate()

def main():
    test()


if __name__ == "__main__":
    main()
