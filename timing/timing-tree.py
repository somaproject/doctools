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
                self.timingobject.add_signal_to_tree(self.name, self.datastr)
            elif name == "bus":                
                self.timingobject.add_bus_to_tree(self.name, self.datastr, self.classstr)

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
	clksig = signal(name, self.xzero, self.ypos, self.period, self.height)
	tree.append(self.cycles)
	tree.append((clksig.create_name_node(), clksig.create_clock_node()))
	
	self.ypos += self.signalspacing + self.height  

    def add_signal_to_tree(self, name, datastr):
	sig = signal(name, self.xzero, self.ypos, self.period, self.height)
	sigelem = []	
        for i in datastr.split():
            if i == 'H':
                sigelem.append(sig.create_high_node())
            elif i == 'L':
                sigelem.append(sig.create_low_node())
            elif i == 'Z':
                sigelem.append(sig.create_z_node())
            elif i == '//':
                sigelem.append(sig.draw_split())

        self.ypos += self.signalspacing + self.height   
#        self.signalselem.append(sigelem)
        self.signalcnt += 1	
	tree.append(sig.create_name_node()) 
	tree.append(sigelem)

    def add_bus_to_tree(self, name, datastr, classstr):
        sigelem = []
        
        sig = signal(name, self.xzero, self.ypos, self.period, self.height)

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
                sigelem.append(sig.create_z_node())
            else:
                sigelem.append(sig.create_bus_node(data[i], cyccolor))            
        self.ypos += self.signalspacing + self.height   
#        self.signalselem.append(sigelem)
	tree.append(sig.create_name_node())
	tree.append(sigelem)
        self.signalcnt += 1	

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


    def create_name_node(self):
        """ the name is to the left of the original draw point"""
        dict = {}
        dict['x'] = (self.startx -4)
        dict['y'] = (self.starty-4)
        dict['font-family'] = "Helvetica"
        dict['font-size'] = (self.height/1.4)
        dict['text-anchor'] = "end"
        dict['name'] = self.name
        return dict
      
    def create_clock_node(self):
	dict = {}
        ptuple = (self.x, self.y, self.period/2, -self.height, self.period/2, self.height)
        dict['d'] = "M%f,%f h%f v%f h%f v%f" % ptuple
        dict['stroke'] = "black"
        dict['fill'] = "none"
        dict['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'L'
	return dict

    def create_low_node(self):
	dict = {}

        if self.sval == 'H':
            starty = self.y - self.height
        elif self.sval == 'Z':
            starty = self.y - self.height/2
        else:
            starty = self.y

        ptuple = [self.x, starty,  self.period/8, self.y-starty, 7*self.period/8]
        dict['d'] = ptuple
        dict['stroke'] = "black"
        dict['fill'] = "none"
        dict['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'L'
	return dict

    def create_high_node(self):

        if self.sval == 'L':
            starty = self.y
            delta = -self.height
        elif self.sval == 'Z':
            starty = self.y - self.height/2
            delta = -self.height/2
        else:
            starty = self.y - self.height
            delta = 0.0
	dict = {}
        ptuple = [self.x, starty,  self.period/8, delta, 7*self.period/8]
        dict['d'] = ptuple
        dict['stroke'] = "black"
        dict['fill'] = "none"
        dict['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'H'

        return dict

    def create_z_node(self):
        dict = {}

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
        dict['d'] = "M%f,%f  l%f, %f h%f" % ptuple
        dict['stroke'] = "black"
        dict['fill'] = "none"
        dict['stroke-linecap'] = "square"
        self.x += self.period
        self.sval = 'Z'
        
        return dict

    def create_bus_node(self, title, color):

        gelem = []

        oelem = {}

        otuple = (self.x, self.y - self.height/2, self.period/8, -self.height/2, 6*self.period/8.0, self.period/8.0, self.height/2, -self.period/8, self.height/2.0, -6*self.period/8.0)
        oelem['d']= "M%f,%f l%f,%f h%f l%f,%f l%f,%f h%f Z" % otuple
        oelem['stroke'] = "black"
        oelem['fill'] = color
        oelem['stroke-linecap'] = "square"

        gelem.append(oelem)
        
        telem = {}
        telem['x'] =  "%f" %  (self.x + self.period/2)
        telem['y'] = "%f" % (self.y - self.height/4.0-0.3)
        telem['font-family'] = "Helvetica"
        telem['font-size'] = "%f" % (self.height/1.9)
        telem['text-anchor'] = "middle"
        telem['text'] = title
        
        gelem.append(telem)
        self.x += self.period
        self.sval = 'Z'
        return gelem


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
