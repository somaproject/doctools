#!/usr/bin/python

import os
import os.path
import sys
import re

import md5

"""
Takes an SVG file and generates a PDF with a tight bounding box.


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
    #svg2boundedPDFeps(filename, outfilename)
    svg2boundedPDFbatik(filename, outfilename)

def svg2boundedPDFbatik(filename, outfilename):
    """
    Uses batik and java to convert svg file filename to pdf file ouputfilename
    """

    somatexpy = sys.argv[0]
    #we just go up two and then append the jarfile
    s1 = os.path.split(somatexpy)[0]
    s2 = os.path.split(s1)[0]
    print s2
    
    jarfile = "batik/batik-rasterizer.jar" 
    os.system("java -jar %s -m application/pdf %s -d %s" % (s2 + '/' + jarfile,
                                                            filename,
                                                            outfilename))
    
              
def svg2boundedPDFeps(filename, outfilename):
    """
    convert filename to pdf file outputfilename. We make no assumptions
    file extensions. Goes through an eps intermediate step. 

    Creates a constraining bounding box.
    
    """

    if os.path.isfile("/tmp/svg2boundedPDF.eps"):
        os.unlink("/tmp/svg2boundedPDF.eps")
        


    try:
        fid = file(filename)
    except IOError:
        raise IOError, "%s not openable" % filename
    fid.close()
        
    cmdstr = "inkscape --without-gui --file=%s  --print='| ps2eps - > /tmp/svg2boundedPDF.eps'" % (filename)
    
    (fidin, fidout)= os.popen4(cmdstr)

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
    
