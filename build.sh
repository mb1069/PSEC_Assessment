rm -rf submission/
rm -rf submission.zip
mkdir -p submission/
mkdir -p submission/data/
mkdir -p submission/results/

cp main.py submission/main.py
cp bruteforce.py submission/bruteforce.py
cp data/500-worst-passwords-processed.txt submission/data/500-worst-passwords-processed.txt
cp data/rockyou-withcount-processed.txt submission/data/rockyou-withcount-processed.txt
cp data/raw_data.csv submission/data/raw_data.csv



cd report/
pdflatex report.tex -output-directory=report/
bibtex references.bib
pdflatex report.tex -output-directory=report/
pdflatex report.tex -output-directory=report/
cp report.pdf ../submission/
cd ../
pwd
zip -r submission.zip submission