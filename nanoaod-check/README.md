# Check the produced NanoAOD files

In particular, check the following (all at gen-level for now):
- There are 2 H bosons per event.
- Each H boson decays to two b-jets (or maybe one bb fatjet?)
- The invariant mass of the H boson decay products corresponds to the intended value as set in the Powheg and Pythia input files.

Note: this check requires the `coffea` package, which is not installed by default.
However, it can be simply installed with `pip3 install coffea`.
It might be needed to first do `cmsenv` in a recent CMSSW version.
I used `CMSSW_13_3_1` for installing `coffea` and running this script.
