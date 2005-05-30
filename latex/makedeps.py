#!/usr/bin/python
"""

Our goal is to create a per-directory .depends file

This will be used for building the subdirs:

rootfile.tex

rootfile.pdf: dirname1 dirname2 dirname3 dirname4


dirname1:
     make -C dirname1


"""

import os
import re
import glob


def makedeps(rootdir):
    importRE = re.compile(r"^\\import{(.+)/}.+")
    depfid = file(".depends", 'w')
    for texfile in glob.glob("*.tex"):
        subdirincludes = []
        fid = file(texfile)
        for l in fid.readlines():
            r = importRE.match(l)
            if r:
                subdirincludes.append(r.group(1))
        
        if len(subdirincludes) > 0:
            depstr = ""
            for i in subdirincludes:
                depstr += i + ' '
                depfid.write("%s:\n\t$(MAKE) -C %s support\n" % (i, i))

                try:
                    os.chdir(i)
                    makedeps("./")
                    os.chdir("..")
                except:
                    pass
            depfid.write("%s: %s\n" % (texfile, depstr))
        
            
        
if __name__ == "__main__":
    makedeps("./")
