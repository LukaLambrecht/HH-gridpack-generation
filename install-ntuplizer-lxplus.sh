#!/bin/bash

# Install the ntuplizer repositories inside a suitable CMSSW release
# Specific version for lxplus

# Note: just a wrapper that calls the general installer
# inside a cmssw-cc7 container.

cmssw-cc7 --command-to-run 'bash ./install-ntuplizer.sh'
