#!/usr/bin/python

import os
import sys
import re

"""
Depends on:
   modern version of Inkscape
   ps2eps
   ps2pdf

"""

def svgStringToBoundedPDF(string, outfilename):
    fid = file("/tmp/%s.tmp.svg" % outfilename, 'w')

    fid.write(string)
    fid.close()
    
    svg2boundedPDF("/tmp/%s.tmp.svg" % outfilename, outfilename)


def svg2boundedPDF(filename, outfilename):
    """
    convert filename to pdf file outputfilename. We make no assumptions
    file extensions. 

    """

    (fidin, fidout)= os.popen4("inkscape --without-gui --file=%s  --print='| ps2eps - > /tmp/%s.eps'" % (filename, filename));


    res =  fidout.read()


    # new attempt to extract outut boundingbox
    fid = file("/tmp/%s.eps" % filename)
    res = fid.read()
    bbre = re.compile("%%BoundingBox: (\d+) (\d+) (\d+) (\d+)")

    m =  bbre.search(res)

    if m:
        (x1, y1, x2, y2) =  m.groups()
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)

        os.popen("ps2pdf -dEPSCrop /tmp/%s.eps  %s" % (filename, outfilename))

if __name__ == "__main__":
    filename = sys.argv[1]

    fnre = re.compile("(.+)\.svg$")

    filenameWithoutSVG = fnre.match(filename).group(1)



    svg2boundedPDF(filename, filenameWithoutSVG + ".pdf")
    
