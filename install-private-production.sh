#!/bin/bash

# Install the genproductions repository inside a suitable CMSSW release


# Install CMSSW_10_6_8 if not yet previously installed
if [ ! -d CMSSW_10_6_8 ]; then
    echo "Installing CMSSW_10_6_8..."
    cmsrel CMSSW_10_6_8
fi

# Move into CMSSW_10_6_8 and cmsenv
cd CMSSW_10_6_8/src/
cmsenv

# Git clone the private production repository
echo "Cloning the private_production repository..."
git clone https://github.com/ekoenig4/private_production.git
