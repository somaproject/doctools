#!/usr/bin/python
"""
   This code is my attempt to resolve some of the challenges faced by me when trying to use docbook to output non-horrible math text, and creating non-horrible-looking LaTeX output. The plan is as follows:


The normal signal chain will be to process our modified docbook-latex-stuff into something that's valid docbook, at the very least. Here, we'll try to follow the conventions of :

http://www.sagehill.net/docbookxsl/TexMath.html

but no promises. In particular, that appears to have no real support for in-line equations. So hmm, we'll instead create:

<math></math> to surround $$
and
<eqn></eqn> to surround \begin{equation} and \end{equation}. To reference them in the text... will be a pickle.


We'll use the SAX engine, based on the idea that it'll be easier to handle various classes of nesting...



What if we do things really recursively...
    i.e. if we're at the end of a section, we take the current 'body' text and wrap it in \section{foo}, and do things like increment/decrement our section object?
    This is all terribly stack-based. Wow, maybe I should do this more in something like, say, scheme.

    so, the problem is, we need ways of remembering 'what' we're inside of, and then when we leave it, serialzing that output to disk. That's not going to be all that easy.
    for example, when we're inside a paragraph, how do we remember that we're also in a caption in a figure?


    What if you create new objects, and push them on a stack, and then call them with associated objects? I mean, what if, for exmple, para creates a para object, and we add chars to a para object, and then should we encounter emphasis, we create an emphasis object, and when we're done, we pass the emphasis object to the para object, which knows to serialize it into 

    
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import Dispatcher
import DocbookElement


class DBLaTeXHandler(ContentHandler):

    def __init__(self, texoutput):
        self.elementobjs = []
        self.edispatch = Dispatcher.dispatcher()
        self.outproc = texoutput
        
    def startElement(self, name, attrs):
        self.elementobjs.append(self.edispatch(name, attrs))
        

    def characters(self, characters):
        self.elementobjs[-1].append(characters)


    def endElement(self, name):
        if len(self.elementobjs) > 1:
            x = self.elementobjs.pop()
            self.elementobjs[-1].append(x)

        else:
            print "last element!"
            self.outproc.finalize(self.elementobjs.pop())



import sys
from LatexDoc import * 

def main():


    filename = sys.argv[1]
    f = file(filename, 'r')

    output = LatexDoc(sys.argv[2])
    
    dbh = DBLaTeXHandler(output)
    saxparser = make_parser()

    saxparser.setContentHandler(dbh)
    saxparser.parse(f)

    
if __name__ == "__main__":
    main()
