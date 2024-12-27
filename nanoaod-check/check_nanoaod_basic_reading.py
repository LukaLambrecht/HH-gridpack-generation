# Basic file reading checks of privately produced NanoAOD


import os
import sys
import numpy as np
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to NanoAOD input file')
    args = parser.parse_args()
    print('Running check_hh4b_nanoaod_gen.py with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # read input file
    events = NanoEventsFactory.from_root(
               {args.inputfile: 'Events'},
               schemaclass=NanoAODSchema).events()
    print('Number of events: {}'.format(ak.num(events.run.compute(), axis=0)))
    print('Available branches:')
    print(events.fields)
