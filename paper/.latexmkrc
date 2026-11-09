# main.tex（\documentclass[dvipdfmx,a4paper]{jsarticle}・biblatex/biber）を upLaTeX で組む設定。
# jsclasses は 2023-02-12 版から engine を自動判定するので、main.tex に uplatex オプションを足す必要はない。
$latex = 'uplatex -synctex=1 -halt-on-error -interaction=nonstopmode -file-line-error %O %S';
$bibtex_use = 2;
$biber = 'biber %O %S';
$dvipdf = 'dvipdfmx %O -o %D %S';
$pdf_mode = 3;
