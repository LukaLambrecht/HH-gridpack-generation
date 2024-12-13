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


def get_condor_q(do_check=False):
    # get the output by condor_q as a list of strings
    # note: works by writing condor_q output to a temporary file and reading it

    # get the output of condor_q
    tempfile = 'check_running_jobs.txt'
    os.system('condor_q > {}'.format(tempfile))
    with open(tempfile, 'r') as f: lines = f.readlines()
    lines = [line for line in lines if line!='\n']
    os.system('rm {}'.format(tempfile))

    # do a syntax check if requested
    if do_check:
        error = False
        if len(lines) < 5: error = True
        if not error:
            if not lines[0].startswith('-- Schedd:'): error = True
            if not lines[1].startswith('OWNER'): error = True
            if not lines[-3].startswith('Total for query:'): error = True
            if not lines[-2].startswith('Total for'): error = True
            if not lines[-1].startswith('Total for all users:'): error = True
        if error:
            msg = 'WARNING: condor_q returned suspicious output:\n'
            msg += '\n'.join(lines)
            print(msg)
            return None
    return lines

def jobs_are_running():
    # checks whether jobs are running
    # note: this function does not take into account specific job/batch IDs,
    #       it counts any job that is currently running.

    lines = get_condor_q()
    # find the line that lists the number of jobs
    tag = 'Total for query: '
    lines = [line for line in lines if line.startswith(tag)]
    if len(lines)!=1:
        msg = 'Cannot determine whether jobs are running.'
        raise Exception(msg)
    line = lines[0]
    # determine number of jobs
    njobs = line.replace(tag, '').split(';')[0].replace(' jobs','')
    njobs = int(njobs)
    if njobs>0: return True
    else: return False

def find_latest_jobid():
    # find latest job id
    # note: based on the text returned by condor_q,
    #       and assumes the latest job is the lowest line.
    
    lines = get_condor_q()
    # find the lowest line corresponding to a job/batch
    tag = 'Total for query: '
    match_idx = [idx for idx,line in enumerate(lines) if line.startswith(tag)]
    if len(match_idx)!=1:
        msg = 'Cannot determine whether jobs are running.'
        raise Exception(msg)
    match_idx = match_idx[0]
    latest_line = lines[match_idx-1]
    if latest_line.startswith('OWNER'): return None
    jobid = latest_line.split(' ')[2]
    return jobid

def find_running_jobs(jobid):
    # find running jobs for a specific job id

    # get the output of condor_q command
    # and return -1 if it looks like something is wrong
    lines = get_condor_q(do_check=True)
    if lines is None: return -1
 
    # find line corresponding to given job id
    lines = [line for line in lines if line.split(' ')[2]==str(jobid)]
    if len(lines) == 0: return 0
    if len(lines) > 1:
        msg = 'WARNING: ambiguity in job id, found multiple lines {} for jobid {}'.format(lines, jobid)
        print(msg)
        return -1

    # split the line in parts and find the part corresponding to total number of jobs
    lineparts = [part for part in lines[0].split(' ') if part!='']
    ntotal = int(lineparts[8])
    return ntotal


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
    for arg in vars(args): print('- {}: {}'.format(arg, getattr(args,arg)))

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
