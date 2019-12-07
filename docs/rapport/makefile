all : rapport

rapport :
	pdflatex -shell-escape rapport.tex && pdflatex -shell-escape rapport.tex && pdflatex rapport.tex  
	rm -f ./*.aux
	rm -f ./*.log
	rm -f ./*.out
	rm -f ./*.synctex.gz
	rm -f ./*.toc
	rm -f ./*.bbl
	rm -f ./*.blg
	rm -f ./*.dvi

clean :
	rm -f ./*.aux
	rm -f ./*.log
	rm -f ./*.out
	rm -f ./*.pdf
	rm -f ./*.synctex.gz
	rm -f ./*.toc
	rm -f ./*.bbl
	rm -f ./*.blg
	rm -f ./*.dvi
	rm -f ./*.bcf
	rm -f ./*.run.xml
	rm rapport.pdf