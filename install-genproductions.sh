#!/bin/bash

cmsrel CMSSW_10_6_8
cd CMSSW_10_6_8/src/
cmsenv
git clone https://github.com/fabio-mon/genproductions
cd genproductions
git checkout -b POWHEGggHH_cmssw106x origin/POWHEGggHH_cmssw106x
