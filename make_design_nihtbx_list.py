#!/usr/bin/env python

# Richard Watts, Department of Radiology, University of Vermont, April 2018
# 
import numpy as np
import pandas as pd
import sys

task = sys.argv[1]
contrast = sys.argv[2]
design = sys.argv[3]
subjectFile = 'subjects.txt'
createSiteContrast = False


if task=='nback':
    NDARdata = ['nbackgordonp101.txt', 'abcd_mrinback01.txt', 'abcd_tbss01.txt']
    thresholdDoF = 543
    nonImagingEVs = ['interview_age','genderNum','nihtbx_list_uncorrected']
elif task=='sst':
    NDARdata = ['mrisstp101.txt', 'abcd_sst01.txt']
    thresholdDoF = 655
    nonImagingEVs = ['interview_age','genderNum','beh_sst_ssrt_mean_total']
elif task=='mid':
    NDARdata = ['gordonp101.txt']
    thresholdDoF = 601
    nonImagingEVs = ['interview_age','genderNum']

outSubjects = '{0}_{1}_subjects.csv'.format(contrast,design)
outDesign = '{0}_{1}_design.csv'.format(contrast,design)
outContrast = '{0}_{1}_contrast.csv'.format(contrast,design)

NDARFolder = '~/ABCD_RELEASE_1/'
combine = 'inner'

print('Reading {0}'.format(subjectFile))
df = pd.read_table(subjectFile,sep='\t', header=None, names=['subjectkey'])
df.set_index('subjectkey', inplace=True)

print('Found {0} subjects'.format(len(df.index)))

for file in range(0,len(NDARdata)):
    print('Reading {0}'.format(NDARdata[file]))
    dftmp = pd.read_table(NDARFolder+NDARdata[file],sep='\t',header=0, skiprows=[1])
    dftmp.set_index('subjectkey', inplace=True)
    if 'lmt_run' in dftmp.columns:
        dftmp = dftmp[dftmp.lmt_run=='AVERAGE']

    df = pd.merge(df,dftmp, how=combine, left_index=True, right_index=True, suffixes=('', '_y'))
    to_drop = [x for x in df if x.endswith('_y')]
    df.drop(to_drop, axis=1, inplace=True)

    
print('Found {0} subjects after merging'.format(len(df.index)))

df['vendorGE'] = df.visit.str.startswith('G').astype(float)
df['vendorSiemens'] = df.visit.str.startswith('S').astype(float)
df['vendorPhilips'] = df.visit.str.startswith('P').astype(float)

siteOneHot = pd.get_dummies(df['visit'].str.slice(0,4))
nSites = len(siteOneHot.columns)

print(siteOneHot.sum())

df = df.join(siteOneHot)

df['genderNum'] = (df['gender'] == 'M').astype(float)
df['constant']= 1.0

print('{0} subjects before filtering'.format(len(df.index)))

df = df[df['mid_beta_seg_dof']>thresholdDoF]

# nBack performance
if task=='nback':
    df = df[df['beh_nback_perform_flag']==1]

# SST performance
if task=='sst':
    df = df[df['beh_mid_perform_flag']==1]
    df.drop('NDAR_INVD806H93D', inplace=True)

# Drop any subjects with missing imaging data. There must be a neater way to do this
bad = df[nonImagingEVs].isnull().any(axis=1)
good = (bad == False)
df = df[good]

print('{0} subjects after filtering'.format(len(df.index)))

# Demean non-imaging values
for column in nonImagingEVs:
    if column in df.columns:
        df[column] = df[column]-df[column].mean()

columns = list(nonImagingEVs) + list(siteOneHot.columns)


print(len(columns))
print(columns)
    
# Write custom data to file
df.to_csv(outDesign, header=None, index=False, float_format='%.3f', columns=columns)
df.to_csv(outSubjects, header=None, index=True, columns=[])

# Create contrast file
mainEffect = np.hstack([np.zeros(len(nonImagingEVs)), np.ones(nSites)/nSites])
contrasts = np.vstack([mainEffect, np.identity(len(columns))])

if createSiteContrast:
    pd.DataFrame(contrasts).to_csv(outContrast, header=None, index=False)
else:
    pd.DataFrame(contrasts).head(len(nonImagingEVs)+1).to_csv(outContrast, header=None, index=False)
