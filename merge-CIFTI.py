#!/usr/bin/env python

import os, sys
import numpy as np

def combineFiles(outFile, inFiles):
    command = baseCommand + 'subjects/tmp.dscalar.nii '

    for subjectName in inFiles:
        filename = 'subjects/{0}.dscalar.nii'.format(subjectName)

        if os.path.exists(filename):
            command += '-cifti {0} '.format(filename)
        else:
            print('Warning: {0} not found'.format(filename))

    print(command)
    os.system(command)
    command = 'mv subjects/tmp.dscalar.nii subjects/{0}.dscalar.nii'.format(outFile)
    print(command)
    os.system(command)


try:
    subject = sys.argv[1]
except IndexError:
    print("Usage: {0} <subjects>".format(sys.argv[0]))
    print('e.g. merge-CIFTI.py contrast_design_subjects.csv')
    sys.exit(1)

baseCommand = 'wb_command -cifti-merge '
nsubjects = 0
stepSize = 100
outFile = 'all-subjects'

with open(sys.argv[1], 'r') as ifile:
    subjectList = ifile.read().splitlines()
nSubjects = len(subjectList)

print(nSubjects)

for i in range(0,nSubjects/stepSize + 1):
    startIndex = i*stepSize
    endIndex = min(startIndex+stepSize, nSubjects)
    print(startIndex, endIndex)

    if i==0:
        combineFiles(outFile, subjectList[startIndex:endIndex])
    else:
        combineFiles(outFile, [outFile] + subjectList[startIndex:endIndex])


command = 'mv subjects/all-subjects.dscalar.nii ./'
print(command)
os.system(command)
