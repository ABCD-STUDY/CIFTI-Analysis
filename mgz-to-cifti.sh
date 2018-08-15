#!/bin/bash
# Convert full resolution DAIC data to HCP CIFTI
# Richard Watts, April 2018

if [[ $# -eq 0 ]] ; then
    echo 'Error: No task specified'
    echo 'e.g. mgz-to-cifti.sh 2_back_vs_0_back 5 5'
    exit 0
fi

echo $1

task=$1
smoothSurf=$2
smoothVol=$3

for run in 1 2
do
    for hemi in l r
    do
        hemiup=$(tr '[a-z]' '[A-Z]' <<< $hemi)

        echo 'Processing' ${task} ${run} ${hemi} ${hemiup}
        # Smooth data, 16 iterations ~ 5mm. No longer necessary, done after CIFTI conversion
#        mri_surf2surf --srcsubject fsaverage --srcsurfval taskBOLD_${task}_run_${run}-${hemi}h.mgz \
#                --trgsubject fsaverage --trgsurfval taskBOLD_${task}_run_${run}-${hemi}h_sm.mgz \
#                --nsmooth-in 16 --hemi ${hemi}h


        # Convert to GIFTI using fsaverage/?h.sphere
        mris_convert -f taskBOLD_${task}_run_${run}-${hemi}h.mgz $FREESURFER_HOME/subjects/fsaverage/surf/${hemi}h.white \
                        taskBOLD_${task}_run_${run}-${hemi}h.func.gii

        # Resample to HCP 32k template
        wb_command -metric-resample taskBOLD_${task}_run_${run}-${hemi}h.func.gii \
                                    ../../standard_mesh_atlases/resample_fsaverage/fsaverage_std_sphere.${hemiup}.164k_fsavg_${hemiup}.surf.gii \
                                    ../../standard_mesh_atlases/resample_fsaverage/fs_LR-deformed_to-fsaverage.${hemiup}.sphere.32k_fs_LR.surf.gii \
                                    ADAP_BARY_AREA \
                                    ${task}.run${run}.${hemi}.32k_fs_LR.func.gii \
                                    -area-metrics \
                                    ../../standard_mesh_atlases/resample_fsaverage/fsaverage.${hemiup}.midthickness_va_avg.164k_fsavg_${hemiup}.shape.gii \
                                    ../../standard_mesh_atlases/resample_fsaverage/fs_LR.${hemiup}.midthickness_va_avg.32k_fs_LR.shape.gii
        # Mask out the medial wall
        wb_command -metric-mask ${task}.run${run}.${hemi}.32k_fs_LR.func.gii  \
                   ${HOME}/projects/Pipelines/global/templates/standard_mesh_atlases/${hemiup}.atlasroi.32k_fs_LR.shape.gii \
                   ${task}_mask.run${run}.${hemi}.32k_fs_LR.func.gii                            
    done


    cut  -c 7-17 taskBOLD_${task}_run_${run}-lh.csv > tmp.txt
    tail -n +2 tmp.txt > names.txt

    # Combine left and right hemispheres
    wb_command -cifti-create-dense-scalar ${task}_run${run}.dscalar.nii \
                                          -left-metric ${task}_mask.run${run}.l.32k_fs_LR.func.gii \
                                          -right-metric ${task}_mask.run${run}.r.32k_fs_LR.func.gii \
                                          -name-file names.txt

    # Smoothing
    wb_command -cifti-smoothing ${task}_run${run}.dscalar.nii ${smoothSurf} ${smoothVol} COLUMN ${task}_run${run}_sm${smoothSurf}.dscalar.nii \
               -left-surface ../../standard_mesh_atlases/resample_fsaverage/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
               -left-corrected-areas ../../standard_mesh_atlases/resample_fsaverage/fs_LR.L.midthickness_va_avg.32k_fs_LR.shape.gii \
               -right-surface ../../standard_mesh_atlases/resample_fsaverage/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii \
               -right-corrected-areas ../../standard_mesh_atlases/resample_fsaverage/fs_LR.R.midthickness_va_avg.32k_fs_LR.shape.gii

done
