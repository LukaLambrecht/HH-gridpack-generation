# HH sample generation with different H masses

### Preamble
See instructions here:
- [gridpack generation](https://gitlab.cern.ch/hh/hhgridpacks) (by Fabio Monti)
- [sample production](https://github.com/ekoenig4/private_production) (by Evan Koenig)

See also Thomas' lab notes for additional instructions!

So far, the procedures below have been tested on T2B, not yet on LXPLUS!
Small modifications are potentially needed in the latter case.
To do: run on lxplus and update the instructions as needed.

### Installation of this repository
Git clone this repository:

```
git clone https://github.com/LukaLambrecht/HH-sample-production.git
```

### Setting up the gridpack generation software
Set up a suitable CMSSW release and git clone the `genproductions` repository (fork by Fabio Monti) into it. All of this preferably inside the `HH-sample-production` folder to keep things orderly, but not necessarily.

```
cd HH-sample-production
cmsrel CMSSW_10_6_8
cd CMSSW_10_6_8/src/
cmsenv
git clone https://github.com/fabio-mon/genproductions
```

Switch to the correct branch.

```
cd genproductions
git checkout -b POWHEGggHH_cmssw106x origin/POWHEGggHH_cmssw106x
```

The `genproductions` repo is quite big, which can lead to network-related errors during cloning.
In order to avoid those (or just to save space), you can replace the standard `git clone` above by:

```
git clone https://github.com/fabio-mon/genproductions --depth 1 --branch POWHEGggHH_cmssw106x
```

This will download only the required branch and ignore the git history.
When you use this kind of clone, there is also no need anymore to checkout the specific branch, since it is already set during cloning.

All of these steps can be done slightly more conveniently in one go by running `./install-genproductions.sh` from inside the `HH-sample-production` main directory.

**Specific for lxplus:** the installation as detailed above does not work on lxplus,
since `CMSSW_10_6_X` is not compatible with the default lxplus architecture.
Therefore, just before installing `CMSSW`, do `cmssw-cc7` to switch to a suitable container.
Then follow exactly the same steps as above.

**Specific for T2B:** some tweaking of the working directory settings seems to be needed,
probably because of different settings HTCondor between lxplus and T2B.
Run the following:

```
cd tools
./tweak_workdir_t2b.sh ../CMSSW_10_6_8/src/genproductions/bin/Powheg
```

This basically replaces `cd -` in the job template script by `cd /tmp`, where `/tmp` is a temporary working directory on the T2B nodes (also works on the interface machines).

### Compile an input file
The instructions use `powheg_ggHH_kl_2p45_kt_1p00_c2_0p00.input`, but for our purposes, the SM point (`powheg_ggHH_kl_1p00_kt_1p00_c2_0p00.input`) is probably more useful. This step might take O(10-20) minutes.

```
cd bin/Powheg/
python ./run_pwg_condor.py -p 0 -i production/Run3/13p6TeV/Higgs/gg_HH_HEFT/powheg_ggHH_kl_1p00_kt_1p00_c2_0p00.input -m ggHH -f workdir_powheg_ggHH_kl_1p00_kt_1p00_c2_0p00 --svn 4038
```

Note: the instructions do not cover a change in the H mass.
This can probably be done by modifying the `.input` file above (it has an `hmass` parameter).
Not sure if that is the only required change though.
Current attempt using this change (see also notes on parallelization below); to be verified.

Note: the `.input` file above does not yet specify the decay of the H bosons.
It has a H decay mode parameter `hdecaymode` set to `-1`, i.e. close all decay channels).
So the H boson is considered stable as far as this step goes.
The decay to bb is probably specified in the Pythia configuration later on.

Notes on parallelization of this step:
- For creating gridpacks at many mass values, some parallelization is probably needed.
- The powheg compilation step seems to modify not only its specified working directory, but also some other files/variables. However, so far it seems that multiple compilations (e.g. multiple mass values) can run simultaneously within the same project, at least when run in job mode (see below). Not sure if this also works in interactive mode. To be verified.

The compilation can be configured (e.g. modify the mass in the input file) and wrapped in a condor job.
See the `compilation` directory.
Run `python compilation.py -h` to see a list of command line options.

### Preprocess the grid files
Following the instructions without modifications.

```
cd workdir_ggHH_kl_1p00_kt_1p00_c2_0p00
sed -i -e 's/import lhapdf/#import lhapdf/g' -e 's/pdf=lhapdf.mkPDF(lhaid)/#pdf=lhapdf.mkPDF(lhaid)/g' -e 's/alphas = pdf.alphasQ2(muRs)/alphas = 0.0 #alphas = pdf.alphasQ2(muRs)/g'  creategrid.py
chhh=$(awk 'sub(/^chhh/,""){printf "%+.4E", $1}' powheg.input)
ct=$(awk 'sub(/^ct /,""){printf "%+.4E", $1}' powheg.input)
ctt=$(awk 'sub(/^ctt/,""){printf "%+.4E", $1}' powheg.input)
cg=$(awk 'sub(/^cggh /,""){printf "%+.4E", $1}' powheg.input)
cgg=$(awk 'sub(/^cgghh/,""){printf "%+.4E", $1}' powheg.input)
gridtemp="Virt_full_${chhh}_${ct}_${ctt}_${cg}_${cgg}.grid"
pythoncmd="import creategrid as cg; cg.combinegrids('${gridtemp}', ${chhh}, ${ct}, ${ctt}, ${cg}, ${cgg})"
python3 -c "$pythoncmd"
```

This creates a `.grid` file named `Virt_full_+1.0000E+00_+1.0000E+00_+0.0000E+00_+0.0000E+00_+0.0000E+00.grid` in the chosen working directory `workdir_powheg_ggHH_kl_1p00_kt_1p00_c2_0p00`.

These grid preprocessing steps can be run in one go using the script `preprocess_grid_files.sh` in the `tools` subdirectory. It takes one cmd-line arg, namely the working directory. So in this case:

```
cd tools
./preprocess_grid_files.sh ../CMSSW_10_6_8/src/genproductions/bin/Powheg/workdir_ggHH_kl_1p00_kt_1p00_c2_0p00
```

### Run the calculation and make the gridpack
Follow the instructions without modifications, but try to automate a little bit more.
See `gridpack_generation` subdirectory.
Still very experimental, README to be updated when it works better.

### Check the gridpack
Follow the instructions with small modifications:
- wrap in an HTCondor job.
- change working directory from `/tmp/` (on lxplus) to `$TMPDIR` (on T2B).
See `gridpack_generation` subdirectory.

### Setting up the sample production software
Clone the repository.

```
cd CMSSW_10_6_8/src/
cmsenv
git clone https://github.com/ekoenig4/private_production.git
cd private_production
cd HIG-Run3Summer22EE
```

Note: the Pythia fragment is located under `Template/Configuration/GenProduction/python/HIG-Run3Summer22EEwmLHEGS-00282-fragment_powheg.py`. The decay of the H boson to b quarks is specified by the `25:onMode = off` and `25:onIfMatch = 5 -5` parameters.

Note: the Pythia fragment also has a parameter `POWHEG:nFinal = 3`.
Still to ask if it means what it seems to mean, but should probably be changed to 2.
See e.g. [here](https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/TSG-Run3Summer22EEwmLHEGS-00013/0)) for an example fragment of a central HH sample.

Note: the Pythia fragment also has an H mass parameter.
Not sure what happen if the value in the gridpack and in the Pythia fragment do not agree, but probably best to synchronize them.
Yet to find out how to do this automatically and systematically.
For the gridpack one can just create different input files and run them in parallel (?).
Not sure how to best synchronize the the Pythia fragment though.
