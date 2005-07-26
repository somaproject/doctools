
TIMING2SVG = $(TOOLSPATH)/timing/timing.py
SVG2PDF = $(TOOLSPATH)/svg2boundedPDF.py
MEMMAP = $(LATEXPATH)/memmap.py
SOMALATEX = $(LATEXPATH)/somatex.py
LATEX = pdflatex

export TEXINPUTS := .:$(LATEXPATH)//:
SVGFILES := $(patsubst %.svg,%.pdf,$(wildcard *.svg))
TEXFILES := $(wildcard *.tex)

TEXINCLUDEFIND :=  

.DELETE_ON_ERROR:

all: $(SUBPROJECTS) support 

$(SUBPROJECTS): 
	$(MAKE) --directory=$@ $(TARGET)

%.pdf : %.svg
	$(SVG2PDF) $< 

%.somatex : %.tex support
	$(SOMALATEX) $< > $(subst .tex,.somatex,$<)

%.pdf : %.somatex
	cat $(LATEXPATH)/wrapper.header.tex > wrapped.tex
	cat $< >> wrapped.tex
	cat $(LATEXPATH)/wrapper.footer.tex >> wrapped.tex
	$(LATEX) wrapped.tex
	mv wrapped.pdf $(subst .somatex,.pdf,$<)
	rm wrapped.tex

graphics: $(SVGFILES)

support: graphics

distclean: clean 
	rm .depends
clean:	
	rm -Rf $(patsubst %.tex,%.pdf,$(TEXFILES))
	rm -Rf *.log *.aux *.dvi *.out *.somatex
	rm -Rf $(patsubst %.svg,%.pdf,$(SVGFILES)) 
	rm -Rf *.dspcmd.pdf *.event.pdf *.dspcmd.svg *.event.svg
	rm -f wildcard.tex 

dep:
	$(LATEXPATH)/makedeps.py


ifneq (,$(wildcard .depends))
include .depends
else
endif 


