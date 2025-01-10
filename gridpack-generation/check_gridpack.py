# Check a created gridpack by trying to generate some events


import os
import sys
import argparse
sys.path.append(os.path.abspath('../jobtools'))
import condortools as ct


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gridpack', required=True, type=os.path.abspath,
      help='Path to the gridpack to check')
    parser.add_argument('-n', '--nevents', default=10, type=int,
      help='Path to the gridpack to check')
    parser.add_argument('-r', '--runmode', default='local', choices=['local', 'condor'],
      help='Run interactively or in condor job')
    parser.add_argument('--el7', default=False, action='store_true',
      help='Run in el7 container')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.gridpack):
        msg = 'Provided gridpack {} does not exist.'.format(args.gridpack)
        raise Exception(msg)

    # set path to this directory and tools directory
    # (for use later)
    thisdir = os.path.abspath(os.path.dirname(__file__))
    toolsdir = os.path.abspath(os.path.join(thisdir, '../tools'))

    # make executable script
    exe = 'exe_check_gridpack.sh'
    with open(exe, 'w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('mkdir -p /tmp/$USER/\n')
        f.write('cd /tmp/$USER/\n')
        f.write('cp {} ./gridpack.tgz\n'.format(args.gridpack))
        f.write('tar -xf ./gridpack.tgz\n')
        f.write('./runcmsgrid.sh {} 1 1\n'.format(args.nevents))
        f.write('cp cmsgrid_final.lhe {}'.format(thisdir))
    os.system('chmod +x {}'.format(exe))
    exe = os.path.abspath(exe)
    cmd = 'bash {}'.format(exe)

    # make el7 wrapping if requested
    if args.el7:
        thisdir = os.path.abspath(os.path.dirname(__file__))
        toolsdir = os.path.abspath(os.path.join(thisdir, '../tools'))
        run_in_container_script = os.path.join(toolsdir, 'run_in_el7_container.sh')
        cmd = 'bash {} {}'.format(run_in_container_script, exe)

    # run the command or submit as job
    if args.runmode=='local':
        os.system(cmd)
    elif args.runmode=='condor':
        ct.submitCommandAsCondorJob('cjob_check_gridpack', cmd, jobflavour='workday')
