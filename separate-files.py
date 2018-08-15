#!/usr/bin/env python

import pandas as pd
import os, sys

if len(sys.argv) != 2:
    print('Error: No task specified')
    print('e.g. separate-files 2_back_vs_0_back')
    sys.exit(1)

if not os.path.exists('subjects'):
    os.makedirs('subjects')

for run in {'1','2'}:
    subjectFile = 'taskBOLD_{0}_run_{1}-rh.csv'.format(sys.argv[1], run)

    print('Reading {0}'.format(subjectFile))
    df = pd.read_table(subjectFile,header=0, sep=',',index_col=0)

    nSubjects = len(df.index)
    print('{0} subjects'.format(nSubjects))

    f = open('subjects-{0}.txt'.format(run),'w')

    for index in range(0,nSubjects):
        subjectID = 'NDAR_' + df.iloc[index,0][5:16]
        outFile = 'subjects/' + subjectID + '-' + run + '.dscalar.nii'
    
        cmd = 'wb_command -cifti-merge {0} -cifti {1}_run{2}_sm5.dscalar.nii -column {3}'.format(outFile, sys.argv[1], run, index+1)
        print(cmd)
        os.system(cmd)
    
        f.write(subjectID+'\n')
f.close()

