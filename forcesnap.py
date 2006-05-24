import sys

## from xml.sax import make_parser, handler

## class ForceToGrid(handler.ContentHandler):

##     def __init__(self):
##         pass
    

##     def startElement(self, name, attrs):
##         if name == "rect":
##             print "rect!"
            
## ##         self._elems = self._elems + 1
## ##         self._attrs = self._attrs + len(attrs)
## ##         self._elem_types[name] = self._elem_types.get(name, 0) + 1

## ##         for name in attrs.keys():
## ##             self._attr_types[name] = self._attr_types.get(name, 0) + 1

##     def endDocument(self):
##         pass

            
## parser = make_parser()
## parser.setContentHandler(ForceToGrid())
## parser.parse(sys.argv[1])
import sys
from xml.dom import minidom, Node

"""

    <rect
       y="83.75"
       x="99.999954"
       height="12.499997"
       width="46.875011"


"""

def forceSnap(x, grid, thold = None):
    """
    Takes in a value and a grid level and
    snaps to that grid

    grid is in whatever the default units are.

    
    """

    if thold == None:
        thold = grid * 0.1 # 10% snap

    gridmult  = 1/float(grid)
    y  = round(x * gridmult) / gridmult  # nearest grid position

    if (abs(x - y) < thold) and (abs(x-y) > 0.0):
        return y
    else:
        return False
    
    

    
       
def walk(parent):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if node.nodeName == "rect":
                print "rect!"
                
                attrs = node.attributes                             # [2]

                for attrname in ['x', 'y', 'width', 'height']:
                    
                    v = float(attrs[attrname].nodeValue)
                    vs = forceSnap(v, 0.125)
                    if vs:
                        print attrname, v, "-->",  vs
                        attrs[attrname].nodeValue = str(vs)
            walk(node)
            


def showNode(node):
    if node.nodeType == Node.ELEMENT_NODE:
        print 'Element name: %s' % node.nodeName
        for (name, value) in node.attributes.items():
            print '    Attr -- Name: %s  Value: %s' % (name, value)
        if node.attributes.get('ID') is not None:
            print '    ID: %s' % node.attributes.get('ID').value

def main():
    doc = minidom.parse(sys.argv[1])
    node = doc.documentElement
    walk(node)

    doc.writexml(file(sys.argv[2], 'w'))
    
if __name__ == '__main__':
    main()
    #print forceSnap(71.25, 0.125)
    pass

    


