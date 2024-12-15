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
    parser.add_argument('-n', '--name', default='run_powheg_commands',
      help='Name tag for auto-generated script and log file')
    parser.add_argument('--el7', default=False, action='store_true',
      help='Run in el7 container')
    args = parser.parse_args()
    print('----- {} -----'.format(datetime.datetime.now()))
    print('Running run_powheg_commands_crontab.py with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.inputfile):
        msg = 'Provided inputfile {} does not exist.'.format(args.inputfile)
        raise Exception(msg)

    # find the number of commands to run
    with open(args.inputfile, 'r') as f:
        powheg_cmds = f.readlines()
    n_powheg_cmds = len(powheg_cmds)

    # define a base tag for interaction with the log file
    tag = '###RUNNING###: STEP: {}' + '/{},'.format(n_powheg_cmds) + ' JOBID: {}'
    tagstart = tag[:14]

    # parse the log file name and check if log file already exists
    # note: there is a short log file for internal bookkeeping,
    #       and a full log file to just dump all the output
    #       (for potential debugging)
    logfile = os.path.abspath('log_{}.txt'.format(args.name))
    fulllogfile = os.path.abspath('log_{}_full.txt'.format(args.name))
    exe = os.path.abspath('exe_{}.sh'.format(args.name))
    logfile_exists = os.path.exists(logfile)

    # some safety checks
    if not logfile_exists:
        existingfile = None
        if os.path.exists(fulllogfile): existingfile = fulllogfile
        if os.path.exists(exe): existingfile = exe
        if existingfile is not None:
            msg = 'ERROR: a file with name {} already exists'.format(fulllogfile)
            msg += ' and will interfere with the current run.'
            msg += ' Either remove/rename the file'
            msg += ' or choose a different name (-n) for the current run.'
            raise Exception(msg)
    if logfile_exists:
        missingfile = None
        if not os.path.exists(exe): missingfile = exe
        if missingfile is not None:
            msg = 'ERROR: file {} not found.'.format(missingfile)
            raise Exception(msg)

    # case: log file does not exist yet
    # (i.e. manually initiated first call)
    if not logfile_exists:
        
        # create the log file and write initial tag
        print('Log file does not yet exist; creating a new one...')
        with open(logfile, 'w') as f:
            inittag = tag.format(0, 0)
            f.write(inittag+'\n')
        print('Created log file {}'.format(logfile))

        # retrieve the tool directory (for use later)
        thisdir = os.path.abspath(os.path.dirname(__file__))
        toolsdir = os.path.abspath(os.path.join(thisdir, '../tools'))

        # make executable script for next steps
        cmd = 'python3 run_powheg_commands_crontab.py'
        cmd += ' -i {} -n {}'.format(args.inputfile, args.name)
        with open(exe, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
            f.write('cd {}\n'.format(thisdir))
            f.write(cmd+'\n')
        os.system('chmod +x {}'.format(exe))
        cmd = 'bash {}'.format(exe)

        # make el7 wrapping if requested
        if args.el7:
            run_in_container_script = os.path.join(toolsdir, 'run_in_el7_container.sh')
            cmd = 'bash {} {}'.format(run_in_container_script, exe)

        # print some information
        fullcmd  = cmd + ' >> {} 2>&1'.format(fulllogfile)
        info = '\n'
        info += 'Run the following command at regular intervals'
        info += ' to check the status and submit the next step if appropriate:\n'
        info += fullcmd
        info += '\n\n'
        info += 'Alternatively, add the following to your crontab file:\n'
        info += '0-59/30 * * * * {}\n'.format(fullcmd)
        info += 'or in the case of lxplus acrontab:\n'
        info += '0-59/30 * * * * lxplus.cern.ch {}\n'.format(fullcmd)
        print(info)

    # case: the log file already exists
    # (i.e. crontab initiated calls)
    if logfile_exists:

        # initialize message to write to log file
        logmsg = '---- {} ----\n'.format(datetime.datetime.now())
        
        # read the log file to find out which step is running
        print('Checking currently running step in log file.')
        with open(logfile, 'r') as f:
            lines = [l for l in f.readlines() if l.startswith(tagstart)]
        if len(lines)==0:
            step = 0
            jobid = 0
        else:
            line = lines[-1]
            lineparts = line.split(' ')
            step = int(lineparts[2].split('/')[0])
            jobid = int(lineparts[4])
        msg = 'Found step {} with jobid {}'.format(step, jobid)
        print(msg)
        logmsg += msg+'\n'

        # check if jobs are still running/pending
        if jobid==0: njobs = 0
        else: njobs = find_running_jobs(jobid)
        msg = 'Found {} running/pending jobs for jobid {}'.format(njobs, jobid)
        doexit = False
        if njobs!=0:
            msg += ' -> do nothing, exiting.'
            print(msg)
            logmsg += msg+'\n'
            doexit = True
        else:
            if step == n_powheg_cmds:
                msg += ' -> all steps have been completed, exiting.'
                print(msg)
                logmsg += msg+'\n'
                doexit = True
            else:
                msg += ' -> submit next step!'
                print(msg)
                logmsg += msg+'\n'
        if doexit:
            with open(logfile, 'a') as f: f.write(logmsg)
            sys.exit()

        # select the next command to run
        cmd = powheg_cmds[step] # note: not step+1!

        # retrieve latest job id
        # (to check new job id against after submission)
        oldjobid = find_latest_jobid()

        # run command
        print('Now running the following command:')
        print(cmd)
        os.system(cmd)
        sys.stdout.flush()
        sys.stderr.flush()
        
        # wait for the condor queue to update correctly
        time.sleep(1)
        
        # find and check the job id of the jobs just submitted
        jobid = find_latest_jobid()
        if jobid is None: raise Exception('ERROR: no jobs found.')
        if oldjobid is not None and jobid==oldjobid:
            msg = 'ERROR: job id equals an already existing job id.'
            raise Exception(msg)
        
        # write info to log file
        logmsg += tag.format(step+1, jobid)+'\n'
        with open(logfile, 'a') as f: f.write(logmsg)
