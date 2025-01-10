#!/usr/bin/env python3

# Patch a created gridpack


import os
import sys
import six
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gridpack', required=True, type=os.path.abspath,
      help='Path to the gridpack to patch')
    parser.add_argument('-o', '--output', default=None,
      help='Path for the patched output gridpack (default: overwrite input)')
    parser.add_argument('--inputfile', default=None,
      help='Alternative powheg.input file')
    parser.add_argument('--weightfile', default=None,
      help='Alternative scales and pdf weight file (to replace pwg-rwl.dat)')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line args
    if not os.path.exists(args.gridpack):
        msg = 'Provided gridpack {} does not exist.'.format(args.gridpack)
        raise Exception(msg)
    if args.output is None:
        msg = 'WARNING: no output specified. Overwrite input gridpack? (y/n)'
        print(msg)
        go = six.moves.input()
        if go!='y': sys.exit()
        args.output = args.gridpack
    else: args.output = os.path.abspath(args.output)
    if args.inputfile is not None: args.inputfile = os.path.abspath(args.inputfile)
    if args.weightfile is not None: args.weightfile = os.path.abspath(args.weightfile)

    # set path to this directory and other path-related variables
    # (for use later)
    thisdir = os.path.abspath(os.path.dirname(__file__))
    gridpackbase = os.path.basename(args.gridpack)
    gridpackname = os.path.splitext(gridpackbase)[0]
    tmpdir = f'/tmp/{gridpackname}'

    # make temporary working directory for unpacking the gridpack
    if os.path.exists(tmpdir): os.system(f'rm -r {tmpdir}')
    os.makedirs(tmpdir)

    # copy the gridpack to working directory and unpack it
    print(f'Unpacking {args.gridpack} in {tmpdir}...')
    os.system(f'cp {args.gridpack} {tmpdir}')
    os.system(f'cd {tmpdir}; tar -xvzf {gridpackbase}')

    # remove the gridpack itself from the working directory
    tmpgridpack = os.path.join(tmpdir, gridpackbase)
    os.system(f'rm {tmpgridpack}')

    # --- start patching here ---

    # replace weight file
    if args.inputfile is not None:
        print('Replacing input file...')
        dest = os.path.join(tmpdir, 'powheg.input')
        os.system(f'cp {args.inputfile} {dest}')

    # replace weight file
    if args.weightfile is not None:
        print('Replacing weight file...')
        dest = os.path.join(tmpdir, 'pwg-rwl.dat')
        os.system(f'cp {args.weightfile} {dest}')

    # --- end patching ---
    
    # re-pack the gridpack
    print('Re-packing gridpack...')
    newgridpack = f'/tmp/{gridpackbase}'
    os.system(f'cd {tmpdir}; tar -cvzf {newgridpack} *')

    # move gridpack to desired output location
    print(f'Moving patched gridpack to {args.output}...')
    os.system(f'mv {newgridpack} {args.output}')
    print('Done.')
