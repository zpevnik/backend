PDFSRC = $(wildcard *.tex)
PDFSOURCE = $(patsubst %.tex,%.pdf,$(PDFSRC))

%.pdf: %.tex
	xelatex $<

all: $(PDFSOURCE)

clean:
	rm -rf *.aux *.log

purge: clean
	rm -rf  *.pdf