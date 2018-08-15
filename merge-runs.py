#!/usr/bin/env python
#
# Richard Watts, Department of Radiology, University of Vermont, Match 2018
# 
# 
# Requires numpy and pandas libraries. The easiest way to get a python installation with all the necessary libraries is to install <a href='https://www.anaconda.com/download'>anaconda</a>

import numpy as np
import pandas as pd
import os,sys


# Data files can be combined with 'inner' (intersection, only subjects in all files are included) or 'outer' (union, all subjects in any of the files are included). Note that using 'inner', adding extra files may decrease the number of subjects.

if len(sys.argv) != 2:
    print('Error: No task specified')
    print('e.g. merge-runs 2_back_vs_0_back')
    sys.exit(1)

task = sys.argv[1]

mgzFile = ['taskBOLD_{0}_run_1-lh.csv'.format(task), 'taskBOLD_{0}_run_1-rh.csv'.format(task),
           'taskBOLD_{0}_run_2-lh.csv'.format(task), 'taskBOLD_{0}_run_2-rh.csv'.format(task)]

NDARFolder = '/Users/watts/Dropbox/ABCD_RELEASE_1/'
NDARdata = 'abcd_mrinback01.txt'

combine = 'inner'

print('Reading {0}'.format(mgzFile[0]))
df = pd.read_table(mgzFile[0],sep=',', header=0)
df.index = 'NDAR_' + df['StudyID'].str[5:16]

print('Found {0} subjects'.format(len(df.index)))
df = df[~df.index.duplicated(keep='first')]
print('Found {0} subjects after removal of duplicates'.format(len(df.index)))

for file in range(1,len(mgzFile)):
    print('Reading {0}'.format(mgzFile[file]))
    dftmp = pd.read_table(mgzFile[file],sep=',',header=0)
    dftmp.index = 'NDAR_' + dftmp['StudyID'].str[5:16]
    dftmp = dftmp[~dftmp.index.duplicated(keep='first')]

    df = pd.merge(df,dftmp, how=combine, left_index=True, right_index=True, suffixes=('', '_y'))
    print('Found {0} subjects'.format(len(df.index)))

    to_drop = [x for x in df if x.endswith('_y')]
    df.drop(to_drop, axis=1, inplace=True)
    
#print('Reading {0}'.format(NDARdata))   
#dftmp = pd.read_table(NDARFolder+NDARdata,sep='\t',header=0, index_col=3, skiprows=[1])
#df = pd.merge(df, dftmp,how=combine, left_index=True, right_index=True, suffixes=('', '_y'))
#to_drop = [x for x in df if x.endswith('_y')]
#df.drop(to_drop, axis=1, inplace=True)
#print('Found {0} subjects'.format(len(df.index)))


for subject in df.index:
    command = ('wb_command -cifti-math \'(run1+run2)/2\' '
                          + '-var run1 subjects/{0}-1.dscalar.nii -var run2 subjects/{0}-2.dscalar.nii '
                          + 'subjects/{0}.dscalar.nii').format(subject)
    print(command)
    os.system(command)

df.to_csv('subjects.txt', columns=[], header=None, index=True)
