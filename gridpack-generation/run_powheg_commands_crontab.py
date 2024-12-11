# Run the Powheg commands for the several stages and iterations of the calculation

# Note: the individual commands already use job submission,
# so cannot simply run commands in a job,
# need to run them in the terminal and check for finishing of jobs
# before running the next command.

# Note: this is an alternative approach to run_powheg_commands_nohup.py.
# The former one uses a python script that runs continuously in the background.
# The problem is that it might get killed after some time on a shared environment (like lxplus or T2B).
# This new approach uses a crontab instead to regularly check for job completion
# and submitting the next step of the calculation.


import os
import sys
import time
import datetime
import argparse
from run_powheg_commands_nohup import find_latest_jobid
from run_powheg_commands_nohup import find_running_jobs


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to file with Powheg commands')
    parser.add_argument('-l', '--logfile', default='log_run_powheg_commands_crontab.txt',
      help='Path to log file for writing output to')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('- {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.inputfile):
        msg = 'Provided inputfile {} does not exist.'.format(args.inputfile)
        raise Exception(msg)

    # find the number of commands to run
    with open(args.inputfile, 'r') as f:
        cmds = f.readlines()
    ncmds = len(cmds)

    # define a base tag for interaction with the log file
    tag = '###RUNNING###: STEP: {}' + '/{},'.format(ncmds) + ' JOBID: {}'
    tagstart = tag[:14]

    # check if log file already exists
    logfile_exists = os.path.exists(args.logfile)

    # case: log file does not exist yet
    # (i.e. manually initiated first call)
    if not logfile_exists:
        
        # create the log file and write initial tag
        print('Creating a new log file...')
        with open(args.logfile, 'w') as f:
            inittag = tag.format(0, 0)
            f.write(inittag)
        print('Created log file {}'.format(args.logfile))

        # print some information
        cmd = 'python run_powheg_commands_crontab.py -i {} -l {}'.format(args.inputfile, args.logfile)
        cmd += ' >> {} 2>&1'.format(args.logfile)
        thisdir = os.path.dirname(os.path.abspath(__file__))
        fullcmd = 'cd {}; {}'.format(thisdir, cmd)
        info = '\n'
        info += 'Run the following command at regular intervals'
        info += ' to check the status and submit the next step if appropriate:\n'
        info += cmd
        info += '\n\n'
        info += 'Alternatively, add the following to your crontab file:\n'
        info += '0-59/10 * * * * {}'.format(fullcmd)
        print(info)

    # case: the log file already exists
    # (i.e. crontab initiated calls)
    if logfile_exists:
        
        # read the log file to find out which step is running
        print('----- {} -----'.format(datetime.datetime.now()))
        print('Checking currently running step in log file.')
        with open(args.logfile, 'r') as f:
            lines = [l for l in f.readlines() if l.startswith(tagstart)]
        if len(lines)==0:
            step = 0
            jobid = 0
        else:
            line = lines[-1]
            lineparts = line.split(' ')
            step = int(lineparts[2].split('/')[0])
            jobid = int(lineparts[4])
        print('Found step {} with jobid {}'.format(step, jobid))

        # check if jobs are still running/pending
        if jobid==0: njobs = 0
        else: njobs = find_running_jobs(jobid)
        msg = 'Found {} running/pending jobs for jobid {}'.format(njobs, jobid)
        if njobs!=0:
            msg += ' -> do nothing, exiting.'
            print(msg)
            sys.exit()
        else:
            if step == ncmds:
                msg += ' -> all steps have been completed, exiting.'
                print(msg)
                sys.exit()
            else:
                msg += ' -> submit next step!'
                print(msg)

        # select the next command to run
        cmd = cmds[step] # note: not step+1!
        
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
        time.sleep(1)
        # find the job id of the jobs just submitted
        jobid = find_latest_jobid()
        if jobid is None: raise Exception('Something went wrong: no jobs found.')
        # add tag to the log file
        print(tag.format(step+1, jobid))
