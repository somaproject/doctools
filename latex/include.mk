
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

wrapper: $(SVGFILES)
	cat $(LATEXPATH)/wrapper.header.tex > wrapped.tex
	cat $(TARGET) >> wrapped.tex
	cat $(LATEXPATH)/wrapper.footer.tex >> wrapped.tex
	$(SOMALATEX)  wrapped.tex > wrapped.output.tex
	$(LATEX) wrapped.output.tex
	mv wrapped.output.pdf $(TARGET).pdf

%.pdf : %.svg
	$(SVG2PDF) $< 

%.somatex : %.tex
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

clean:	$(SUBPROJECTS)
	rm -Rf $(patsubst %.tex,%.pdf,$(TEXFILES))
	rm -Rf *.log *.aux *.dvi *.out
	rm -Rf $(patsubst %.svg,%.pdf,$(SVGFILES)) 
	rm -f wildcard.tex 

include .depends

dep:
	$(LATEXPATH)/makedeps.py
