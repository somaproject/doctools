#!/usr/bin/python

import os
import sys
import re

import md5

"""
Depends on:
   modern version of Inkscape
   ps2eps
   ps2pdf

"""

def svgStringToBoundedPDF(string, outfilename):
    hash = md5.new()
    hash.update(string)
    
    fid = file("/tmp/%s.tmp.svg" % hash.hexdigest(), 'w')

    fid.write(string)
    fid.close()
    
    svg2boundedPDF("/tmp/%s.tmp.svg" % hash.hexdigest(), outfilename)


def svg2boundedPDF(filename, outfilename):
    """
    convert filename to pdf file outputfilename. We make no assumptions
    file extensions. 

    """

    (fidin, fidout)= os.popen4("inkscape --without-gui --file=%s  --print='| ps2eps - > /tmp/svg2boundedPDF.eps'" % (filename));


    res =  fidout.read()


    # new attempt to extract outut boundingbox
    fid = file('/tmp/svg2boundedPDF.eps')
    res = fid.read()
    bbre = re.compile("%%BoundingBox: (\d+) (\d+) (\d+) (\d+)")

    m =  bbre.search(res)

    if m:
        (x1, y1, x2, y2) =  m.groups()
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)

        os.popen("ps2pdf -dEPSCrop /tmp/svg2boundedPDF.eps  %s" % ( outfilename))

if __name__ == "__main__":
    filename = sys.argv[1]

    fnre = re.compile("(.+)\.svg$")

    filenameWithoutSVG = fnre.match(filename).group(1)



    svg2boundedPDF(filename, filenameWithoutSVG + ".pdf")
    
