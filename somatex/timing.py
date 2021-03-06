#!/usr/bin/python

"""
Turns xml into svg. Yea, i could do this with xslt, but it sounds like more work than it's worth.
"""

import sys

from elementtree import ElementTree
from elementtree.ElementTree import Element, SubElement, dump


class signal:
    """

    note that all signal draws are from half a period before the tick to half
    a period after

    constructor calls with name, position in x-y, period width, period height
        
    methods:
       draw clock
       draw_low
       draw_high
       draw_z
       draw_bus
       draw_hash
p
    each of these incrmeents an internal 'tick' variable that we use to figure
    out where to draw. 
    """

    def __init__(self, name, startx, starty, period, height):
        self.name = name
        self.startx = float(startx)
        self.starty = float(starty)
        self.x = float(startx)
        self.y = float(starty)
        
        self.period = float(period)
        self.height = float(height)
        self.sval = ''   # previous value

    def draw_name(self):
        """ the name is to the left of the original draw point"""
        elem = Element("text")
        elem.attrib['x'] =  "%f" %  (self.startx -4)
        elem.attrib['y'] = "%f" % (self.starty-4)
        elem.attrib['font-family'] = "Helvetica"
        elem.attrib['font-size'] = "%f" % (self.height/1.4)
        elem.attrib['text-anchor'] = "end"
        elem.text = self.name
        return elem

    def draw_split(self):
        """ Draws a set of hashmarks at the desired level """

        gelem = Element("g") # create a group
        level = self.sval
        if level == 'H':
            y = self.y-self.height
        elif level == 'Z':
            y = self.y - self.height/2.0
        else:
            y = self.y

        l0elem = Element("line")
        l0elem.attrib['x1'] = str(self.x)
        l0elem.attrib['y1'] = str(y);
        l0elem.attrib['x2'] = str(self.x + 3.5 * self.period/8.0)
        l0elem.attrib['y2'] = str(y);
        l0elem.attrib['stroke'] = "black"

        gelem.append(l0elem)


        l1elem = Element("line")
        l1elem.attrib['x1'] = str(self.x + 3.0* self.period/8.0)
        l1elem.attrib['y1'] = str(y + self.height/4.0);
        l1elem.attrib['x2'] = str(self.x + 4*self.period/8.0)
        l1elem.attrib['y2'] = str(y - self.height/4.0);
        l1elem.attrib['stroke'] = "black"

        gelem.append(l1elem)

        l2elem = Element("line")
        l2elem.attrib['x1'] = str(self.x + 4.0* self.period/8.0)
        l2elem.attrib['y1'] = str(y + self.height/4.0);
        l2elem.attrib['x2'] = str(self.x + 5.0*self.period/8.0)
        l2elem.attrib['y2'] = str(y - self.height/4.0);
        l2elem.attrib['stroke'] = "black"

        gelem.append(l2elem)

        l3elem = Element("line")
        l3elem.attrib['x1'] = str(self.x + 4.5*self.period/8.0)
        l3elem.attrib['y1'] = str(y);
        l3elem.attrib['x2'] = str(self.x + self.period)
        l3elem.attrib['y2'] = str(y);
        l3elem.attrib['stroke'] = "black"

        gelem.append(l3elem)


        self.x += self.period

        return gelem
        
    def draw_clock(self):

        elem = Element("path")
        ptuple = (self.x, self.y, self.period/2, -self.height, self.period/2, self.height)
        elem.attrib['d'] = "M%f,%f h%f v%f h%f v%f" % ptuple
        elem.attrib['stroke'] = "black"
        elem.attrib['fill'] = "none"
        elem.attrib['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'L'
        return elem

    def draw_low(self):
        elem = Element("path")


        if self.sval == 'H':
            starty = self.y - self.height
        elif self.sval == 'Z':
            starty = self.y - self.height/2
        else:
            starty = self.y

        ptuple = (self.x, starty,  self.period/8, self.y-starty, 7*self.period/8)
        elem.attrib['d'] = "M%f,%f  l%f, %f h%f" % ptuple
        elem.attrib['stroke'] = "black"
        elem.attrib['fill'] = "none"
        elem.attrib['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'L'
        

            
        return elem
    
    def draw_high(self):
        elem = Element("path")


        if self.sval == 'L':
            starty = self.y
            delta = -self.height
        elif self.sval == 'Z':
            starty = self.y - self.height/2
            delta = -self.height/2
        else:
            starty = self.y - self.height
            delta = 0.0

        ptuple = (self.x, starty,  self.period/8, delta, 7*self.period/8)
        elem.attrib['d'] = "M%f,%f  l%f, %f h%f" % ptuple
        elem.attrib['stroke'] = "black"
        elem.attrib['fill'] = "none"
        elem.attrib['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'H'

        return elem

    def draw_z(self):
        elem = Element("path")


        if self.sval == 'L':
            starty = self.y
            delta = -self.height/2.0
        elif self.sval == 'H':
            starty = self.y - self.height
            delta = self.height/2
        else:
            starty = self.y - self.height/2.0
            delta = 0.0

        ptuple = (self.x, starty,  self.period/8, delta, 7*self.period/8)
        elem.attrib['d'] = "M%f,%f  l%f, %f h%f" % ptuple
        elem.attrib['stroke'] = "black"
        elem.attrib['fill'] = "none"
        elem.attrib['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'Z'
        
        return elem
    
    def draw_bus(self, title, color):

        gelem = Element("g") # create a group

        oelem = Element("path")

        otuple = (self.x, self.y - self.height/2, self.period/8, -self.height/2, 6*self.period/8.0, self.period/8.0, self.height/2, -self.period/8, self.height/2.0, -6*self.period/8.0)
        oelem.attrib['d']= "M%f,%f l%f,%f h%f l%f,%f l%f,%f h%f Z" % otuple
        oelem.attrib['stroke'] = "black"
        oelem.attrib['fill'] = color
        oelem.attrib['stroke-linecap'] = "square"

        gelem.append(oelem)
        
        telem = Element("text")
        telem.attrib['x'] =  "%f" %  (self.x + self.period/2)
        telem.attrib['y'] = "%f" % (self.y - self.height/4.0-0.3)
        telem.attrib['font-family'] = "Helvetica"
        telem.attrib['font-size'] = "%f" % (self.height/1.9)
        telem.attrib['text-anchor'] = "middle"
        telem.text = title
        
        gelem.append(telem)
        self.x += self.period
        self.sval = 'Z'
        return gelem




class timing:
    
    def __init__(self, filename):
        
        self.filename = filename
        
        # we assume that the clock is the maximum length
        
        self.period = 40
        self.height = 20
        self.signalspacing = 10

        self.xzero = 90
        self.signalcnt  = 0 
        self.cycles = 0
        
        
        self.colors = ['powderblue', 'palegreen', 'lightpink', 'lightsalmon', 'lightgrey']
        self.classes = {}
        
        
        self.svgelem = Element("{http://www.w3.org/2000/svg}svg")


        self.signalselem = Element("g")
        
        self.ypos = self.height + self.signalspacing
      
       



    def set_size(self):
        self.svgelem.attrib["width"] = str(self.xzero + int(self.cycles)*self.period + 2)
        self.svgelem.attrib['height'] = str(self.signalcnt * (self.height+ self.signalspacing) + self.signalspacing +2)

        
    def save(self):

        if self.filename == "":
            dump(self.svgelem)
        else:
            #print "Creating ", self.filename
            ElementTree.ElementTree(self.svgelem).write(self.filename)

    
    def add_clock(self, name, datastr):
        
        sigelem = Element('g')

        # this is where we get the cycle count
        
        self.cycles = len(datastr.split())
        
        clksig = signal(name, self.xzero, self.ypos, self.period, self.height)
        sigelem.append(clksig.draw_name())
        for i in datastr.split():
                sigelem.append(clksig.draw_clock())

        self.ypos += self.signalspacing + self.height   

        self.signalselem.append(sigelem)
        self.signalcnt += 1
        
                
    
    def add_signal(self, name, datastr):

        sigelem = Element('g')
        sig = signal(name, self.xzero, self.ypos, self.period, self.height)
        
        sigelem.append(sig.draw_name())
            
        
        for i in datastr.split():
            if i == 'H':
                sigelem.append(sig.draw_high())
            elif i == 'L':
                sigelem.append(sig.draw_low())
            elif i == 'Z':
                sigelem.append(sig.draw_z())
            elif i == '//':
                sigelem.append(sig.draw_split())

        self.ypos += self.signalspacing + self.height   
        self.signalselem.append(sigelem)
        self.signalcnt += 1

        
    def add_bus(self, name, datastr, classstr):
        sigelem = Element('g')

        
        sig = signal(name, self.xzero, self.ypos, self.period, self.height)
        sigelem.append(sig.draw_name())

        color = "white"

        data = datastr.split()

        if classstr != None:
            classes = classstr.split()

        
        for i in range(len(data)):
            cyccolor = color
            if len(classes) == 0:
                cl = 0
            else:
                cl = classes[i]
            if self.classes.has_key(cl):
                cyccolor = self.classes[cl]
            else:
                cyccolor = self.colors.pop(0)
                self.classes[cl] = cyccolor
            if data[i] =='//':
                sigelem.append(sig.draw_split())
            elif data[i] == 'Z':
                sigelem.append(sig.draw_z())
            else:
                sigelem.append(sig.draw_bus(data[i], cyccolor))            

        self.ypos += self.signalspacing + self.height   
        self.signalselem.append(sigelem)
        self.signalcnt += 1
                
            
    def timinggrid(self):
        """
        This function uses the signalcnt, cycles, period, height, and spacing
        to draw the light lines that will be the clock lines.
        """

        gelem = Element("g") # create a group
        for i in range(int(self.cycles)):

            lelem = Element("line")
            lelem.attrib['x1'] = str(i*self.period + self.period/2.0 + self.xzero)
            lelem.attrib['y1'] = str(0);
            lelem.attrib['x2'] = str(i*self.period + self.period/2.0 + self.xzero)
            lelem.attrib['y2'] = str(self.signalcnt*(self.height + self.signalspacing) + self.signalspacing)
            lelem.attrib['stroke'] = "grey"
            lelem.attrib['stroke-width'] = "0.5"
            gelem.append(lelem)

        
        self.svgelem.append(gelem)
        self.svgelem.append(self.signalselem)
        
import sys

def parseTiming(timingString, outFilename):
    """ takes in a timing string and writes the resulting
    svg to outFilename """

    
    ls = timingString.split('\n')
    
    timingobject = timing(outFilename)
    

    while len(ls) > 0:
        l = ls.pop(0)
        seg = l.split(':')
        if len(seg) > 3:
            seg = [seg[0], seg[1]+ ':' + seg[2], seg[3]]

        cl = seg[0].strip()
        na = seg[1].strip()
        de = seg[2].strip()

        if cl == 'C':
            timingobject.add_clock(na, de)
        elif cl == 'S':
            timingobject.add_signal(na, de)
        elif cl == 'B':
            # check if we have a class:
            if len(ls) > 0 and ls[0][:2] == "BC" :
                
                l = ls.pop(0)
                seg = l.split(':')
                bde = seg[2].strip()
            else:
                # there isn't a class; deal
                bde = ""
                
            timingobject.add_bus(na, de, bde)
    timingobject.timinggrid()
    timingobject.set_size()
    timingobject.save()
                

        
        
        
def main():
    """
    called with filename.xml filename.svg will convert xml
    signal definition to svg. 

    but -d filename to start with will parse the docbook filename
    and create a series of svg files from the timingobject tags with names
         name.timing.svg



    """

    #th = TimingHandler()

    #saxparser = make_parser()

    #saxparser.setContentHandler(th)
    #saxparser.parse(sys.stdin)


    parseTiming(sys.argv[1])
    

if __name__ == "__main__":
    main()
    
    
