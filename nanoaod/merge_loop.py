# Merge the output of NanoAOD production
# Looper over multiple samples


import os
import sys
import six
import glob
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--samples', required=True, type=os.path.abspath, nargs='+',
      help='Paths to samples (separated by spaces, can use wildcards)')
    parser.add_argument('-o', '--outputdir', required=True, type=os.path.abspath,
      help='Path to top-level output directory where to store the merged samples')
    parser.add_argument('-g', '--group', default=-1, type=int,
      help='Group size of files to merge (default: merge all files per sample into 1)')
    parser.add_argument('--cmssw', default=None,
      help='Path to CMSSW installation to do cmsenv (needed for haddnano.py)'
          +' (choose an intallation compatible with current el9 lxplus architecture, e.g. 14+)')
    parser.add_argument('-r', '--runmode', default='condor', choices=['condor','local'],
      help='Run in condor job or locally in the terminal')
    args = parser.parse_args()
    print('Running merge_loop.py with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line args
    for sample in args.samples:
        if not os.path.exists(sample):
            msg = 'Provided sample {} does not exist.'.format(sample)
            raise Exception(msg)
    cmssw = os.path.abspath(args.cmssw) if args.cmssw is not None else None
    if cmssw is not None:
        if not os.path.exists(cmssw):
            msg = 'Provided CMSSW installation {} does not exist.'.format(cmssw)
            raise Exception(msg)

    # count the files in the samples
    # (just for info printing)
    for sample in args.samples:
        pattern = os.path.join(sample, '**', 'ntuple_*.root')
        files = sorted(glob.glob(pattern, recursive=True))
        print('Found {} files for sample {}.'.format(len(files), sample))

    # manage output directory
    if os.path.exists(args.outputdir):
        msg = 'WARNING: output directory {} already exists'.format(args.outputdir)
        msg += ', clean it? (y/n)'
        print(msg)
        go = six.moves.input()
        if go!='y': sys.exit()
        os.system('rm -r {}'.format(args.outputdir))
    os.makedirs(args.outputdir)

    # make separate output directories per sample
    outputdirs = []
    for sample in args.samples:
        outputdir = os.path.join(args.outputdir, os.path.basename(sample))
        outputdirs.append(outputdir)

    # print and ask for confirmation
    print('Will merge the samples as follows:')
    for sample, outputdir in zip(args.samples, outputdirs):
        print('  - {} -> {}'.format(sample, outputdir))
    print('Continue> (y/n)')
    go = six.moves.input()
    if go!='y': sys.exit()

    # loop over samples
    cmds = []
    for sample, outputdir in zip(args.samples, outputdirs):
        # make the merge command
        cmd = 'python3 merge.py'
        cmd += ' -s {}'.format(sample)
        cmd += ' -o {}'.format(outputdir)
        cmd += ' -g {}'.format(args.group)
        if cmssw is not None: cmd += ' --cmssw {}'.format(cmssw)
        cmd += ' -r {}'.format(args.runmode)
        cmds.append(cmd)

    # run commands
    for cmd in cmds: os.system(cmd)
