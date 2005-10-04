
"""
A simple demo that reads in an XML document and spits out an equivalent,
but not necessarily identical, document.
"""

import sys, string

from xml.sax import saxutils, handler, make_parser
import re
from scipy import *


def styleStringToDict(sstr):
    sdict = {}
    for i in sstr.split(';'):
        (key, value) = i.split(':')
        sdict[key] = value
    return sdict

        

def transformStringToMatrix(tstr):
    # we parse a transform string and build up an assoicated transform matrix

    ops = tstr.split()
    t = identity(3, Float64)

    scalere = re.compile("scale\(([\d\.\-]+),*([\d\.\-]+)*\)")
    rotatere = re.compile("rotate\(([\d\.\-]+)\)")
    translatere = re.compile("translate\(([\d\.\-e]+),([\d\.\-e]+)\)")


    for o in ops:
        newm = identity(3, Float64)
        if "scale" in o:

            scalestr = scalere.match(o).groups(1)[0]
            scalea = float(scalestr)
            if len(scalere.match(o).groups()) > 2:
                scaleb = float(scalere.match(o).groups()[1])
            else:
                scaleb = scalea
            newm[0, 0] = scalea
            newm[1, 1] = scaleb
        elif "rotate" in o:
            rotatestr = rotatere.match(o).groups(1)[0]
            rotate = float(rotatestr)
            rotdeg = rotate/180.0*pi
            newm[0, 0] = cos(rotdeg)
            newm[0, 1] = -sin(rotdeg)
            newm[1, 0] = sin(rotdeg)
            newm[1, 1] = cos(rotdeg)
        elif "translate" in o:
            transstrx = translatere.match(o).group(1)
            transstry = translatere.match(o).group(2)
            x = float(transstrx)
            y = float(transstry)
            newm[0, 2] = x
            newm[1 , 2]  = y

        elif "matrix" in o:
            newm = getmatrix(o)

        t = matrixmultiply(t, newm)
    return t
        
def getmatrix(matstr):
    """ Takes in a matrix string:
    matrix(2.000000,0.000000,0.000000,1.000000,-240.6250,0.000000)

    and returns the eq. transformation matrix """

    retm = re.compile("matrix\((.+)\)")
    try:
        cstr = retm.match(matstr).group(1)
    except AttributeError:
        raise "problem" 
        
    points = cstr.split(',')
    tm = zeros((3, 3), Float64)
    tm[0, 0] = float(points[0])
    tm[1, 0] = float(points[1])
    tm[2, 0] = 0.0
    tm[0, 1] = float(points[2])
    tm[1, 1] = float(points[3])
    tm[2, 1] = 0.0
    tm[0, 2] = float(points[4])
    tm[1, 2] = float(points[5])
    tm[2, 2] = 1.0

    return tm

def lexPath(pathstr):
    i = 0
    pos = 0
    strlist = []
    substr = ""
    while pos < len(pathstr):

        if pathstr[pos] in ['M', 'm', 'Z', 'z', 'L', 'l', 'H', 'h', 'V', 'v', 'C', 'c', 'S', 's', 'Q', 'q', 'T', 't', 'A', 'a']:
            strlist.append(pathstr[pos])
            substr = ""
            pos +=1
        elif pathstr[pos] in ['-', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            substr += pathstr[pos]
            pos += 1
        else:
            if substr != "":
                strlist.append(substr)
                substr = ""
            pos += 1
    if substr != "":
        strlist.append(substr)
    
    return strlist
            
            
        
        
def transformPath(pathstr, tm):
    """ I really can't believe I'm doing this"""

    # we make the following state machine to convert paths; we build up a list of tuples

    strlist = lexPath(pathstr)

    # minor assumptions are made here about inkscape's svg: always absolute,
    # always an assoicated coordinate set; we raise an error otherwise

    ipos = 0

    outstr = ""
    
    while ipos < len(strlist):

        if strlist[ipos] in ('M', 'L'):
            # move command absolute:
            (xs, ys) = strlist[ipos+1], strlist[ipos+2]
            x = float(xs)
            y = float(ys)

            (newx, newy, dummy) = matrixmultiply(tm, r_[x, y, 1])
            outstr += "%s %f %f " % (strlist[ipos], newx, newy)
            
            ipos += 3
            
        elif strlist[ipos] in ('C'):
            (x1s, y1s) = strlist[ipos+1], strlist[ipos+2]
            (x2s, y2s) = strlist[ipos+3], strlist[ipos+4]
            (xs, ys) = strlist[ipos+5], strlist[ipos+6]
            
            x = float(xs)
            y = float(ys)
            x1 = float(x1s)
            x2 = float(x2s)
            y1 = float(y1s)
            y2 = float(y2s)

            (newx, newy, dummy) = matrixmultiply(tm, r_[x, y, 1])
            (newx1, newy1, dummy) = matrixmultiply(tm, r_[x1, y1, 1])
            (newx2, newy2, dummy) = matrixmultiply(tm, r_[x2, y2, 1])
            outstr += "%s %f %f %f %f %f %f " % (strlist[ipos], newx1, newy1,
                                                 newx2, newy2,
                                                 newx, newy)

            ipos += 7
        elif strlist[ipos] in ('Z', 'z'):
            outstr += " z"
            ipos += 1

        elif strlist[ipos] in ['A', 'a']:
            #
            rxs = strlist[ipos + 1]
            rys = strlist[ipos + 2]
            xaxisrotations = strlist[ipos+3]
            largearcflags = strlist[ipos + 4]
            sweepflags = strlist[ipos + 5]
            xs = strlist[ipos + 6]
            ys = strlist[ipos + 7]

            rx = float(rxs)
            ry = float(rys)
            xaxisrotation = float(xaxisrotations)
            x = float(xs)
            y = float(ys)
            largearcflag = largearcflags
            sweepflag = sweepflags
            
            (rxnew, rynew, dummy) = matrixmultiply(tm, r_[rx, ry, 1])
            #(rxnew, rynew) = (rx, ry)
            
            xaxisrotationnew = xaxisrotation  + 180
            (xnew, ynew, dummy) = matrixmultiply(tm, r_[x, y, 1]) 
            #(xnew, ynew) = (x, y)

            outstr += "%s %f %f %f %s %s %f %f "  % (strlist[ipos],
                                                     rxnew, rynew,
                                                     xaxisrotationnew,
                                                     largearcflag,
                                                     sweepflag,
                                                     xnew,
                                                     ynew)
            
            ipos += 8
            
            
            
    return outstr

        
    
    

# --- The ContentHandler

class ContentGenerator(handler.ContentHandler):

    def __init__(self, out = sys.stdout):
        handler.ContentHandler.__init__(self)
        self._out = out

        self.tmstack = []

    def getCurrentTM(self):

        # returns the current net transformation matrix

        t = identity(3, Float64)

        for m in self.tmstack:
            t = matrixmultiply(t, m)
        return t

    def checkCurrentTM(self):
        tm = self.getCurrentTM()
        if abs(tm[0, 0]) != abs(tm[1, 1]):
            print "non-uniformly scaled transformation matrix"
            return True
        return False
            
        
    # ContentHandler methods
        
    def startDocument(self):
        self._out.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')
        self._out.write('<svg>')
        
    def startElement(self, name, attrs):

        if attrs.has_key("transform"):
            newtm = transformStringToMatrix(str(attrs["transform"]))
        else:
            newtm = identity(3, Float64)

        self.tmstack.append(newtm)

        tm = self.getCurrentTM()
        stm = False


        if self.checkCurrentTM():
            print name
            self._out.write('<' + name)
            for (name, value) in attrs.items():
                self._out.write(' %s="%s"' % (name,
                                              saxutils.escape(value)))
                
            self._out.write('>')

    def endElement(self, name):
        if self.checkCurrentTM():
            self._out.write('</%s>' % name)
        self.tmstack.pop()
        


    def characters(self, content):
        if self.checkCurrentTM():
            self._out.write(saxutils.escape(content))

    def ignorableWhitespace(self, content):
        self._out.write(content)
        
    def processingInstruction(self, target, data):
        #self._out.write('<?%s %s?>' % (target, data))
        pass

    def endDocument(self):
        self._out.write('</svg>')
    
# --- The main program

parser = make_parser()
fout = file("/tmp/test.svg", 'w')

parser.setContentHandler(ContentGenerator(fout))
parser.parse(sys.argv[1])
