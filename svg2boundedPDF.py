#!/usr/bin/python

import os
import sys
import re

def svg2boundedPDF(filename):

    (fidin, fidout)= os.popen4("inkscape --without-gui --file=%s  --print='| ps2eps - > /tmp/%s.eps'" % (filename, filename));


    res =  fidout.read()


    # new attempt to extract outut boundingbox
    fid = file("/tmp/%s.eps" % filename)
    res = fid.read()
    bbre = re.compile("%%BoundingBox: (\d+) (\d+) (\d+) (\d+)")

    m =  bbre.search(res)

    fnre = re.compile("(.+)\.svg$")

    filenameWithoutSVG = fnre.match(filename).group(1)


    if m:
        (x1, y1, x2, y2) =  m.groups()
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)

        #print x1, x2, y1, y2
        #os.popen("ps2pdf -dDEVICEWIDTHPOINTS=%d -dDEVICEHEIGHTPOINTS=%d /tmp/%s.eps  %s.pdf" % (x2-x1, y2-y1, filename, filenameWithoutSVG))
        os.popen("ps2pdf -dEPSCrop /tmp/%s.eps  %s.pdf" % (filename, filenameWithoutSVG))

if __name__ = "__main__":
    filename = sys.argv[1]
    svg2boundedPDF(filename)
    
