# Make the Powheg commands for the several stages and iterations of the calculation

import os
import sys
import argparse

if __name__=='__main__':
    
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to the Powheg .input file for this process')
    parser.add_argument('-w', '--workdir', required=True, type=os.path.abspath,
      help='Path to the working directory for this process')
    parser.add_argument('-o', '--outputfile', default=None,
      help='Path to a file to write the Powheg commands (default: print to screen)')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('- {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.inputfile):
        msg = 'Provided input file {} does not exist.'.format(args.inputfile)
        raise Exception(msg)
    if not os.path.exists(args.workdir):
        msg = 'Provided working directory {} does not exist.'.format(args.workdir)
        raise Exception(msg)

    # find the powheg directory from where to run the commands
    # (assume the .input file is located inside that directory)
    tag = 'genproductions/bin/Powheg/'
    powhegdir = os.path.join(args.inputfile.split(tag)[0], tag)
    print('Found Powheg base directory {}'.format(powhegdir))

    # make input file and working directory relative to the powheg path
    # (seems to be needed for ./run_pwg_condor.py to run correctly)
    inputfile_rel = os.path.relpath(args.inputfile, powhegdir)
    workdir_rel = os.path.relpath(args.workdir, powhegdir)
    print('Found following relative paths:')
    print(' - input file: {}'.format(inputfile_rel))
    print(' - working directory: {}'.format(workdir_rel))

    # make the powheg commands
    pcmdbase = 'python ./run_pwg_condor.py'
    pcmdargs = ' -i {} -m ggHH -f {}'.format(inputfile_rel, workdir_rel)
    pcmdargs += ' -j 20 -q testmatch'
    pcmds = []
    for x in [1,2,3,4,5]:
        pcmd = pcmdbase + ' -p 1 -x {}'.format(x) + pcmdargs
        pcmds.append(pcmd)
    for p in [2,3]:
        pcmd = pcmdbase + ' -p {}'.format(p) + pcmdargs
        pcmds.append(pcmd)

    # add the final command to create the gridpack
    pcmd = pcmdbase + ' -p 9'
    pcmd += ' -i {} -m ggHH -f {} -k 1'.format(inputfile_rel, workdir_rel)
    pcmds.append(pcmd)

    # make the total command sequence
    cmds = []
    for cmd in pcmds:
        fullcmd = 'cd {}; cmsenv; {}'.format(powhegdir, cmd)
        cmds.append(fullcmd)

    # print the commands
    if args.outputfile is None:
        print('Generated following commands:')
        for cmd in cmds: print(cmd)

    # write to file
    if args.outputfile is not None:
        with open(args.outputfile, 'w') as f:
            for cmd in cmds: f.write(cmd+'\n')
        print('Commands written to {}'.format(args.outputfile))
