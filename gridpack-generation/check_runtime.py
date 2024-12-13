# Check the runtime of condor jobs for gridpack generation

# Note: essentially just a wrapper around the following bash command:
# grep 'Run Remote Usage' <working directory>/run_<#step>_<#iteration>.log


import os
import sys
import fnmatch
import argparse
import subprocess


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--workdir', required=True, type=os.path.abspath,
      help='Path to working directory')
    parser.add_argument('-p', '--parstage', required=0, type=int,
      help='Stage of the calculation (default: all stages)')
    parser.add_argument('-x', '--xgrid', required=0, type=int,
      help='Iteration of the calculation (default: all iterations)')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('- {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.workdir):
        msg = 'Provided inputfile {} does not exist.'.format(args.workdir)
        raise Exception(msg)

    # find all log files matching the requested stage and iteration
    pchar = str(args.parstage) if args.parstage>0 else '*'
    ichar = str(args.xgrid) if args.xgrid>0 else '*'
    pattern = 'run_{}_{}.log'.format(pchar, ichar)
    logfiles = [os.path.join(args.workdir, f) for f in os.listdir(args.workdir) if fnmatch.fnmatch(f, pattern)]
    logfiles.sort()
    print('Found {} log files matching criteria'.format(len(logfiles)))

    # loop over log files
    for logfile in logfiles:
        
        # gather information on runtimes
        tag = os.path.splitext(os.path.basename(logfile))[0]
        parstage = int(tag.split('_')[1])
        iteration = int(tag.split('_')[2])
        grepcmd = "grep 'Run Remote Usage' {}".format(logfile)
        grepstdout = subprocess.check_output(grepcmd, shell=True)
        grepstdout = grepstdout.decode(sys.stdout.encoding)
        greplines = [l.strip(' \t\n') for l in grepstdout.split('\n') if len(l)>0]
        runtimes = sorted([el.split(' ')[2].strip(',') for el in greplines])

        # do printouts
        print('Results for file {}:'.format(logfile))
        print('Job runtimes ({}): {}'.format(len(runtimes), runtimes))
