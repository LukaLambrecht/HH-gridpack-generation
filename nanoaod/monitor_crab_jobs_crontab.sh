#!/bin/bash

# run by adding something like this in the acrontab file:
# 0 */4 * * * lxplus.cern.ch cd <path to here>; bash monitor_crab_jobs_crontab.sh >> <some log file> 2>&1


# print date and time for bookkeeping
echo "\nRunning monitor_crab_jobs_crontab.sh"
date
echo "\n"

# copy proxy in current directory to /tmp
# (make sure proxy is valid for the entire expected duration of the crontab task)
cp x509up_u116295 /tmp

# this seems to be needed for scram and crab commands to be available
source /cvmfs/cms.cern.ch/cmsset_default.sh

# run the monitoring
python3 monitor_crab_jobs.py -i ../CMSSW_10_6_8/src/private_production/HIG-Run3Summer22EE/simpacks/ -r
