#!/bin/bash

# Run a command in and el7 container, without starting an interactive container shell
# Seems to actually work...

# Example use: ./run_in_el7_container.sh ./script_with_commands.sh

export APPTAINER_BINDPATH=/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/cvmfs/grid.cern.ch/etc/grid-security/vomses:/etc/vomses,/eos,/etc/pki/ca-trust,/etc/tnsnames.ora,/run/user,/tmp,/var/run/user,/etc/sysconfig,/etc:/orig/etc
schedd=`myschedd show -j | jq .currentschedd | tr -d '"'`

apptainer -s exec /cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cat/cmssw-lxplus/cmssw-el7-lxplus:latest/ "$1" -c "source /app/setupCondor.sh && export _condor_SCHEDD_HOST=$schedd && export _condor_SCHEDD_NAME=$schedd && export _condor_CREDD_HOST=$schedd && /bin/bash"
