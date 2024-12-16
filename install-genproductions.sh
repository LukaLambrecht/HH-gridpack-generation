#!/bin/bash

# Install the genproductions repository inside a suitable CMSSW release

echo "Installing CMSSW_10_6_8..."
cmsrel CMSSW_10_6_8
cd CMSSW_10_6_8/src/
cmsenv
echo "Cloning the genproductions repository..."
git clone https://github.com/fabio-mon/genproductions --depth 1 --branch POWHEGggHH_cmssw106x
