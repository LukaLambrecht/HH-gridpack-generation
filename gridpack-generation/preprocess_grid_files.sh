#!/bin/bash

# Preprocess grid files after compilation but before running the calculation


# References:
# - https://gitlab.cern.ch/hh/hhgridpacks
# - own experience and notes, see README


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

# prepare the grid
echo "Preparing grid..."
chhh=$(awk 'sub(/^chhh/,""){printf "%+.4E", $1}' powheg.input)
ct=$(awk 'sub(/^ct /,""){printf "%+.4E", $1}' powheg.input)
ctt=$(awk 'sub(/^ctt/,""){printf "%+.4E", $1}' powheg.input)
cg=$(awk 'sub(/^cggh /,""){printf "%+.4E", $1}' powheg.input)
cgg=$(awk 'sub(/^cgghh/,""){printf "%+.4E", $1}' powheg.input)
gridtemp="Virt_full_${chhh}_${ct}_${ctt}_${cg}_${cgg}.grid"
pythoncmd="import creategrid as cg; cg.combinegrids('${gridtemp}', ${chhh}, ${ct}, ${ctt}, ${cg}, ${cgg})"
python3 -c "$pythoncmd"

# go one directory up (assume this is the genproductions/bin/Powheg directory!)
cd ..

# tweak the prepareJob template
echo "Tweaking prepareJob template..."
sed -i '34s/cd -/cd $tmpdir/' Templates/prepareJob_template.sh

# tweak the run_pwg_condor.py file
echo "Tweaking run_pwg_condor.py..."
sed -i '110s/"rootfolder" : rootfolder,.*/"rootfolder" : rootfolder, "tmpdir": "$TMPDIR",/' run_pwg_condor.py
