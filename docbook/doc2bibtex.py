#!/usr/bin/python

"""

Here we take any input docbook file, scan for any <bibliography id=foo> items, and create a resulting foo.bib bibtex file. This isn't -totally- trivial as we still need to figure out the -type- of the article that we're dealing with.

We only process biblioentries, i.e. "raw" data

consider
http://www-h.eng.cam.ac.uk/help/tpl/textprocessing/bibliographies.html

should we ever want multiple bibliographies 

consider citetitle, type = foo


Potential citetytle options are:
article
bbs
book
cdrom
chapter
dvd
emailmessage
gopher
journal
manuscript
newsposting
part
refentry
section
series
set
webpage
wiki

We need some way of mapping these onto bibtex entries, which are:


@article
    An article from a journal or magazine. 
@book
    A book with an explicit publisher. 
@booklet
    A work that is printed and bound, but without a named publisher or sponsoring institution. 
@conference
    The same as inproceedings. 
@inbook
    A part of a book, which may be a chapter (or section or whatever) and/or a range of pages. 
@incollection
    A part of a book having its own title. 
@inproceedings
    An article in a conference proceedings. 
@manual
    Technical documentation. 
@mastersthesis
    A Master's thesis. 
@misc
    Use this type when nothing else fits. 
@phdthesis
    A PhD thesis. 
@proceedings
    The proceedings of a conference. 
@techreport
    A report published by a school or other institution, usually numbered within a series. 
@unpublished
    A document having an author and title, but not formally published.
    


So, the mapping is:

If there's a book title, then :
   if there's nothing else, it's a book
   if there's a chapter/section, it's an inbook

<biblioentry>                     
<authorgroup>
  <author><firstname>W.</firstname><surname>Clinton</surname></author>
  <author><firstname>B.</firstname><surname>Jeltsin</surname></author>
</authorgroup>
<citetitle pubwork="article">Ruling the World</citetitle>
<citetitle pubwork="journal">Journal of Applied Politics</citetitle>
<volumenum>42</volumenum>
<artpagenums>113-152</artpagenums>
<pubdate>1999</pubdate>
</biblioentry>      

So, mapping this to docbook shouldn't be all -that- hard. And the other things I want to support are:

data sheets
app notes
books
chapters in books
journal articles
URLs to datasheet links, app-note links, that sort of thing.


We will use a similar framework to the other docbook parser, but it will be much more compact.



"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import DocbookBibElement
            
        
    
class dispatcher:
    elements = {}
    elements["bibliography"] = DocbookBibElement.Bibliography
    elements["biblioentry"] = DocbookBibElement.BiblioEntry
    elements["authorgroup"] = DocbookBibElement.AuthorGroup
    elements["author"] = DocbookBibElement.Author
    elements["firstname"] = DocbookBibElement.Firstname
    elements["surname"] = DocbookBibElement.Surname
    elements["citetitle"] = DocbookBibElement.Citetitle
    elements["volumenum"] = DocbookBibElement.VolumeNum
    elements["artpagenums"] = DocbookBibElement.ArtPageNums
    elements["pubdate"] = DocbookBibElement.PubDate
    elements["publisher"] = DocbookBibElement.Publisher
    elements["publishername"] = DocbookBibElement.PublisherName
    elements["copyright"] = DocbookBibElement.Copyright
    elements["year"] = DocbookBibElement.Year
    elements["holder"] = DocbookBibElement.Holder
    elements["editor"] = DocbookBibElement.Editor
    elements["isbn"] = DocbookBibElement.ISBN
    
    
    def __call__(self, element, attrs):
        return self.elements[element](attrs)

class DBBibloHandler(ContentHandler):
        
    def __init__(self, bibtexoutput):
        self.elementobjs = []
        self.edispatch = dispatcher()
        self.outproc = bibtexoutput

        self.inBibliography = False
        
    def startElement(self, name, attrs):
        if name == "bibliography":
            self.inBibliography = True
            self.elementobjs.append(self.edispatch(name, attrs))
        else:
            if self.inBibliography:
                self.elementobjs.append(self.edispatch(name, attrs))
        

    def characters(self, characters):
        if self.inBibliography:
            self.elementobjs[-1].append(characters)


    def endElement(self, name):
        if len(self.elementobjs) > 1:
            x = self.elementobjs.pop()
            self.elementobjs[-1].append(x)

        else:
            if self.inBibliography:
                print "last element!"
                self.outproc.finalize(self.elementobjs.pop())
                self.inBibliography = False
                

class BibtexDoc:
    def finalize(self, obj):
        # this is where we write out the collection of bibitems"

        #first, create the appropriate bibtex file:
        bib = obj

        filename = bib.id + ".bib"

        fid = file(filename, 'w')

        for i in bib.bibitems:
            fid.write(i.to_bibtex())

        fid.close()

import sys

def main():


    filename = sys.argv[1]
    f = file(filename, 'r')

    output = BibtexDoc()
    
    dbh = DBBibloHandler(output)
    saxparser = make_parser()

    saxparser.setContentHandler(dbh)
    saxparser.parse(f)

    
if __name__ == "__main__":
    main()
