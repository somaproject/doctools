#!/usr/bin/python

import re


def trimstr(str):
     p = re.compile(r"^\s+", re.MULTILINE)
     q = re.compile(r"\s$");
     
     return q.sub("", p.sub("", str))

def newlinetospace(str):
     p = re.compile(r"\n", re.MULTILINE)
     return p.sub(" ", str); 

class DocbookElement:
    
    def __init__(self, attrs):

        self.attrs = attrs
        self.chars = ""

    def append(self, obj):
        pass

    def to_latex(self):
        return self.chars


class Generic(DocbookElement):
     def append(self, obj):
          pass
     def to_latex(self):
          return ""
     


# FOOs classes (note the S) are parent classses

class Components(DocbookElement):
    def __init__(self, attrs):
        self.title = ""
        self.author = ""
        DocbookElement.__init__(self, attrs)
        

class Inlines(DocbookElement):

    def append(self, obj):
        self.chars += str(obj)

    
class Blocks(DocbookElement):
    def append(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        else:
            self.chars += obj.to_latex()

class Sections(DocbookElement):
    pass


class Metas(DocbookElement):
    def append(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
             self.chars += str(obj)
        else:
             self.chars += obj.to_latex()

# COMPONENTS ###############################################################

class Article(Components):

    def append(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        elif isinstance(obj, Title):
            self.title = obj.chars
        elif isinstance(obj, Author):
            self.author = obj.chars
        elif isinstance(obj, ArticleInfo):
             self.author = obj.author
             self.title = obj.title
        else:
            self.chars += obj.to_latex()

    def to_latex(self):
        return self.chars

# SECTIONS ##################################################################

class Section(Sections):
    depth = 0
    def __init__(self, attrs):
        self.__class__.depth += 1
        self.title = ""
        Sections.__init__(self, attrs)
        
    def append(self, obj):
        print "Section appending", type(obj)
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        elif isinstance(obj,  Title):
            print "section title is", obj.chars
            self.title = obj.chars
        else:
            self.chars += obj.to_latex()

    def to_latex(self):
        sectstr =""
        if self.__class__.depth == 1 :
            secstr = "\section"
        elif self.__class__.depth == 2:
            secstr = "\subsection"
        elif self.__class__.depth == 3:
            secstr = "\subsubsection"
        elif self.__class__.depth ==4 :
            secstr = "\subsubsubsection"
        else:
            secstr = "\section"
            print "sections too deep!"

        header = "%s{%s}" % (secstr, self.title)
        self.__class__.depth -= 1
        
        return header + self.chars


class Bibliography(Sections):
     def to_latex(self):
          # Yea, here's where we depend on this integrating with LaTeX
          return "\n\\bibliographystyle{amsplain}\\bibliography{" + self.attrs["id"] + "}\n"
     
     
# METAS #####################################################################
class ArticleInfo(Metas):

    def append(self, obj):
         
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        elif isinstance(obj, Title):
            self.title = obj.chars
        elif isinstance(obj, Author):
            self.author = obj.to_latex()
        else:
            self.chars += obj.to_latex()

    def to_latex(self):
        return self.chars


class Author(Metas):
     def to_latex(self):
          return newlinetospace(trimstr(self.chars))

class Title(Metas):
    pass

class Firstname(Metas):
     pass

class Surname(Metas):
     pass
        
# BLOCKS ####################################################################
class Para(Blocks):
    
    def to_latex(self):
        return "%s\n" % self.chars

class Equation(Blocks):

    def to_latex(self):
        return "\n\\begin{equation}\n%s\n\\end{equation}" % trimstr(self.chars)

class Figure(Blocks):
    def __init__(self, attrs):
        self.caption = ""
        self.fileref = ""
        self.fileformat = ""
        self.tite = ""
        
        Blocks.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, MediaObject):
            self.caption = obj.caption
            self.fileref = obj.dataobj.fileref
            self.fileformat = obj.dataobj.fileformat
            self.width = obj.dataobj.width
        elif isinstance(obj, Title):
             self.title = obj.chars
             

    def to_latex(self):
        # here we go : )
        str = "\n\\begin{figure}[!h]\n"
        str += "\\centering\n"
        str += "\\includegraphics"
        if self.width != "":
             str += "[width=" + self.width + "]"
        str += "{" + self.fileref + "}\n"
        
        if self.title != "" and self.caption == "":
             
             str += "\\caption{" + self.title + "}\n"
        elif self.title == "" and self.caption != "":
             str += "\\caption{" + self.caption + "}\n"
        elif self.title != "" and self.caption != "":
             str += "\\caption{\textbf{" + self.caption + ":} " + self.title + "}\n"

        str += "\\end{figure}"

        return str

class Caption(Blocks):
    def append(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            self.chars += str(obj)
        else:
            self.chars += obj.to_latex()

        

# INLINE ####################################################################
class Emphasis(Inlines):
    def to_latex(self):
        return "\\textit{%s}" % self.chars

class ImageData(Inlines):
    pass

class ImageObject(Inlines):
    def __init__(self, attrs):
        self.fileref = ""
        self.fileformat = ""
        self.width = ""
        Inlines.__init__(self, attrs)

    def append(self, obj):
        if isinstance(obj, ImageData):
            self.fileref = obj.attrs["fileref"]
            self.fileformat = obj.attrs["format"]
            self.width = obj.attrs.get("contentwidth", "")
            


class MediaObject(Inlines):
    """ Really, I wish I knew why there were all these damn objects"""
    def __init__(self, attrs):
        self.dataobj = None
        self.caption = ""
        Inlines.__init__(self, attrs)

        
    def append(self, obj):
        if isinstance(obj, ImageObject):
            self.dataobj = obj
        elif isinstance(obj, Caption):
            self.caption = trimstr(obj.to_latex())
    

class Xref(Inlines):
    def to_latex(self):
        return "\cite{" + self.attrs["linkend"] + "}"
    

# CUSTOM ------------------------------------------------------------------

class Signal(Inlines):
     
     def to_latex(self):
          print self.chars
          # for signals, we regexp out the relevant bits
          rebits = re.compile(r"\s*(\w+)(\[([0-9:]+)\])*\s*")
          bm = rebits.match(self.chars)
          bits = bm.groups()
          signal = "\\textrm{%s}" % bits[0]  # get signal name
          if self.attrs.get("active") == "low":
               signal = "\\bar{" + signal +  "}"

          if bits[2]:
               signal += "_\\textrm{" + bits[2] + "}"
               
          return "$%s$" % signal
     
        
def main():
    x = Inline("")
    x.test()
    x.inc()
    x.test()

    y = Inline("")
    y.test()
    




if __name__ == "__main__":
    main()
    
