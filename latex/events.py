#!/usr/bin/python
"""

This is our attempt to programatically generate Event plots and configuraiton information. I'm not yet sure the best way to do this, although I think what we want is maybe two lines.

The problem is that an event is, in total, 6*16 = 96 bits, which is just too
freaking wide, so we use 3 rows.


How to represent, draw?

drawWordBase(x, y, lcap, rcap):


How to represent an event / a sequence of bits?


""" 
import xml.dom.minidom
import xml.dom.ext
import re
from StringIO import * 

xmlns="http://www.w3.org/2000/svg"

BITSIZE = 7.5 # size of bit square in points

def genRectElement(doc, x, y, width, height, fill=None, stroke="none",
                   strokewidth=1.0):
    bgRect = doc.createElementNS(xmlns, "rect")
    bgRect.setAttributeNS(xmlns, "x",
                          "%f" % x)
    bgRect.setAttributeNS(xmlns, "y",
                          "%f" % y)
    bgRect.setAttributeNS(xmlns, "width",
                          "%f" % width)
    bgRect.setAttributeNS(xmlns, "height",
                          "%f" % height)
    stylestr = ""
    if fill:
        stylestr += "fill:%s;" % fill
    stylestr += "stroke:%s;" % stroke
    stylestr += "stroke-width:%f" % strokewidth
        
    bgRect.setAttributeNS(xmlns, "style",
                          stylestr); 

    return bgRect

def genPathElement(doc, x, y, xlist, ylist, strokeWidth=1, stroke=None):
    pelem = doc.createElementNS(xmlns, "path")

    pathstr = "M %f %f " % (x, y)

    for i in range(len(xlist)):
        pathstr += " L %f %f"  % (xlist[i], ylist[i])
        
    pelem.setAttributeNS(xmlns, "d",
                          pathstr);

    stylestr = ""
    if stroke:
        stylestr += "stroke:%s;" % stroke
    if strokeWidth:
        stylestr += "stroke-width:%f;" % strokeWidth 

    pelem.setAttributeNS(xmlns, "style",
                          stylestr); 

    return pelem

def genTextElement(doc, x, y, string, size, anchor="middle", fill="black"):
    pelem = doc.createElementNS(xmlns, "text")
    
    pelem.setAttributeNS(xmlns, "x",
                         "%f" % x)
    pelem.setAttributeNS(xmlns, "y",
                         "%f" % y)

    pelem.setAttributeNS(xmlns, "text-anchor", anchor)
    pelem.setAttributeNS(xmlns, "font-size", "%f" % size)
    pelem.setAttributeNS(xmlns, "style", "fill:%s" % fill)

    description = doc.createTextNode(string)

    pelem.appendChild(description)
    
    
    return pelem
    
    

class xmlFrame:

    def __init__(self, xos, yos):
        self.doc = xml.dom.minidom.Document()

        self.svgElement = self.doc.createElementNS(xmlns, "svg")
        self.svgElement.setAttributeNS(xmlns, "width", "100%")
        self.svgElement.setAttributeNS(xmlns, "height", "100%")
        self.xos = xos
        self.yos = yos

    def getText(self, fid = None):
        
        self.doc.appendChild(self.svgElement)
        if fid:
            xml.dom.ext.PrettyPrint(self.doc, fid)
        else:
            sfid = StringIO()
            xml.dom.ext.PrettyPrint(self.doc, sfid)
            return sfid.getvalue()
   
    def drawWordBase(self, x, y, lcap, rcap,  name, bits):
        """
        bits = how many bits?
        x, y : lower left-hand corner of word
        lcap: ls the left-end capped
        rcap: is the right-end capped

        """

        x += self.xos
        y += self.yos
        
        groupElement = self.doc.createElementNS(xmlns, "g")
       

       
        # start group

        # draw background square

        groupElement.appendChild(genRectElement(self.doc,
                                                x, y, BITSIZE*bits,
                                                BITSIZE,
                                                fill = "rgb(192,192,192)"))
        # draw top bit-indicator background
        groupElement.appendChild(
            genRectElement(self.doc,
                           x, y-BITSIZE/3.0, BITSIZE*bits,
                           BITSIZE/3.0, fill = "rgb(192,192,192)"))



        # draw bit-markers:
        for i in range(bits+1):

            if i == 0 or i == bits:
                stroke = "black"
            else:
                stroke = "rgb(128,128,128)"
            groupElement.appendChild(
                genPathElement(self.doc,
                               x + i*BITSIZE, y-BITSIZE/3.0,
                               [x + i*BITSIZE], [y], stroke=stroke))
        
        # draw top line
        groupElement.appendChild(genPathElement(self.doc,
                                                x, y, [BITSIZE*bits+x], [y],
                                                stroke="black"))

        # draw bottom line
        groupElement.appendChild(
            genPathElement(self.doc,
                           x, y+BITSIZE, [BITSIZE*bits+x], [y+BITSIZE],
                          stroke="black"))
        
        #draw caps (?)
        if lcap:
            groupElement.appendChild(
                genPathElement(self.doc,
                               x, y, [x], [y+BITSIZE],
                               stroke="black"))
            
        if rcap:
            groupElement.appendChild(
                genPathElement(self.doc,
                               x+BITSIZE*bits, y, [x+BITSIZE*bits],
                               [y+BITSIZE],
                               stroke="black"))
        

        # label text
        groupElement.appendChild(
            genTextElement(self.doc, x + BITSIZE/2.0, y - BITSIZE/3.0-0.5, 
                           "%d" % (bits-1), 4)) 

        groupElement.appendChild(
            genTextElement(self.doc, x + BITSIZE/2.0 + BITSIZE*(bits-1),
                           y - BITSIZE/3.0 - 0.5, 
                           "0", 4)) 

        # word text
        groupElement.appendChild(
            genTextElement(self.doc, x + (BITSIZE*bits)/2.0,
                           y - BITSIZE/3.0 - 1, 
                           name, 6, fill="gray"))
        
        self.svgElement.appendChild(groupElement)

    def drawBitRange(self, x, y, startbit, stopbit, name, totalbits):
        #print x, y, startbit, stopbit, name, totalbits
        x += self.xos
        y += self.yos

        if startbit > stopbit:
            print "ERROR"
            raise LogicError
        groupElement = self.doc.createElementNS(xmlns, "g")
       
       
        # start group
        groupElement.appendChild(
            genRectElement(self.doc,
                           x + (totalbits-stopbit-1)*BITSIZE, y,
                           BITSIZE*(stopbit-startbit+1),
                           BITSIZE, fill = "white",
                           stroke = "black", strokewidth=1.0))


        # draw left line:
        groupElement.appendChild(
            genPathElement(self.doc,
                           x + (totalbits - stopbit-1)*BITSIZE, y,
                           [x + (totalbits - stopbit-1)*BITSIZE], [y+BITSIZE],
                           stroke="black"))

        groupElement.appendChild(
            genPathElement(self.doc,
                           x + (totalbits - startbit)*BITSIZE, y,
                           [x + (totalbits - startbit)*BITSIZE], [y+BITSIZE],
                           stroke="black"))

        # draw text
        groupElement.appendChild(
            genTextElement(self.doc, x + BITSIZE*(totalbits-stopbit) \
                           + (stopbit-startbit-1)*BITSIZE/2.0,
                           y + BITSIZE-0.9, 
                           name, 7.8, fill="black"))

        
        self.svgElement.appendChild(groupElement)

class Event:
    """
    So, in fact, this is really confusing.
    The event obviously has a source, and a command, but beyond that, we
    need some way of intelligently describing the subsequent bitfield.

    we could try and just amalgamate the 16*5 = 80 bits and specify their
    resulting ranges

    So event will take in an event string that we parse from LATEX of the
    form

    CMD: 0x40
    SRC: ANY
    DW0[3:8]
    DW1-2: blah

    etc. etc.

    Now, the mapping between bit string and DW is somewhat confusing:
        

    we convert this into an internal :
    .cmd : command string
    .src : source string
    .fields[0]: a sorted list of bit ranges, 0-79,
    .fieldnames: an accompanying list of names
    
    
    """

    
    def __init__(self, inputstr):
        self.cmd = ""
        self.src = ""
        self.fields = [[], [], [], [], [], []]
        self.fieldnames = [[], [], [], [], [], []]

        self.parseEventString(inputstr)
        
        

                           
    def parseEventString(self, dstr):
        segs = dstr.split('\n')

        cmdre = re.compile("^\s*CMD\s*:(.+)")
        srcre = re.compile("^\s*SRC\s*:(.+)")
        dwre = re.compile("^\s*DW(\d)(\[(\d+)+(:(\d+))*\])*\s*:\s*(.+)")


        for s in segs:
            if cmdre.match(s):
                self.cmd = cmdre.match(s).group(1)
            elif srcre.match(s):
                self.src = srcre.match(s).group(1)
            elif dwre.match(s):
                
                word = int(dwre.match(s).group(1))
                bitsH = dwre.match(s).group(3)
                bitsL = dwre.match(s).group(5)
                name = dwre.match(s).group(6)
                if bitsL and bitsH :
                    bitsL = int(bitsL)
                    bitsH = int(bitsH)
                elif bitsL:
                    bitsL = int(bitsL)
                    bitsH = int(bitsL)
                else:
                    bitsL = 0
                    bitsH = 15
                self.fields[word].append((bitsL, bitsH))
                self.fieldnames[word].append(name)
                
    def generateSVG(self):
        self.xmlf = xmlFrame(0, 10)

        heightspace = 3*BITSIZE

        # first, we generate the command/data word:
        self.xmlf.drawWordBase(0, 0, True, False, 'CMD', 8)
        self.xmlf.drawBitRange(0, 0, 0, 7, self.cmd, 8)
        self.xmlf.drawWordBase(BITSIZE*8, 0, False, True, 'SRC', 8)
        self.xmlf.drawBitRange(BITSIZE*8, 0, 0, 7, self.src, 8)
        
        # Then we generate the word after that:
        self.xmlf.drawWordBase(BITSIZE*16, 0, True, True, 'EDW0', 16)
        for b, n in zip(self.fields[0], self.fieldnames[0]):
            self.xmlf.drawBitRange(BITSIZE*16, 0, b[0], b[1], n, 16)
            
        
        # genereate the next two data words
        self.xmlf.drawWordBase(0, heightspace, True, True, 'EDW1', 16)
        for b, n in zip(self.fields[1], self.fieldnames[1]):
            self.xmlf.drawBitRange(0, heightspace, b[0], b[1], n, 16)

        self.xmlf.drawWordBase(BITSIZE*16, heightspace, True, True, 'EDW2', 16)
        for b, n in zip(self.fields[2], self.fieldnames[2]):
            self.xmlf.drawBitRange(BITSIZE*16, heightspace, b[0], b[1], n, 16)

        # genereate the final two data words
        self.xmlf.drawWordBase(0, heightspace*2, True, True, 'EDW3', 16)
        for b, n in zip(self.fields[3], self.fieldnames[3]):
            self.xmlf.drawBitRange(0, heightspace*2, b[0], b[1], n, 16)

        self.xmlf.drawWordBase(BITSIZE*16, heightspace*2, True, True, 'EDW4', 16)
        for b, n in zip(self.fields[4], self.fieldnames[4]):
            self.xmlf.drawBitRange(BITSIZE*16, heightspace*2, b[0], b[1], n, 16)
         
    def getText(self, fid = None):
        if fid:
            self.xmlf.getText(fid)
        else:
            sfid = StringIO()
            self.xmlf.getText(sfid)
            return sfid.getvalue()

        
class DSPcmd:
    """
    TARGET: 0x40
    ADDR: 0x80
    DW0: foo
    DW1: boo
    

    etc. etc.

    Now, the mapping between bit string and DW is somewhat confusing:
        

    we convert this into an internal :
    .target : target string
    .addr : addr string
    .fields[0]: a sorted list of bit ranges
    .fieldnames: an accompanying list of names
    
    
    """

    
    def __init__(self, inputstr):
        self.cmd = ""
        self.src = ""
        self.target = ""
        self.addr = ""
        
        self.fields = [[], []]
        self.fieldnames = [[], []]

        self.parseEventString(inputstr)
        
        

                           
    def parseEventString(self, dstr):
        segs = dstr.split('\n')

        cmdre = re.compile("^\s*CMD\s*:(.+)")
        srcre = re.compile("^\s*SRC\s*:(.+)")
        targetre = re.compile("^\s*TARGET\s*:(.+)")
        addrre = re.compile("^\s*ADDR\s*:(.+)")
        dwre = re.compile("^\s*DW(\d)(\[(\d+)+(:(\d+))*\])*\s*:\s*(.+)")


        for s in segs:
            if cmdre.match(s):
                self.cmd = cmdre.match(s).group(1)
            elif srcre.match(s):
                self.src = srcre.match(s).group(1)
            elif targetre.match(s):
                self.target = targetre.match(s).group(1)
            elif addrre.match(s):
                self.addr = addrre.match(s).group(1)
            elif dwre.match(s):
                
                word = int(dwre.match(s).group(1))
                bitsH = dwre.match(s).group(3)
                bitsL = dwre.match(s).group(5)
                name = dwre.match(s).group(6)
                if bitsL and bitsH :
                    bitsL = int(bitsL)
                    bitsH = int(bitsH)
                elif bitsL:
                    bitsL = int(bitsL)
                    bitsH = int(bitsL)
                else:
                    bitsL = 0
                    bitsH = 15
                self.fields[word].append((bitsL, bitsH))
                self.fieldnames[word].append(name)
                
    def generateSVG(self):
        self.xmlf = xmlFrame(0, 10)

        heightspace = 3*BITSIZE

        # first, we generate the command/data word:
        self.xmlf.drawWordBase(0, 0, True, False, 'CMD', 8)
        self.xmlf.drawBitRange(0, 0, 0, 7, self.cmd, 8)
        self.xmlf.drawWordBase(BITSIZE*8, 0, False, True, 'SRC', 8)
        self.xmlf.drawBitRange(BITSIZE*8, 0, 0, 7, self.src, 8)
        
        # Then we generate the word after that:
        self.xmlf.drawWordBase(BITSIZE*16, 0, True, False, 'TARGET', 8)
        self.xmlf.drawBitRange(BITSIZE*16, 0, 0, 7, self.target, 8)
        self.xmlf.drawWordBase(BITSIZE*24, 0, False, True, 'ADDR', 8)
        self.xmlf.drawBitRange(BITSIZE*24, 0, 0, 7, self.addr, 8)

            
        
        # genereate the first data word
        self.xmlf.drawWordBase(0, heightspace, True, True, 'DW0', 32)
        for b, n in zip(self.fields[0], self.fieldnames[0]):
            self.xmlf.drawBitRange(0, heightspace, b[0], b[1], n, 32)

        # genereate the second data word
        self.xmlf.drawWordBase(0, heightspace*2, True, True, 'DW1', 32)
        for b, n in zip(self.fields[1], self.fieldnames[1]):
            self.xmlf.drawBitRange(0, heightspace*2, b[0], b[1], n, 32)

    def getText(self, fid = None):

        if fid :
            
            self.xmlf.getText(fid)
        else:
            sfid = StringIO()
            self.xmlf.getText(sfid)
            return sfid.getvalue()

        
def stest():
    xf = xmlFrame(16)
    xf.drawWordBase(10, 10, True, True, "ETEST");
    xf.drawBitRange(10, 10, 13, 15, "TET")
    xf.getText()

def dtest():
    inputstr = """
    CMD: 0x80
    SRC : SOURCE
    DW0 : TEST
    DW1[0:3] : INSP
    DW1[4:8] : HAFA
    DW1[9] : R
    DW4 : WORD1[31:16]
    DW3 : WORD1[15:0]
    """
    e = Event(inputstr)
    e.generateSVG()
    e.getText()
    

    
if __name__ == "__main__":
    dtest()
