#!/bin/bash

# Start an EL7 container for being compatible with both CMSSW_10_6_X and condor job submission on LXPLUS

# References:
# - https://cms-talk.web.cern.ch/t/emulating-lxplus7-login-on-lxplus9/41544/1
# - https://gitlab.cern.ch/cms-cat/cmssw-lxplus/-/blob/master/README.md

# set bind path
export APPTAINER_BINDPATH=/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/cvmfs/grid.cern.ch/etc/grid-security/vomses:/etc/vomses,/eos,/etc/pki/ca-trust,/etc/tnsnames.ora,/run/user,/tmp,/var/run/user,/etc/sysconfig,/etc:/orig/etc

# get condor schedd from current environment
schedd=`myschedd show -j | jq .currentschedd | tr -d '"'`

# define image
image=/cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cat/cmssw-lxplus/cmssw-el7-lxplus:latest/

# make the command to run
cmd="source /app/setupCondor.sh && export _condor_SCHEDD_HOST=$schedd && export _condor_SCHEDD_NAME=$schedd && export _condor_CREDD_HOST=$schedd && /bin/bash"

# run apptainer
apptainer -s exec "$image" sh -c "$cmd"
