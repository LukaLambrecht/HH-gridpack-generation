#!/bin/bash

# Install the genproductions repository inside a suitable CMSSW release


# get current working directory for later use
cwd=$(pwd)

# install CMSSW
echo "Installing CMSSW_10_6_8..."
cmsrel CMSSW_10_6_8
cd CMSSW_10_6_8/src/
cmsenv

# clone genproductions repository
echo "Cloning the genproductions repository..."
git clone https://github.com/fabio-mon/genproductions --depth 1 --branch POWHEGggHH_cmssw106x

# return to original working directory
cd "$cwd"
