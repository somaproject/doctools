class Citation:
    def __init__(self):
        self.id = None
        self.authors = []
        self.citetitles = {}
        self.volumenum = None
        self.number = None
        self.pages = None
        self.month = None
        self.year = None
        self.copyright = None
        self.ISBN = None
        self.URL = None
        self.editor = None
        self.edition = None
        self.booktitle = None
        self.publisher = None


class DocbookBibElement:
    
    def __init__(self, attrs):
        self.attrs = attrs
        self.chars = ""

    def append(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        
    def to_bibtex(self):
        return self.chars

class Bibliography(DocbookBibElement):
    def __init__(self, attrs):
        self.bibitems = []
        self.id = attrs["id"]
        

    def append(self, obj):
        if isinstance(obj, BiblioEntry):
            self.bibitems.append(obj)


class BiblioEntry(DocbookBibElement):
    def __init__(self, attrs):
        self.bibentry = Citation()
        DocbookBibElement.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, AuthorGroup):
            self.bibentry.authors = obj.authors
        elif isinstance(obj, Citetitle):
            self.bibentry.citetitles[obj.attrs["pubwork"]] = obj.chars
        elif isinstance(obj, VolumeNum):
            self.bibentry.volumenum = obj.chars
        elif isinstance(obj, ArtPageNums):
            self.bibentry.pages = obj.chars
        elif isinstance(obj, PubDate):
            self.bibentry.year = obj.getyear()
            self.bibentry.month = obj.getmonth()
        elif isinstance(obj, Copyright):
            if not self.bibentry.year:
                self.bibentry.year =  obj.year
            self.bibentry.copyright = obj.holder
        elif isinstance(obj, Publisher):
            self.bibentry.publisher = obj.pubname
        elif isinstance(obj, Editor):
            self.bibentry.editor = obj.firstname + obj.surname
        elif isinstance(obj, ISBN):
            self.bibentry.ISBN = obj.chars
           
            
    def to_bibtex(self):
        # first, we identify what type it is:
        str = "\n\n"
        if self.bibentry.citetitles.has_key("article"):
            # it's an article:
            str+="@article{"
            mode = "journal"
        elif self.bibentry.citetitles.has_key("book"):
            if self.bibentry.citetitles.has_key("section") or self.bibentry.citetitles.has_key("chapter"):
                str += "@inbook{"
                mode = "inbook"
            else:
                str +="@book{"
                mode = "book"
        
            
        str += self.attrs['id'] + ',\n'
                
        # add authors
        if len(self.bibentry.authors)  > 0:
            
            str += 'author = "' + self.bibentry.authors.pop(0)
            for i in self.bibentry.authors:
                str += " and " + i
                
            str += '",\n'

        # TITLE IDENTIFICATION
            
        if mode == "journal":
            # it's an article:
            str += 'title="%s",\n' % self.bibentry.citetitles["article"]

        if mode == "book":
            str += 'title="%s",\n' % self.bibentry.citetitles["book"]

        # JOURNAL INFO
        if mode == "journal":
            str += 'journal="%s",\n' % self.bibentry.citetitles["journal"]

        if self.bibentry.volumenum:
            str += 'volume="%s",\n' % self.bibentry.volumenum

        # page identification
        if mode == "journal":
            str += 'pages="%s",\n' % self.bibentry.pages

        # Dates:
        if self.bibentry.month:
            str += 'month="%s",\n' % self.bibentry.month
        if self.bibentry.year:
            str += 'year="%s",\n' % self.bibentry.year
            
        #Publisher
        if self.bibentry.publisher:
            str += 'publisher="%s",\n' % self.bibentry.publisher

        # copyright
        if self.bibentry.copyright:
            str += 'copyright="%s",\n' % self.bibentry.copyright

        #ISBN :
        if self.bibentry.ISBN:
            str += 'isbn="%s",\n' % self.bibentry.ISBN
        str += "}"
        
        return str
    
            

class AuthorGroup(DocbookBibElement):
    def __init__(self, attrs):
        self.authors = []
        DocbookBibElement.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, Author):
            str = obj.firstname + ' '  + obj.surname
            self.authors.append(str)


class Author(DocbookBibElement):
    def __init__(self, attrs):
        self.firstname = ""
        self.surname = ""


    def append(self, obj):
        if isinstance(obj, Surname):
            self.surname = obj.chars
        elif isinstance(obj, Firstname):
            self.firstname = obj.chars

class Editor(DocbookBibElement):
    def __init__(self, attrs):
        self.firstname = ""
        self.surname = ""


    def append(self, obj):
        if isinstance(obj, Surname):
            self.surname = obj.chars
        elif isinstance(obj, Firstname):
            self.firstname = obj.chars


class Firstname(DocbookBibElement):
    pass

class Surname(DocbookBibElement):
    pass

class Citetitle(DocbookBibElement):
    pass

class VolumeNum(DocbookBibElement):
    pass 

class ArtPageNums(DocbookBibElement):
    pass

import re
class PubDate(DocbookBibElement):

    def getyear(self):
        # parses self.chars to get the year
        yearre = re.compile(r'.*(\d\d\d\d).*')
        m = yearre.match(self.chars)
        return m.group(1)
    def getmonth(self):
        # parses self.chars to get the month
        monthre = re.compile(r'([a-zA-Z]*)')
        m = monthre.match(self.chars)
        return m.group(1)


class Publisher(DocbookBibElement):
    def __init__(self, attrs):
        self.pubname = None
        DocbookBibElement.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, PublisherName):
            self.pubname = obj.chars
            
        

class PublisherName(DocbookBibElement):
    pass

class Copyright(DocbookBibElement):
    def __init__(self, attrs):
        self.year = None
        self.holder = None

        DocbookBibElement.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, Year):
            self.year = obj.chars
        elif isinstance(obj, Holder):
            self.holder = obj.chars

class Year(DocbookBibElement):
    pass

class Holder(DocbookBibElement):
    pass


class ISBN(DocbookBibElement):
    pass
