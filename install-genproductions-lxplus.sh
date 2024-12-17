#!/bin/bash

# Install the genproductions repository inside a suitable CMSSW release
# Specific version for lxplus

# Note: the general version can be used on lxplus as well,
# by running it inside a cmssw-cc7 container.
# This script simply automates entering and exithing the container,
# and produces the most efficient (i.e. sparse) checkout.

# Note: the cmssw-cc7 container is only used for installing CMSSW,
# not for checking out the genproductions git repository,
# because the git version inside the container is too old for sparse-checkout.

# get current working directory for later use
cwd=$(pwd)

# install CMSSW in container
echo "Installing CMSSW_10_6_8..."
cmssw-cc7 --command-to-run 'cmsrel CMSSW_10_6_8 && cd CMSSW_10_6_8/src/ && cmsenv'
cd "$cwd"
cd CMSSW_10_6_8/src

# clone the genproductions repository with a sparse checkout
echo "Cloning the genproductions repository..."
git clone https://github.com/fabio-mon/genproductions --depth 1 --branch POWHEGggHH_cmssw106x --no-checkout
cd genproductions
git sparse-checkout set .github bin/Powheg
git checkout

# return to original working directory
cd "$cwd"
