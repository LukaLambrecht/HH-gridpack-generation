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

Note: this can be done in one go by running `bash install-genproductions.sh` from inside the `HH-sample-production` main directory.

### Compile an input file
Note: the instructions use `powheg_ggHH_kl_2p45_kt_1p00_c2_0p00.input`, but for our purposes, the SM point (`powheg_ggHH_kl_1p00_kt_1p00_c2_0p00.input`) is probably more useful. This step might take O(10-20) minutes.

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
- The powheg compilation step seems to modify not only its specified working directory, but also some other files/variables. Therefore, the attempt performed so far consists of making a fresh install of `CMSSW_10_6_8` and within it `genproductions` for each gridpack. So far this seems to work, even if the compilation in the different projects are run simultaneously (in different terminal windows on T2B).
- This duplication is only temporary; once the gridpacks are ready a few steps down, they can be moved to a single place and the duplicate project folders can be removed.
- Not yet explicitly tried to run multiple compilations in the same project. Maybe it works miraculously. To be tried later.

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

An extra change appears to be needed, on top of what both the instructions and Thomas' notes say.
This is perhap due to the HTCondor settings on T2B compared to lxplus?
Maybe try later on lxplus without this change.
Go to the `bin/Powheg` directory.
In the file `Templates/prepareJob_template.sh`, change line 34 from `cd -` to `cd $tmpdir`.
In the file `run_pwg_condor.py`, add `"tmpdir": "$TMPDIR",` after line 110.
The problem was that `cd -` redirected to my home folder, making the jobs interfere with one another and crash.
On T2B, `$TMPDIR` refers to the working directory on worker nodes reserved for jobs.

Note: all grid preprocessing steps listed in this section can be run in one go using the script `preprocess_grid_files.sh` in the `gridpack_generation` subdirectory. It takes one cmd-line arg, namely the working directory. So in this case:

```
cd gridpack_generation
bash preprocess_grid_files.sh ../CMSSW_10_6_8/src/genproductions/bin/Powheg/workdir_ggHH_kl_1p00_kt_1p00_c2_0p00
```

### Run the calculation and make the gridpack
Follow the instructions without modifications, but try to automate a little bit more. See `gridpack_generation` subdirectory.

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
