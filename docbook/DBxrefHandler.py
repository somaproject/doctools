

"""
as we encounter each new element, we place it on the stack
then, as we pop them off, we check:
   if it was a "title" element, we append its title to the previous element
   if it had an "id", we add it to the hash, calling an error if it already existsed

"""
    

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class DBxrefHandler(ContentHandler):

    def __init__(self):
        self.IDs = {}
        self.elementobjs = []
        
    def startElement(self, name, attrs):
        self.elementobjs.append(element(name, attrs))
        

    def characters(self, characters):
        self.elementobjs[-1].appendchars(characters)


    def endElement(self, name):
        if len(self.elementobjs) > 1:
            x = self.elementobjs.pop()
            if name == "title":
                self.elementobjs[-1].title = x.chars
            elif x.attrs.has_key('id'):
                if self.IDs.has_key(str(x.attrs['id'])):
                    print "ERROR! ID %s already exists!" % x.attrs['id']
                else:
                    self.IDs[str(x.attrs['id'])] = (str(x.name), str(x.title))
        else:
            print self.IDs
            

class element:
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs
        self.chars = ""
        self.title = None

    def appendchars(self, chars):
        self.chars += chars
        

