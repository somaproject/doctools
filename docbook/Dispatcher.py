#!/usr/bin/python


"""
Dispatcher class: responsible for, well, dispatching all of the tags to objects. We call this in the form :

dispatcher(elementname, attrs)
and are returned an object. The root of this is a giant dict that performs an element-to-new-object mapping, and returns the relevant object.


"""

import DocbookElement

class dispatcher:
    elements = {}
    elements["article"] = DocbookElement.Article
    elements["section"] = DocbookElement.Section
    elements["title"] = DocbookElement.Title
    elements["author"] = DocbookElement.Author
    elements["para"] = DocbookElement.Para
    elements["emphasis"] = DocbookElement.Emphasis
    elements["equation"] = DocbookElement.Equation
    elements["imagedata"] = DocbookElement.ImageData
    elements["imageobject"] = DocbookElement.ImageObject
    elements["mediaobject"] = DocbookElement.MediaObject
    elements["figure"] = DocbookElement.Figure
    elements["caption"] = DocbookElement.Caption
    elements["xref"] = DocbookElement.Xref
    elements["bibliography"] = DocbookElement.Bibliography
    elements["signal"] = DocbookElement.Signal
    elements["articleinfo"] = DocbookElement.ArticleInfo
    elements["firstname"] = DocbookElement.Firstname
    elements["surname"] = DocbookElement.Surname

    def __call__(self, element, attrs):
        print "processing", element
        if self.elements.has_key(element):
            return self.elements[element](attrs)
        else:
            return DocbookElement.Generic(attrs)

