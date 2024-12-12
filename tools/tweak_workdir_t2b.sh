#!/bin/bash

# Tweak the working directory settings in run_pwg_condor.py for running on T2B

# read powheg directory as cmdline arg
PWGDIR="$1"
echo "Powheg directory: $PWGDIR"

# go into the working directory
cd "$PWGDIR"

# tweak the prepareJob template
echo "Tweaking prepareJob template..."
sed -i '34s/cd -/cd $tmpdir/' Templates/prepareJob_template.sh

# tweak the run_pwg_condor.py file
echo "Tweaking run_pwg_condor.py..."
sed -i '110s/"rootfolder" : rootfolder,.*/"rootfolder" : rootfolder, "tmpdir": "\/tmp",/' run_pwg_condor.py
