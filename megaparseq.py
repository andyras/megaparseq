#!/usr/bin/env python2.7

debug = True

import argparse

parser = argparse.ArgumentParser(description='Script to process Q-Chem outputs to get coordinates and such')
parser.add_argument('--job', '-j', help='Q-Chem job number', type=int, default=0)
parser.add_argument('qfile', help='Q-Chem output file', type=str)

args = parser.parse_args()

import sys
import os

def getNthJob(f, n):
    '''
    Returns nth job from qchem output file f
    '''
    # get indices where jobs start
    indices = [i for (i, x) in enumerate(f) if x[0:11] == 'Running Job']
    nJobs = len(indices)

    # if no jobs, bomb out
    if (nJobs < 1):
        print 'There are no jobs in the file.'
        sys.exit()

    # if not enough jobs, bomb out
    if (nJobs < n):
        print 'There are less than %d jobs in the file.' % n
        sys.exit()

    # return last job when in doubt
    if (n < 1):
        n = nJobs

    if (debug):
        print 'Returning job number %d' % args.job

    # for last job, return until end of file
    if (n == nJobs):
        return f[indices[n-1]:(len(f)-1)]
    else:
        return f[indices[n-1]:(indices[n]-1)]

def getNAtoms(j):
    '''
    returns the number of atoms in a Q-Chem job.
    '''
    nLines = len(j)
    ii = 0
    
    for ii in range(len(j)):
        if (j[ii][0:10] == '   NAtoms,'):
            nAtoms = int(j[ii+1].split()[0])
            if (debug):
                print 'There are %d atoms.' % nAtoms
            return nAtoms

    print 'NAtoms not specified.'
    sys.exit()

def getNthCoords(j, n):
    '''
    Returns the nth set of atomic coordinates from the q-chem job j.
    '''
    # get indices where coordinates start
    indices = [i for (i, x) in enumerate(j) if x[0:46] == '                       Coordinates (Angstroms)']
    nCoords = len(indices)

    # if no coords, bomb out
    if (nCoords < 1):
        print 'There are no sets of coordinates in the job.'
        sys.exit()

    # if not enough coords, bomb out
    if (nCoords < n):
        print 'There are less than %d sets of coordinates in the job.' % n
        sys.exit()

    # return last set of coords when in doubt
    if (n < 1):
        n = nCoords

    if (debug):
        print 'Returning coordinate set number %d' % n

    # return set of coordinates
    natoms = getNAtoms(j)
    # lines with coordinates start 2 after the line with 'Coordinates (Angstroms)'
    start = indices[n-1] + 2

    coords = []
    for ii in range(start, start + natoms):
        line = j[ii].split()
        coords.append(line[1:5])

    return coords


# read in file
fileStr = []
with open(args.qfile, 'r') as f:
    fileStr = f.readlines()

# find selected job
job = getNthJob(fileStr, args.job)

# find last set of Cartesian coordinates
coords = getNthCoords(job, 0)
if (debug):
    print coords

# find Mulliken charges (if present)

# print .xyz to file
xyzfile = os.path.splitext(args.qfile)[0]+'_.xyz'
if (debug):
    print '.xyz output file is %s' % xyzfile

with open(xyzfile, 'w') as f:
    for c in coords:
        f.write('%s %s %s %s\n' % (c[0], c[1], c[2], c[3]))

# print charges to file

# check for error code from Q-chem
