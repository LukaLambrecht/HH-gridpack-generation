#!/bin/bash

# Patch the Pythia fragment from the private_production repository


# read fragment to patch as cmdline arg
# (normally this would be ../CMSSW_10_6_8/src/private_production/
#  HIG-Run3Summer22EE/Template/Configuration/GenProduction/python/
#  HIG-Run3Summer22EEwmLHEGS-00282-fragment_powheg.py,
#  but leave as a configurable argument for now)
fragment="$1"
echo "Fragment: $fragment"

# read the mass as a command line arg (default: -1)
mass="${2:--1}"
mass_formatted=`printf "%.1f" $mass`

# set the number of final state particles
echo "Setting POWHEG:nFinal parameter to 2..."
sed -i -e "s/'POWHEG:nFinal = .*',/'POWHEG:nFinal = 2',/g" "$fragment"

# replace H mass parameter which is hard-coded in the file
if [ "$mass" -gt 0 ]; then
    echo "Setting H mass to $mass..."
    sed -i -e "s/'25:m0 = .*',/'25:m0 = $mass_formatted',/g" "$fragment"
fi
