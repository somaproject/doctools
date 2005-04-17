
TIMING2SVG = $(TOOLSPATH)/timing/timing.py
SVG2PDF = $(TOOLSPATH)/svg2boundedPDF.py
MEMMAP = $(LATEXPATH)/memmap.py
LATEX = pdflatex

export TEXINPUTS := .:$(LATEXPATH)//:
TIMINGFILES := $(patsubst %.timing,%.timing.pdf,$(wildcard *.timing))
MEMMAPFILES := $(patsubst %.memmap,%.memmap.tex,$(wildcard *.memmap))
SVGFILES := $(patsubst %.svg,%.pdf,$(wildcard *.svg))
TEXFILES := $(wildcard *.tex)

.DELETE_ON_ERROR:

all: $(SUBPROJECTS) support 


$(SUBPROJECTS): 
	$(MAKE) --directory=$@ $(TARGET)


wrapper: $(TIMINGFILES) $(MEMMAPFILES) $(SVGFILES)
	cat $(LATEXPATH)/wrapper.header.tex > wrapped.tex
	cat $(TARGET) >> wrapped.tex
	cat $(LATEXPATH)/wrapper.footer.tex >> wrapped.tex
	$(LATEX)  wrapped.tex $(TARGET).pdf

%.timing.pdf : %.timing
	$(TIMING2SVG) $<
	$(SVG2PDF) $<.svg	 


%.memmap.tex : %.memmap
	$(MEMMAP) $< > $@

%.pdf : %.svg
	$(SVG2PDF) $< 

%.pdf : %.tex
	$(LATEX) $< 


graphics: $(TIMINGFILES) $(MEMMAPFILES) $(SVGFILES)

support: graphics

clean:	$(SUBPROJECTS)
	rm -Rf *.timing.pdf *.timing.svg
	rm -Rf $(patsubst %.tex,%.pdf,$(TEXFILES))
	rm -Rf $(MEMMAPFILES)
	rm -Rf *.log *.aux *.dvi *.out
	rm -Rf $(patsubst %.svg,%.pdf,$(SVGFILES)) 
	rm -f wildcard.tex 
