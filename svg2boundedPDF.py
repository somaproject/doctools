#!/usr/bin/python

import os
import sys
import re

filename = sys.argv[1]
(fidin, fidout)= os.popen4("inkscape --without-gui --file=%s  --print='| ps2eps - > /tmp/%s.eps'" % (filename, filename));

bbre = re.compile("%%BoundingBox: (\d+) (\d+) (\d+) (\d+)")

res =  fidout.read()
m =  bbre.search(res)

fnre = re.compile("(.+)\.svg$")

filenameWithoutSVG = fnre.match(filename).group(1)
    

if m:
    (x1, y1, x2, y2) =  m.groups()
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)

    os.popen("ps2pdf -dDEVICEWIDTHPOINTS=%d -dDEVICEHEIGHTPOINTS=%d /tmp/%s.eps  %s.pdf" % (x2-x1, y2-y1, filename, filenameWithoutSVG))
