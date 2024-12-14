# Prepare and run the compilation of a Powheg input file with configurable H mass

import os
import sys
import six
import argparse
sys.path.append('../jobtools')
import condortools as ct

if __name__=='__main__':
    
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to the baseline Powheg .input file for this process')
    parser.add_argument('-m', '--mass', default=125, type=int,
      help='Mass for the H boson (default: unmodified at 125 GeV)')
    parser.add_argument('-w', '--workdir', required=True, type=os.path.abspath,
      help='Set a unique working directory for this process (MUST be inside bin/Powheg!)')
    parser.add_argument('-r', '--runmode', choices=['condor', 'local'], default='condor',
      help='Run in condor job or locally in the terminal')
    parser.add_argument('--el7', default=False, action='store_true',
      help='Run in an el7 container')
    parser.add_argument('--preparegrid', default=False, action='store_true',
      help='Do grid preprocessing steps after the compilation')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.inputfile):
        msg = 'Provided input file {} does not exist.'.format(args.inputfile)
        raise Exception(msg)
    if os.path.exists(args.workdir):
        msg = 'Provided working directory {} already exists.'.format(args.workdir)
        msg += ' Overwrite? (y/n)'
        print(msg)
        go = six.moves.input()
        if go!='y': sys.exit()
        os.system('rm -r {}'.format(args.workdir))
    os.makedirs(args.workdir)

    # copy the input file to the working directory
    newname = os.path.basename(args.inputfile).replace('.input', '_m_{}.input'.format(args.mass))
    new_input_file = os.path.join(args.workdir, newname)
    cmd = 'cp {} {}'.format(args.inputfile, new_input_file)
    print('Running {}'.format(cmd))
    os.system(cmd)

    # modify the mass setting in the input file
    cmd = "sed -i -e 's/hmass 125/hmass {}/g' {}".format(args.mass, new_input_file)
    print('Running {}'.format(cmd))
    os.system(cmd)

    # find the powheg directory from where to run the compilation command
    # (assume the working directory is located inside that directory)
    tag = 'genproductions/bin/Powheg/'
    try: powhegdir = os.path.join(args.workdir.split(tag)[0], tag)
    except:
        msg = 'Could not retrieve Powheg base directory from the provided working directory.'
        raise Exception(msg)
    print('Found Powheg base directory {}'.format(powhegdir))

    # make input file and working directory relative to the powheg path
    # (seems to be needed for ./run_pwg_condor.py to run correctly)
    inputfile_rel = os.path.relpath(new_input_file, powhegdir)
    workdir_rel = os.path.relpath(args.workdir, powhegdir)
    print('Found following relative paths:')
    print(' - input file: {}'.format(inputfile_rel))
    print(' - working directory: {}'.format(workdir_rel))

    # retrieve the tool directory (for use later)
    thisdir = os.path.abspath(os.path.dirname(__file__))
    toolsdir = os.path.abspath(os.path.join(thisdir, '../tools'))

    # make the commands and write to a script
    exe = 'exe_{}.sh'.format(os.path.basename(args.workdir))
    pcmd = 'python ./run_pwg_condor.py -p 0'
    pcmd += ' -i {} -m ggHH -f {}'.format(inputfile_rel, workdir_rel)
    pcmd += ' --svn 4038' # see main README for instructions on this
    with open(exe, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
        f.write('cd {}\n'.format(powhegdir))
        f.write('cmsenv\n')
        f.write(pcmd+'\n')
    os.system('chmod +x {}'.format(exe))
    cmd = './{}'.format(exe)

    # add grid preprocessing commands if requested
    preprocess_script = os.path.join(toolsdir, 'preprocess_grid_files.sh')
    with open(exe, 'a') as f:
        f.write('bash {} {}\n'.format(preprocess_script, args.workdir))

    # make el7 wrapping if requested
    if args.el7:
        run_in_container_script = os.path.join(toolsdir, 'run_in_el7_container.sh')
        cmd = 'bash {} {}'.format(run_in_container_script, os.path.abspath(exe))

    # submit job
    if args.runmode=='condor': ct.submitCommandAsCondorJob('cjob_compilation', cmd, jobflavour='workday')

    # for testing: run locally
    if args.runmode=='local': os.system(cmd)
