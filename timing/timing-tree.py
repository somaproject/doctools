#!/athena/bin/python

"""
Turns XML into a tree, then into SVG-XML.
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import sys

tree = []

class TimingHandler(ContentHandler):
    """
    A handler to deal with our signal object thingies

    """

    def __init__(self):
        self.svgfilename = ""
        self.timingobj = None
        self.inData = False
        self.inClass = False
        self.inTiming = False
        
    def startElement(self, name, attrs):

        if name == "timingobject":
            self.svgfilename = "%s.timing.svg" % (attrs['name'],)            
            self.timingobject = timing(self.svgfilename)
            self.inData = False
            self.inClass = False
            self.inTiming = True

        elif name == "timing":
            self.svgfilename = ""
            self.timingobject = timing(self.svgfilename)
            self.inData = False
            self.inClass = False
            self.inTiming = True
            
        elif name == "clock" or name == "bus" or name == "signal":
            if self.inTiming:
                self.datastr = ""
                self.classstr = ""
                self.name = attrs['name']

                if name == "clock" or name=="signal":
                    self.inData = True
        elif name == "data":
            if self.inTiming:
                self.inData = True
        elif name == "class":
            if self.inTiming:
                self.inClass = True

    def characters(self, characters):
        
        if self.inData :
            self.datastr += characters
        elif self.inClass:
            self.classstr += characters

    def endElement(self, name):
        if self.inData :
            self.inData = False

        if self.inClass:
            self.inClass = False
        
        if self.inTiming :
            if name == "clock":
                self.timingobject.add_clock_to_tree(self.name, self.datastr)
            elif name == "signal":
                self.timingobject.add_signal(self.name, self.datastr)
            elif name == "bus":                
                self.timingobject.add_bus(self.name, self.datastr, self.classstr)

            if name == "timing" or name=="timingobject":
                self.inTiming = False
"""
                self.timingobject.timinggrid()
                self.timingobject.set_size()
                self.timingobject.save()
"""
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
        
        
        self.ypos = self.height + self.signalspacing

    def set_size(self):
        self.svgelem.attrib["width"] = str(self.xzero + int(self.cycles)*self.period + 2)
        self.svgelem.attrib['height'] = str(self.signalcnt * (self.height+ self.signalspacing) + self.signalspacing +2)

    def add_clock_to_tree(self, name, datastr):
	self.cycles = len(datastr.split())
	tree.append(self.cycles)



class signal:

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
        dict = {}
        dict[x] = (self.startx -4)
        dict[y] = (self.starty-4)
        dict[font-family] = "Helvetica"
        dict[font-size] = (self.height/1.4)
        dict[text-anchor] = "end"
        dict[name] = self.name
        return dict
       









def main():
    """
    called with filename.xml filename.svg will convert xml
    signal definition to svg. 

    but -d filename to start with will parse the docbook filename
    and create a series of svg files from the timingobject tags with names
         name.timing.svg



    """
    th = TimingHandler()

    saxparser = make_parser()

    saxparser.setContentHandler(th)
    saxparser.parse(sys.stdin)
    print tree

if __name__ == "__main__":
    main()
