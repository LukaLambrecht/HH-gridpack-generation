# Build the simpack and patch it with some configurable options


import os
import sys
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gridpack', required=True, type=os.path.abspath,
      help='Path to gridpack')
    parser.add_argument('-n', '--name', default=None,
      help='Name tag for folder structure and dataset (default: use gridpack name)')
    parser.add_argument('--events_per_job', default=-1, type=int,
      help='CRAB setting: number of events per job')
    parser.add_argument('--total_events', default=-1, type=int,
      help='CRAB setting: total number of events to generate')
    parser.add_argument('-o', '--outputdirbase', default=None,
      help='CRAB setting: output base directory')
    parser.add_argument('-s', '--site', default=None,
      help='CRAB setting: storage site')
    # to do: add more options
    args = parser.parse_args()
    print('Running run_powheg_commands_crontab.py with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # check command line arg
    if not os.path.exists(args.gridpack):
        msg = 'Provided inputfile {} does not exist.'.format(args.gridpack)
        raise Exception(msg)

    # set path to private production work area
    thisdir = os.path.abspath(os.path.dirname(__file__))
    reldir = '../CMSSW_10_6_8/src/private_production/HIG-Run3Summer22EE'
    workdir = os.path.abspath(os.path.join(thisdir, reldir))

    # make and run command to build the simpack
    cmd = 'sh build_simpack.sh {} powheg cmssw-el8'.format(args.gridpack)
    fullcmd = 'cd {}; {}'.format(workdir, cmd)
    print('Building simpack...')
    os.system(fullcmd)

    # rename the folder
    if args.name is not None:
        oldbasename = os.path.join(workdir, 'simulation')
        newbasename = os.path.join(workdir, 'simpacks')
        if not os.path.exists(newbasename): os.makedirs(newbasename)
        oldname = os.path.join(oldbasename, os.path.basename(args.gridpack))
        newname = os.path.join(newbasename, args.name)
        print('Moving {} to {}...'.format(oldname, newname))
        os.system('mv {} {}'.format(oldname, newname))
        os.system('rm -r {}'.format(oldbasename))
    
    # patch the crab configuration file
    crabconfigfile = os.path.join(newname, 'crabConfig.py')
    patches = []
    if args.name is not None:
        patches.append("sed -i 's/config.General.requestName .*/config.General.requestName = \"{}\"/' {}".format(args.name, crabconfigfile))
        patches.append("sed -i 's/config.General.workArea .*/config.General.workArea = \"{}\"/' {}".format(args.name, crabconfigfile))
        patches.append("sed -i 's/config.Data.outputDatasetTag .*/config.Data.outputDatasetTag = \"{}\"/' {}".format(args.name, crabconfigfile))
    if args.events_per_job > 0:
        patches.append("sed -i 's/config.Data.unitsPerJob .*/config.Data.unitsPerJob = {}/' {}".format(args.events_per_job, crabconfigfile))
    if args.total_events > 0:
        patches.append("sed -i 's/config.Data.totalUnits .*/config.Data.totalUnits = {}/' {}".format(args.total_events, crabconfigfile))
    if args.outputdirbase is not None:
        outputdirbase = args.outputdirbase.replace('/', '\/')
        patches.append("sed -i 's/config.Data.outLFNDirBase .*/config.Data.outLFNDirBase = \"{}\"/' {}".format(outputdirbase, crabconfigfile))
    if args.site is not None:
        patches.append("sed -i 's/config.Site.storageSite .*/config.Site.storageSite = \"{}\"/' {}".format(args.site, crabconfigfile))
    print('Patching the crab config file...')
    for patch in patches:
        os.system(patch)
