#!/bin/bash

# Add a crab_command.sh script to the private_production repository


# read the private_production repo as a command line arg
# (normally this would be ../CMSSW_10_6_8/src/private_production/
#  but leave as a configurable argument for now)
repo="$1"
echo "Location of private_production repo: $repo"

# set the location of template and new file
crab_status="$repo/HIG-Run3Summer22EE/Template/crab_status.sh"
crab_command="$repo/HIG-Run3Summer22EE/Template/crab_command.sh"

# copy crab_status.sh to crab_command.sh
cp "$crab_status" "$crab_command"

# modify the new file to remove the hard-coded 'status'
sed -i -e 's/crab status /crab /g' "$crab_command"

# printout result
echo "Created new script $crab_command"
