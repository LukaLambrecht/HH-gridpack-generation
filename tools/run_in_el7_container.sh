#!/bin/bash

# Run a command in and el7 container, without starting an interactive container shell
# Seems to actually work...

# Example use: ./run_in_el7_container.sh ./script_with_commands.sh

# export bind paths
export APPTAINER_BINDPATH=/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/cvmfs/grid.cern.ch/etc/grid-security/vomses:/etc/vomses,/eos,/etc/pki/ca-trust,/etc/tnsnames.ora,/run/user,/tmp,/var/run/user,/etc/sysconfig,/etc:/orig/etc

# get the condor schedd from the current environment
schedd=`myschedd show -j | jq .currentschedd | tr -d '"'`
#schedd=bigbird27.cern.ch

# define the container image
image=/cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cat/cmssw-lxplus/cmssw-el7-lxplus:latest/

# define the command to run
cmd="source /app/setupCondor.sh && export _condor_SCHEDD_HOST=$schedd && export _condor_SCHEDD_NAME=$schedd && export _condor_CREDD_HOST=$schedd && $1"

# run apptainer
apptainer -s exec "$image" sh -c "$cmd"
