#!/usr/bin/python


"""

Code to actually run all the commands to make the docbook stuff

"""

objdir = "objs"
batikpath = "java -Xmx128m -Djava.awt.headless=true -jar ~/soma/docs/tools/svg/batik-1.5.1/batik-rasterizer.jar -m %s -d %s  %s" % ('%s', objdir, '%s') 

import os
import re
import os.path

def getfiles(extension):
    files = os.listdir(os.getcwd())

    targetfiles = []

    retype = re.compile(".+\.%s$" % extension)

    for i in files:
        if retype.match(i):
            targetfiles.append(i)

    return targetfiles

def recompile(src, target):
    # determines if we need to recompile target src because target is older

    stime = os.path.getmtime(src)
    if os.path.isfile(target):
        ttime = os.path.getmtime(target)
    else:
        ttime = 0
        
    if stime > ttime:
        return True
    else:
        return False
    

def image2png():
    """
    Takes the images in the current directory, and
    runs convert to turn them into pngs in objdir/

    """
    if not os.path.isdir(objdir):
        os.mkdir(objdir)
    
    # get filenames

    # first, we convert the pngs to pngs:
    for png in  getfiles("png"):
        if recompile(png, objdir + "/" + png + ".png"):
            os.system("convert %s %s/%s" % (png, objdir, png+".png"))
        
    # then, we convert the eps figures
    for eps in  getfiles("eps"):
        if recompile(eps, objdir + "/" + eps + ".png"):
            os.system("convert %s %s/%s" % (eps, objdir, eps+".png"))


    # then the svg
    for svg in  getfiles("svg"):
        if recompile(svg, objdir + "/" + svg + ".png"):
            os.system(batikpath % ("image/png", svg))


def image2eps():
    """
    Takes the images in the current directory, and
    runs convert to turn them into EPSes in objdir/

    """
    if not os.path.isdir(objdir):
        os.mkdir(objdir)
    
    # get filenames

    # first, we convert the pngs to eps:
    for png in  getfiles("png"):
        if recompile(png, objdir + "/" + png + ".eps"):
            os.system("convert %s %s/%s" % (png, objdir, png+".eps"))
        
    # then, we convert the eps figures
    for eps in  getfiles("eps"):
        if recompile(eps, objdir + "/" + eps + ".eps"):
            os.system("convert %s %s/%s" % (eps, objdir, eps+".eps"))


    # then the svg
    for svg in  getfiles("svg"):
        if recompile(svg, objdir + "/" + svg + ".eps"):
            os.system(batikpath % ('application/pdf', svg))
            os.system("pdf2ps %s %s" % (objdir+'/' + svg + '.pdf', objdir + '/' + svg + '.ps'))
            os.system("ps2epsi %s %s" % (objdir+'/' + svg + '.ps', objdir + '/' + svg + '.eps'))
            
def image2pdf():
    """
    Takes the images in the current directory, and
    runs convert to turn them into pngs in objdir/

    """
    if not os.path.isdir(objdir):
        os.mkdir(objdir)
    
    # get filenames

    # first, we convert the pngs to eps:
    for png in  getfiles("png"):
        if recompile(png, objdir + "/" + png + ".pdf"):
            os.system("convert %s %s/%s" % (png, objdir, png+".pdf"))
        
    # then, we convert the eps figures
    for eps in  getfiles("eps"):
        if recompile(eps, objdir + "/" + eps + ".pdf"):
            os.system("convert %s %s/%s" % (eps, objdir, eps+".pdf"))


    # then the svg
    for svg in  getfiles("svg"):
        if recompile(svg, objdir + "/" + svg + ".pdf"):
            os.system(batikpath % ('application/pdf', svg))


    
    pass

import sys
if __name__ == "__main__":

    if sys.argv[1] == "html":
        image2png()
    elif sys.argv[1] == "latex":
        image2eps()
    elif sys.argv[1] == "pdflatex":
        image2pdf()
