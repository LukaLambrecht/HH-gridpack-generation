# Run the Powheg commands for the several stages and iterations of the calculation

# Note: the individual commands already use job submission,
# so cannot simply run commands in a job,
# need to run them in the terminal and check for finishing of jobs
# before running the next command.

# Note: the strategy is to use a python script that runs continuously in the background.
# The problem is that it might get killed after some time on a shared environment (like lxplus or T2B).
# This strategy is DEPRECATED and this script is not developed further, but kept as it is for reference.
# See an alternative approach in run_powheg_commands_crontab.py!


import os
import sys
import time
import argparse
sys.path.append(os.path.abspath('../jobtools'))
from condorqtools import find_latest_jobid
from condorqtools import find_running_jobs


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to file with Powheg commands')
    parser.add_argument('-l', '--logfile', default='log_run_powheg_commands_nohup.txt',
      help='Path to log file for writing output to')
    parser.add_argument('-r', '--run', default=False, action='store_true',
      help='Do not use, only for internal usage')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.inputfile):
        msg = 'Provided inputfile {} does not exist.'.format(args.inputfile)
        raise Exception(msg)

    sys.stdout.flush()
    sys.stderr.flush()

    # make the command to run in the background
    if not args.run:
        cmd = 'python run_powheg_commands_nohup.py -i {} -r'.format(args.inputfile)
        cmd = 'nohup {} &> {} &'.format(cmd, args.logfile)
        os.system(cmd)
        print('Process running in the background using nohup.')
        print('Check {} for status.'.format(args.logfile))
        print('Terminate by using "ps" and then "kill <correct PID>".')
        sys.exit()

    # other settings
    wait_interval_mins = 10

    # read the file
    with open(args.inputfile, 'r') as f:
        cmds = f.readlines()

    # loop over commands
    for cmd in cmds:
        # run command
        # note: every os.system generates a new subshell,
        # so it is important that all necessary preparation
        # (such as cd to the right directory, cmsenv, etc.)
        # is included in the command
        # (e.g. 'prep 1; prep 2; actual powheg command')
        print('Now running the following command:')
        print(cmd)
        os.system(cmd)
        sys.stdout.flush()
        sys.stderr.flush()
        # wait for the condor queue to update correctly
        time.sleep(3)
        # find the job id of the jobs just submitted
        jobid = find_latest_jobid()
        if jobid is None:
            raise Exception('Something went wrong: no jobs found.')
        # check for running jobs with the correct job id
        while find_running_jobs(jobid)>0:
            msg = 'Checking for jobs with ID {}'.format(jobid)
            msg += ' -> jobs appear to be running,'
            msg += ' waiting for {} minutes'.format(wait_interval_mins)
            print(msg)
            sys.stdout.flush()
            sys.stderr.flush()
            time.sleep(60*wait_interval_mins)
        # wait an additional margin just to be sure
        time.sleep(10)
    print('All commands have been run, exiting.')
