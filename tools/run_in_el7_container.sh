#!/bin/bash

# Run a command in and el7 container, without starting an interactive container shell

# Example use: ./run_in_el7_container.sh ./script_with_commands.sh

# References:
# - https://cms-talk.web.cern.ch/t/emulating-lxplus7-login-on-lxplus9/41544/1
# - https://gitlab.cern.ch/cms-cat/cmssw-lxplus/-/blob/master/README.md
# A notable addition is the exporting of the KRB5CCNAME environment variable, setting the location of the kerberos credentials.
# This is needed when using this script in a cron job, since every cron job is assigned temporary kerberos credentials,
# while the default personal credentials are not accessibe from inside the cron job.

# export bind paths
export APPTAINER_BINDPATH=/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/cvmfs/grid.cern.ch/etc/grid-security/vomses:/etc/vomses,/eos,/etc/pki/ca-trust,/etc/tnsnames.ora,/run/user,/tmp,/var/run/user,/etc/sysconfig,/etc:/orig/etc

# get the condor schedd from the current environment
schedd=`myschedd show -j | jq .currentschedd | tr -d '"'`
setschedd="source /app/setupCondor.sh && export _condor_SCHEDD_HOST=$schedd && export _condor_SCHEDD_NAME=$schedd && export _condor_CREDD_HOST=$schedd"

# get the kerberos cache location from the current environment
kerberos="$KRB5CCNAME"
setkerberos="export KRB5CCNAME=$kerberos"

# define the container image
image=/cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cat/cmssw-lxplus/cmssw-el7-lxplus:latest/

# define the command to run
cmd="$setschedd && $setkerberos && $1"

# run apptainer
apptainer -s exec "$image" sh -c "$cmd"
