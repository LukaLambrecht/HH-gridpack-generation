#!/usr/bin/env python3

# Extract (untar) a gridpack


import os
import sys
import six
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gridpack', required=True, type=os.path.abspath,
      help='Path to the gridpack')
    parser.add_argument('-o', '--outputdir', required=True, type=os.path.abspath,
      help='Path for the extracted gridpack')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line args
    if not os.path.exists(args.gridpack):
        msg = 'Provided gridpack {} does not exist.'.format(args.gridpack)
        raise Exception(msg)
    if os.path.exists(args.outputdir):
        msg = 'Provided output directory {} already exists.'.format(args.outputdir)
        raise Exception(msg)

    # set path to this directory and other path-related variables
    # (for use later)
    thisdir = os.path.abspath(os.path.dirname(__file__))
    gridpackbase = os.path.basename(args.gridpack)
    gridpackname = os.path.splitext(gridpackbase)[0]

    # make output directory for unpacking the gridpack
    os.makedirs(args.outputdir)

    # copy the gridpack to working directory and unpack it
    print(f'Unpacking {args.gridpack} in {args.outputdir}...')
    os.system(f'cp {args.gridpack} {args.outputdir}')
    os.system(f'cd {args.outputdir}; tar -xvzf {gridpackbase}')

    # remove the gridpack itself from the output directory
    tmpgridpack = os.path.join(args.outputdir, gridpackbase)
    os.system(f'rm {tmpgridpack}')
