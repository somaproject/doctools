#!/bin/bash


echo "" > .depends
for texfile in *.tex
do
  echo $texfile

  awk 'BEGIN {printf "$texfile: "}; /^\\import/ { split($0,a,/[{}/]/); printf("%s ", a[2])}; END {print ""}' $texfile >> .depends

  awk '/^\\import/ { split($0,a,/[{}/]/); printf("%s:\n\t$$(MAKE) -C %s \n", a[2], a[2])}' $texfile >> .depends

  #subdirs = `awk '/^\\import/ { split($0,a,/[{}/]/); printf("%s ", a[2])}'`
  
  
done; 
