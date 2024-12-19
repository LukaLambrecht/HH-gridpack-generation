# Gen-level checks of privately produced NanoAOD with different H masses


import os
import sys
import numpy as np
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

import matplotlib.pyplot as plt

import argparse


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
      help='Path to NanoAOD input file')
    parser.add_argument('--xmin', default=100, type=int,
      help='x-axis minimum for invariant mass plots')
    parser.add_argument('--xmax', default=150, type=int,
      help='x-axis maximum for invariant mass plots')
    parser.add_argument('--nbins', default=50, type=int,
      help='number of bins for invariant mass plots')
    args = parser.parse_args()
    print('Running check_hh4b_nanoaod_gen.py with following configuration:')
    for arg in vars(args): print('  - {}: {}'.format(arg, getattr(args,arg)))

    # read input file
    events = NanoEventsFactory.from_root(
               {args.inputfile: 'Events'},
               schemaclass=NanoAODSchema).events()
    print('Number of events: {}'.format(ak.num(events.run.compute(), axis=0)))

    # get the genparticles and select H bosons
    # (based on PDGID and status codes)
    genparts = events.GenPart
    h = genparts[(genparts.pdgId==25) & (genparts.hasFlags(['isLastCopy']))]
    
    # print the number and mass of selected H bosons
    print('Number of selected H bosons:')
    print(ak.num(h.mass.compute()))
    print('H boson mass:')
    print(h.mass.compute())

    # find children of the selected H bosons
    h_children = h.children
    print('Pdg ID of H boson decay products:')
    print(h_children.pdgId.compute())

    # separate first and second H boson per event
    h1 = h[:, 0]
    h2 = h[:, 1]
    h1_children = h1.children
    h2_children = h2.children

    # make invariant mass distribution of H children
    h1_children_mass = (h1_children[:,0] + h1_children[:,1]).mass.compute()
    h2_children_mass = (h2_children[:,0] + h2_children[:,1]).mass.compute()
    print('Invariant mass of H1 decay products:')
    print(h1_children_mass)
    print('Invariant mass of H2 decay products:')
    print(h2_children_mass)

    # select gen-level b-jets with basic quality criteria
    genjets = events.GenJet
    bjets = genjets[ (genjets.hadronFlavour==5)
                     & (genjets.pt>30)
                     & (np.abs(genjets.eta)<5) ]

    # select events with at least 4 selected b-jets
    event_selection_mask = (ak.num(bjets)>=4)
    print(event_selection_mask.compute())
    npass = ak.sum(event_selection_mask).compute()
    ntot = len(event_selection_mask.compute())
    print('Event selection: {} / {} events passing'.format(npass, ntot))

    # match b-jets to H boson decay products
    h1_genjets = h1_children[event_selection_mask].nearest(bjets[event_selection_mask])
    h2_genjets = h2_children[event_selection_mask].nearest(bjets[event_selection_mask])

    # make invariant mass distributions of matched genjets
    h1_genjets_mass = (h1_genjets[:,0] + h1_genjets[:,1]).mass.compute()
    h2_genjets_mass = (h2_genjets[:,0] + h2_genjets[:,1]).mass.compute()
    print('Invariant mass of H1 decay products matched gen-jets:')
    print(h1_genjets_mass)
    print('Invariant mass of H2 decay products matched gen-jets:')
    print(h2_genjets_mass)

    # make a plot of decay product invariant mass
    fig, axs = plt.subplots(ncols=2, figsize=(12,6))
    bins = np.linspace(args.xmin, args.xmax, num=args.nbins)
    ax = axs[0]
    ax.hist(h1_children_mass, bins=bins, color='dodgerblue')
    ax.set_xlabel('Invariant mass of H_1 decay products (GeV)', fontsize=12)
    ax.set_ylabel('Number of events', fontsize=12)
    ax = axs[1]
    ax.hist(h2_children_mass, bins=bins, color='dodgerblue')
    ax.set_xlabel('Invariant mass of H_2 decay products (GeV)', fontsize=12)
    ax.set_ylabel('Number of events', fontsize=12)
    fig.savefig('results_mass.png')

    # make a plot of gen jet invariant mass
    fig, axs = plt.subplots(ncols=2, figsize=(12,6))
    bins = np.linspace(args.xmin, args.xmax, num=args.nbins)
    ax = axs[0]
    ax.hist(h1_genjets_mass, bins=bins, color='dodgerblue')
    ax.set_xlabel('Invariant mass of H_1 matched gen-jets (GeV)', fontsize=12)
    ax.set_ylabel('Number of events', fontsize=12)
    ax = axs[1]
    ax.hist(h2_genjets_mass, bins=bins, color='dodgerblue')
    ax.set_xlabel('Invariant mass of H_2 matched gen-jets (GeV)', fontsize=12)
    ax.set_ylabel('Number of events', fontsize=12)
    fig.savefig('results_mass_genjets.png')
