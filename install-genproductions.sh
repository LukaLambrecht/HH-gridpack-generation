#!/bin/bash

cmsrel CMSSW_10_6_8
cd CMSSW_10_6_8/src/
cmsenv
git clone https://github.com/fabio-mon/genproductions --depth 1 --branch POWHEGggHH_cmssw106x
cd genproductions
