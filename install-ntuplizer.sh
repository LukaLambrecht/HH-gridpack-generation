#!/bin/bash

# Install the ntuplizer repositories inside a suitable CMSSW release


# Install CMSSW_13_3_1 if not yet previously installed
if [ ! -d CMSSW_13_3_1 ]; then
    echo "Installing CMSSW_13_3_1..."
    cmsrel CMSSW_13_3_1
fi

# Move into CMSSW_13_3_1 and cmsenv
cd CMSSW_13_3_1/src/
cmsenv

# Git clone the NanoAOD-tools repository (fork by Huilin)
# See here: https://github.com/hqucms/nanoAOD-tools
echo "Cloning the NanoAOD-tools repository..."
git clone https://github.com/hqucms/nanoAOD-tools.git PhysicsTools/NanoAODTools -b cmssw-py3 --depth 1

# Git clone the NanoHH4b repository
# See here: https://gitlab.cern.ch/gouskos/hh4b_run3
echo "Cloning the NanoHH4b repository..."
git clone https://gitlab.cern.ch/gouskos/hh4b_run3.git PhysicsTools/NanoHH4b -b run2 --depth 1

# Compile
scram b -j8

# Compile some additional stuff
cd PhysicsTools/NanoHH4b/python/helpers
bash compile.csh
