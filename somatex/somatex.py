#!/usr/bin/python
"""

This is our latex preprocessor.

options:

somatex foo.tex:
  wraps foo.tex, recursively builds it

somatex -standalone foo.tex:
  recursively build foo.tex, don't wrap

somatex -deponly foo.tex:
  only build the external dependencies for foo.tex, don't actually latex the file. This also recurses in this manner.

somatex -norecurse foo.tex:
  don't recurse


"""

import re
import os
import sys
import md5
import StringIO
sys.path.append("../")
import memmap
import timing
from svg2boundedPDF import *
import events
import wrappers

def hasChanged(oldFile, newFile):
    """ is newfile newer than oldfile, or are their timestamps
    the same? """

    if os.path.isfile(oldFile) and os.path.isfile(newFile):
        
        return os.stat(newFile).st_mtime < os.stat(oldFile).st_mtime
    else:
        return True
    
def genLocalDeps(textstr, buildDir, baseDir):

    s1 = genGraphicsDeps(textstr, buildDir, baseDir)
    s2 = genCustomTex(s1, buildDir, baseDir)

    return s2


def genGraphicsDeps(textstr, buildDir, baseDir):
    """ find everything that's
    in an \includegraphics[blah][foo.ext}

    identify the extension

    perform the conversion

    place the result in builddir

    modify the string

    replace the appropriate text file.

    if there's not a match, we change the build dir

    
    
    """

    # replace the PDFs with the relevant files:

    igre = re.compile(r"(\\includegraphics\[.*\]){(.+)\.(\w+)}", )

    resultstr = ""
    for s in textstr.split('\n'):
        m = igre.search(s)

        if m:
            include = m.group(1)
            filebase = m.group(2)
            fileext = m.group(3)


            if fileext == "svg" :
                #perform svg conversion
                if hasChanged("%s/%s.%s" % (baseDir, filebase, fileext),
                              "%s/%s/%s.%s.pdf" % (baseDir, buildDir,
                                                filebase, fileext)):
                    
                    svg2boundedPDF("%s/%s.%s" % (baseDir, filebase, fileext),
                                   "%s/%s/%s.%s.pdf" % (baseDir, buildDir,
                                                     filebase,fileext))

                resultstr += "%s{%s.%s.pdf}\n" % (include, filebase, fileext)
            else:
                # native type?
                resultstr += "%s{%s/%s.%s}\n" % (include, buildDir,
                                               filebase, fileext)
                
        else:
            resultstr += "%s\n" % s

    return resultstr

        
def genCustomTex(texstring, buildDir, baseDir):
    """
    moddict is the dictionary of section-> function mappings

    This code will perform the translation, and returns the file
        
    """

    fid = StringIO.StringIO(texstring)

    moddict = {}
    moddict["memmap"] = memmapfun
    moddict["timing"] = timingfun
    moddict["event"] = eventsfun
    moddict["dspcmd"] = dspcmdfun

    # build up regular expression table
    reStartDict = {}
    reEndDict = {}
    for k, v in moddict.iteritems():
        
        reStartDict[k] = re.compile(r"\s*\\begin{%s}{(.+)}\s*" % k);
        reEndDict[k] = re.compile(r"\s*\\end{%s}\s*" % k);
        
    mod = None
    resultstr = "" 
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

                
                resultstr += v(matchText.strip(), id, buildDir, baseDir)
                
                if reEndDict[k].match(l):
                    l = fid.readline()
        
        resultstr += l

    return resultstr


def memmapfun(string, id, buildDir, baseDir):
    tm = memmap.TexMemMap(id)
    
    memmap.memmap2tex(string, tm)
    return tm.generate()

def eventsfun(string, id, buildDir, baseDir):

    
    m = md5.new()
    m.update(string)

    fname = "%s/%s/%s.%s.event.pdf" % (baseDir, buildDir,
                                        id, m.hexdigest())
    
    if not os.path.isfile(fname):        
        print "generating event ", fname
    
        e = events.Event(string.strip())
    
        e.generateSVG()
        estr = e.getText()
        svgStringToBoundedPDF(estr, fname)

    iname = "%s.%s.event.pdf" % (id, m.hexdigest())

    return r"\begin{center}\includegraphics[scale=1.5]{%s}\end{center}" % iname


def dspcmdfun(string, id, buildDir, baseDir):

    m = md5.new()
    m.update(string)

    fname = "%s/%s/%s.%s.dspcmd.pdf" % (baseDir, buildDir,
                                        id, m.hexdigest())
    
    if not os.path.isfile(fname):        
        print "generating dspcmd ", fname
    
        dc = events.DSPcmd(string.strip())
    
        dc.generateSVG()
        dspcmdstr = dc.getText()
    
        svgStringToBoundedPDF(dspcmdstr, fname)

    iname = "%s.%s.dspcmd.pdf" % (id, m.hexdigest())

    return r"\begin{center}\includegraphics[scale=1.5]{%s}\end{center}" % iname



def timingfun(string, id, buildDir, baseDir):
    
    m = md5.new()
    m.update(string)

    fname = "%s/%s/%s.%s.timing.pdf" % (baseDir, buildDir,
                                        id, m.hexdigest())
    
    if not os.path.isfile(fname):        
        print "generating timing ", fname
        
        timing.parseTiming(string, "%s/%s/%s.timing.svg" % (baseDir,
                                                            buildDir, id))
    
        # here's where we perform the actual bounded pdf conversion
        svg2boundedPDF("%s/%s/%s.timing.svg" % (baseDir, buildDir, id),
                       "%s/%s/%s.%s.timing.pdf" % (baseDir, buildDir,
                                                   id, m.hexdigest()))

    
    x =  r"""\begin{center}
    \includegraphics[scale=0.8]{%s.%s.timing.pdf}
    \end{center}""" % (id, m.hexdigest())

    return x

def buildRecursive(filestr, buildDir, baseDir):
    """ simply build all sub-dependents"""
    

    includere = re.compile(r".*\\import{(.*)}{(.+)}")
    for l in filestr.split("\n"):
        if includere.match(l):
            # text !
            subfilename = includere.match(l).group(2)
            subprefix = includere.match(l).group(1)
            
            somatex(subfilename, buildDir, "%s/%s" % (baseDir, subprefix))
            
    
def recursive(filename, base):
    #print "CALLING RECURSIVE WITH ", filename, base
    fid = file(filename)

    graphicsre = re.compile(r".*\\includegraphics\[(.*)]{(.+)}")
    includere = re.compile(r".*\\import{(.*)}{(.+)}")
    resultstr = "";
    for l in fid.readlines():
        # if there's an includegraphicsxs
        if graphicsre.match(l):
            # perform the substitution
            res = graphicsre.match(l)
            args = res.group(1)
            filename = res.group(2)

            resultstr += r"\n\includegraphics[" + args + "]{" \
                         + base + filename + "}"
            
        elif includere.match(l):
            # text !
            subfilename = includere.match(l).group(2)
            subprefix = includere.match(l).group(1)
            resultstr += recursive(base + subprefix + subfilename,
                                   base + subprefix)
        else:
            resultstr += l
    return resultstr

from optparse import OptionParser


def somatex(filename, buildDir, baseDir):
    """
    filename = the latex file we're going to try and build

    baseDir : this might more correctly be called the target working
    directory. Even though somatex might have a different cwd, this should
    point to the desired wd.

    
    buildDir = normally BUILD, the place where we dump all of our
    outputs relative to baseDir
    
    """

    filestr = file("%s/%s" % (baseDir, filename)).read()

    if not os.path.isdir("%s/%s" % (baseDir, buildDir)):
        os.mkdir("%s/%s" % (baseDir, buildDir))
        

    fre = re.compile(".+/(.+).tex")
    m = fre.match("%s/%s" % (baseDir, filename))

    fbase = m.group(1)
    fid = file("%s/%s/%s.somatex" % (baseDir, buildDir, fbase), 'w')


    buildRecursive(filestr, buildDir, baseDir)
    
    resultstr = genLocalDeps(filestr, buildDir, baseDir)

    resultstr = includeSubfiles(resultstr, buildDir, baseDir)

    fid.write(resultstr)

    fid.close()
    

def includeSubfiles(filestr, buildDir, baseDir):
    """ include all subfiles """


    resultstr = ""
    
    includere = re.compile(r".*\\import{(.*)}{(.+)\.tex}")
    subre = re.compile(r"(\\includegraphics\[.+\]{)(.+})")
    for l in filestr.split("\n"):
        if includere.match(l):
            # text !
            
            subfilenamebase = includere.match(l).group(2)
            subprefix = includere.match(l).group(1)

            #print subfilename, buildDir, subprefix

            fid = file("%s/%s/%s/%s.somatex" % (baseDir, subprefix,
                                                buildDir, subfilenamebase))
            instr = fid.read()
            s = subre.sub("\g<1>../%s/%s/\g<2>" % (subprefix, buildDir), instr) 

            hdr = """%% --------------------------------------------------------\n%% %s\n%% --------------------------------------------------------\n """  % fid.name

            resultstr += (hdr + s)
            
        else:
            resultstr += "%s\n" % l

    return resultstr


def wrapSomaTex(filename, buildDir, baseDir):
    """ simply wrap the file """

    fnamere = re.compile("(.+)\.tex")
    m = fnamere.match(filename)
    
    sfile = file("%s/%s.somatex" % (buildDir, m.group(1)))

    fout = file("%s/%s.wrapped.somatex" % (buildDir, m.group(1)), 'w')

    fout.write(wrappers.header)
    fout.write(sfile.read())
    fout.write(wrappers.footer)
    fout.close()
    sfile.close()
                 
def makePDF(filename, buildDir, baseDir, wrapped):
    pathname = os.path.dirname(sys.argv[0])  

    LATEXCMD = "pdflatex"
    os.chdir(buildDir)

    os.environ["TEXINPUTS"] = ":../%s/" % (pathname)


    fre = re.compile("(.+).tex")
    filenamebase = fre.match(filename).group(1)
    if wrapped:
        cmd = "%s %s.wrapped.somatex" % (LATEXCMD, filenamebase)
    else:
        cmd = "%s %s.somatex" % (LATEXCMD, filenamebase)

    
    os.system(cmd)
             
        
    #os.chdir("../")
    
    
    
    
    
def main():

    parser = OptionParser()
    parser.add_option("-s", "--standalone",  action="store_true",
                      dest="standalone",
                      default = False)
    parser.add_option("-b", "--builddir", action="store", type="string",
                      dest="builddir", default = "BUILD")
    parser.add_option("-a", "--basedir", action="store", type="string",
                      dest="basedir", default = ".")
                     
    options, args = parser.parse_args()
    
    filename = sys.argv[2]

    somatex(filename, options.builddir, options.basedir)

    if not options.standalone:
        wrapSomaTex(filename, options.builddir, options.basedir)
        #latexSomaTex(filename, options.builddir, options.basedir)

    makePDF(filename, options.builddir, options.basedir, not options.standalone)
    
if __name__ == "__main__":
    main()

