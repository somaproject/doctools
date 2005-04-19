#!/usr/bin/python
"""

This is our latex preprocessor. I've given up the ghost and decided to process documentation this way because it is much more flexible and less likely to make me very sad.

---------------------------------------------------------------------
INCLUSION and HIERARCHY
---------------------------------------------------------------------

That said, there are challenges with the recursive nature of the inclusion. So we're defining our own preprocessor directive,

\include{blah/}{foo.tex}

and we append blah/ onto the front 




Most of our types are of the form
\begin{foo}


\end{foo}

which will call a corresponding module foo

We keep a hash of foo->foo() mappings, and build up regexps for each foo.


recursive(filename, base):
   1. read entire file
   2. replace all \includegraphics{foo} with \includegraphics{basefoo}
   3. then find includes, call recursive

"""

import re
import os
import sys
import StringIO

import memmap
import timing
import svg2boundedPDF

def parser(moddict, fid):
    """
    moddict is the dictionary of section-> function mappings

    This code will perform the translation

    
    
    """

    # build up regular expression table
    reStartDict = {}
    reEndDict = {}
    for k, v in moddict.iteritems():
        
        reStartDict[k] = re.compile(r"\s*\\begin{%s}{(.+)}\s*" % k);
        reEndDict[k] = re.compile(r"\s*\\end{%s}\s*" % k);
        
    mod = None
    l = " "
    while not l == "":
       
        l = fid.readline()
        if l == "":
            break; 
            
        for k, v in moddict.iteritems():
            if reStartDict[k].match(l):
            
                mod = moddict[k]
                matchText = ""
                id = reStartDict[k].match(l).group(1)
                l = fid.readline()
            
                while not l == "" and not reEndDict[k].match(l):
                    matchText += l
                    l = fid.readline()
            
                print v(matchText, id)
        print l, 

def memmapfun(string, id):
    
    tm = memmap.TexMemMap()
    
    memmap.memmap2tex(string, tm)
    return tm.generate()

def timingfun(string, id):
    fid = file("%s.timing" % id, 'w') 
    fid.write(string)
    fid.close()
    timing.parseTiming("%s.timing" % id)
    
    # here's where we perform the actual bounded pdf conversion
    svg2boundedPDF.svg2boundedPDF("%s.timing.svg" % id)
    return "\includegraphics[scale=0.8]{%s.timing.pdf}" % id

    
def recursive(filename, base):
    fid = file(filename)

    graphicsre = re.compile(r"\\includegraphics\[(.*)]{(.+)}")
    includere = re.compile(r"\\import{(.*)}{(.+)}")
    resultstr = "";
    for l in fid.readlines():
        # if there's an includegraphicsxs
        if graphicsre.match(l):
            # perform the substitution
            res = graphicsre.match(l)
            args = res.group(1)
            filename = res.group(2)

            resultstr += "\n\\includegraphics[" + args + "]{" \
                         + base + filename + "}"
            
        elif includere.match(l):
            # text !
            subfilename = includere.match(l).group(2)
            subprefix = includere.match(l).group(1)
            resultstr += recursive(subprefix + subfilename,
                                   subprefix)
            
        else:
            resultstr += l
    return resultstr

def main():
    s = recursive(sys.argv[1], "")
    sio = StringIO.StringIO(s)


    foo = {}
    foo["memmap"] = memmapfun
    foo["timing"] = timingfun
    
    parser(foo, sio)


if __name__ == "__main__":
    main()

