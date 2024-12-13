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
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.gridpack):
        msg = 'Provided gridpack {} does not exist.'.format(args.gridpack)
        raise Exception(msg)

    # make executable script
    shfile = 'check_gridpack.sh'
    with open(shfile, 'w'):
        shfile.write('mkdir -p $TMPDIR/llambrec/\n')
        shfile.write('cd $TMPDIR/llambrec/\n')
        shfile.write('cp {} ./gridpack.tgz\n')
        shfile.write('tar -xf ./gridpack.tgz\n')
        shfile.write('./gridpack/\n')
        shfile.write('./runcmsgrid.sh {} 1 1\n'.format(args.nevents))

    # run the script in a job
    cmd = 'bash {}'.format(shfile)
    ct.submitCommandAsCondorJob('cjob_check_gridpack', cmd)
