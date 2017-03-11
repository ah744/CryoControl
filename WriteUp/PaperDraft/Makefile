RM     := /bin/rm -rf

all: 
	pdflatex main ; bibtex main; pdflatex main; pdflatex main; dvips  -G0 -o paper.ps -e 0 main; 

nobib: 
	pdflatex main ; pdflatex main; pdflatex main; dvips  -G0 -o paper.ps -e 0 main; pst2pdf14 paper.ps

clean: 
	$(RM) *.dvi paper.ps *.log *.aux *.pdf *.blg *.bbl *~* main.out

