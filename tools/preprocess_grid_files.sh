#!/bin/bash

# Preprocess grid files after compilation but before running the calculation

# References:
# - https://gitlab.cern.ch/hh/hhgridpacks

# read powheg working directory as cmdline arg
WORKDIR="$1"
echo "Working directory: $WORKDIR"

# go into the working directory
cd "$WORKDIR"

# do cmsenv
# (this is needed for running creategrid.py, see below)
cmsenv

# tweak the creategrid.py file
echo "Tweaking creategrid.py file..."
sed -i -e 's/import lhapdf/#import lhapdf/g' -e 's/pdf=lhapdf.mkPDF(lhaid)/#pdf=lhapdf.mkPDF(lhaid)/g' -e 's/alphas = pdf.alphasQ2(muRs)/alphas = 0.0 #alphas = pdf.alphasQ2(muRs)/g' creategrid.py

# read coupling strengths from powheg input file
# note: if not found in input file, they are set to standard model values
echo "Reading coupling strengths from input file..."
chhh=$(awk 'sub(/^chhh/,""){printf "%+.4E", $1}' powheg.input)
if [ -z "${chhh}" ]; then
    echo "  - param chhh not found in input file, setting to 1."
    chhh="+1.0000E+00"
fi
ct=$(awk 'sub(/^ct /,""){printf "%+.4E", $1}' powheg.input)
if [ -z "${ct}" ]; then
    echo "  - param ct not found in input file, setting to 1."
    ct="+1.0000E+00"
fi
ctt=$(awk 'sub(/^ctt/,""){printf "%+.4E", $1}' powheg.input)
if [ -z "${ctt}" ]; then
    echo "  - param ctt not found in input file, setting to 0."
    ctt="+0.0000E+00"
fi
cg=$(awk 'sub(/^cggh /,""){printf "%+.4E", $1}' powheg.input)
if [ -z "${cg}" ]; then
    echo "  - param cg not found in input file, setting to 0."
    cg="+0.0000E+00"
fi
cgg=$(awk 'sub(/^cgghh/,""){printf "%+.4E", $1}' powheg.input)
if [ -z "${cgg}" ]; then
    echo "  - param cgg not found in input file, setting to 0."
    cgg="+0.0000E+00"
fi

# make the grid
echo "Preparing the grid..."
gridtemp="Virt_full_${chhh}_${ct}_${ctt}_${cg}_${cgg}.grid"
pythoncmd="import creategrid as cg; cg.combinegrids('${gridtemp}', ${chhh}, ${ct}, ${ctt}, ${cg}, ${cgg})"
python3 -c "$pythoncmd"
