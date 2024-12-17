import os
import sys


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

def find_job_status(jobid):
    # find job status for a specific job id
    # (similar to find_running_jobs but more detailed output)
    # output:
    # - None if something seem wrong with the condor_q output
    # - 0 if the given jobid is not found (i.e. jobs are finished or were never submitted)
    # - dict matching job status to number of jobs with that status

    # get the output of condor_q command
    # and return None if it looks like something is wrong
    lines = get_condor_q(do_check=True)
    if lines is None: return None

    # find line corresponding to given job id
    lines = [line for line in lines if line.split(' ')[2]==str(jobid)]
    
    # if no line can be found, return 0
    if len(lines) == 0: return 0

    # if multiple lines are found, something is wrong, return None
    if len(lines) > 1:
        msg = 'WARNING: ambiguity in job id,'
        msg += ' found multiple lines {} for jobid {}'.format(lines, jobid)
        print(msg)
        return None

    # split the line in parts and put the appropriate elements in a dict
    lineparts = [part for part in lines[0].split(' ') if part!='']
    ndone = lineparts[5]
    nrunning = lineparts[6]
    nidle = lineparts[7]
    ntotal = lineparts[8]
    res = {
      'done': ndone,
      'running': nrunning,
      'idle': nidle,
      'total': ntotal
    }

    return res
