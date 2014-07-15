# Taku Ito
# Specific execute blocks, e.g., prepareMPRAGE, epiAlignment, etc.

import sys
sys.path.append('preprocbin')
from run_shell_cmd import run_shell_cmd
import os
import glob
import maskbin

class prepareMPRAGE():
    """
    DESCRIPTION: Prepares and compiles anatomical MRPRAGE from raw DICOM files.  Not for HCP data use.  For use on a single subject.
    PARAMETERS: 
    	conf - a subjectConfig file
    	logname - subject's log output filename
    """

    # Nothing to init, since nextInputFilename doesn't change after this block, but still for the sake of uniformity across all nodes.
    def __init__(self, conf):
        self.conf = conf

    def run(self, conf):    
        logname = conf.logname
        os.chdir(conf.subjfMRIDir) #change working directory to fMRI directory
            
        print 'Preparing MPRAGE file (anatomical image)'

        fileFindString = '*.dcm' #will search for a string that ends with '.dcm'

        ##****## In the future, will want to adjust this to use os.walk to search subdirectories for files of *.dcm
        dirName = glob.glob(conf.subjRawDataDir + conf.T1_image)[0] 
        dicomRenameDir = dirName + '/' + fileFindString

        #Sort DICOM files (to make sure they will be read in the order they were collected in) using Freesurfer
        print 'Sorting DICOM...'
        run_shell_cmd('dicom-rename ' + dicomRenameDir + ' --o ' + conf.basedir + 'SortedDICOMs/MPRAGE/MR',logname)

        #Convert DICOM files to NIFTI format using Freesurfer
        print 'Converting DICOM...'
        run_shell_cmd('mri_convert ' + conf.basedir + 'SortedDICOMs/MPRAGE/*-00001.dcm --in_type siemens --out_type nii mprage.nii.gz',logname)

        #Remove sorted DICOMs
        run_shell_cmd('rm -rf ' + conf.basedir + 'SortedDICOMs/MPRAGE',logname)

        ####
        # Skull strip MPRAGE
        # Use Freesurfer's skullstripping (very slow, but more accurate)
        if conf.runFreesurfer == True:
            run_shell_cmd('recon-all -subject ' + conf.subjID + ' -all -sd ' + conf.freesurferDir + ' -i mprage.nii.gz',logname)


        # Convert to NIFTI
        run_shell_cmd('mri_convert --in_type mgz --out_type nii ' + conf.freesurferDir + '/mri/brain.mgz mprage_skullstripped.nii',logname)


        # gzip files and removed uncompressed file
        run_shell_cmd('3dcopy mprage_skullstripped.nii mprage_skullstripped.nii.gz',logname)
        run_shell_cmd('rm mprage_skullstripped.nii',logname)

        # Compressing file
        run_shell_cmd('3dcopy mprage_skullstripped.nii.gz anat_mprage_skullstripped',logname)



class prepareEPI():
    """
    DESCRIPTION: Converts fMRI data to AFNI format from raw DICOMs.
    PARAMETERS: 
    	conf - a subjectConfig file
    	logname - subject's log output filename
    """
    def __init__(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append('epi')

    def run(self, conf):
        logname = conf.logname
        os.chdir(conf.subjfMRIDir)

        numRuns = len(conf.epi_series)
        # Getting raw fMRI data folder names
        # Modify: How to identify fMRI series directory in raw data [regular expression used to get series order correct]
        ### Edit this, not very clean ###
        rawDirRunList = []
        for run in range(numRuns):
        	# find epi series
        	searchPath = glob.glob(conf.subjRawDataDir + conf.epi_series[run])[0]
        	# append to rawDirRunList
        	rawDirRunList.append(searchPath)

        print 'Raw data folder order:', rawDirRunList

        #For-loop for functions used across multiple runs (prior to run-concatenation)
        for runNum in range(1,numRuns + 1):
            print '--Run', runNum, '---'

            fileFindString = '*.dcm'
            runRawDir = rawDirRunList[runNum-1]
            runRawFile = runRawDir + '/' + fileFindString
            
            # Sorting DICOM files (to make sure they will be read in the order they were collected in) using Freesurfer.
            run_shell_cmd('dicom-rename ' + runRawFile + ' --o ' + conf.basedir + '/SortedDICOMs/Run' + str(runNum) + '/MR',logname)
            
            # Converting from DICOM to NIFTI to AFNI format using Freesurfer
            run_shell_cmd('mri_convert ' + conf.basedir + '/SortedDICOMs/Run' + str(runNum) + '/*00001.dcm --in_type siemens --out_type nii epi_r' + str(runNum) + '.nii.gz',logname)
            run_shell_cmd('rm epi_r' + str(runNum) + '+orig*',logname)
            run_shell_cmd('3dcopy epi_r' + str(runNum) +'.nii.gz epi_r' + str(runNum),logname)
            run_shell_cmd('rm epi_r' + str(runNum) + '.nii.gz',logname)
            
            # Remove sorted DICOMs
            run_shell_cmd('rm -rf ' + conf.basedir + '/SortedDICOMs/Run' + str(runNum),logname)

            # If numTRsToSkip > 0, remove the first couple TRs for every epi run
            if conf.numTRsToSkip > '0':
                run_shell_cmd('3dcalc -a epi_r' + str(runNum) + '+orig"[' + conf.numTRsToSkip + '..$]" -expr ' + "'a' -prefix epi_r" + str(runNum) + ' -overwrite', logname)



    # 3rd Execute Block - Slice Time Correction
def sliceTimeCorrection(conf):
    """
    DESCRIPTION: Performs slice time correction on fMRI data (assuming not a multiband sequence)
    PARAMETERS: 
        conf - a subjectConfig file
        logname - subject's log output filename
    """

    def __init__(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append('stc_' + conf.nextInputFilename[-1])

    def run(self,conf):

        logname = conf.logname
        os.chdir(conf.subjfMRIDir)
        numRuns = len(conf.epi_series)

        for runNum in range(1, numRuns + 1):

            print ' - Slice Time Correction for Run', runNum, '-'
            
            run_shell_cmd('3dTshift -overwrite -Fourier -TR ' + conf.TR + ' -tpattern ' + conf.tpattern + ' -prefix stc_' + conf.nextInputFilename[-1] + '_r' + str(runNum) + ' ' + conf.nextInputFilename[-1] + '_r' + str(runNum) + '+orig', logname)
            
            rmFileName = glob.glob(conf.nextInputFilename[-1] + '_r' + str(runNum) + '????.????.gz')
            if rmFileName:
                run_shell_cmd('rm -v ' + rmFilename,logname)



class concatenateRuns():

    def __init__(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append(conf.nextInputFilename[-1] + '_allruns')
        # Update conf with new attributes/parameters

        # Construct Run List, even if this node isn't run
        numRuns = len(conf.epi_series)
        for runNum in range(1, numRuns+1):
            runList = runList + ' ' + conf.subjfMRIDir + conf.nextInputFilename[-1] + '_r' + str(runNum) + '+orig'
            concatString = concatString + ' ' + str(TRCount)
            TRCount = TRCount + conf.numTRs  ###EDIT THIS!!!

        self.conf.runList = runList
        self.conf.concatString = concatString


    def run(self, conf):
        logname = conf.logname
        os.chdir(conf.subjfMRIDir)
        runList = ' '
        concatString = '1D:'
        TRCount = 0

        numRuns = len(conf.epi_series)

        # Construct Run List
        for runNum in range(1, numRuns+1):
            runList = runList + ' ' + conf.subjfMRIDir + conf.nextInputFilename[-1] + '_r' + str(runNum) + '+orig'
            concatString = concatString + ' ' + str(TRCount)
            TRCount = TRCount + conf.numTRs  ###EDIT THIS!!!

        print '- Concatenating Runs -'
        print 'Run list:', runList
        print 'Concatenation string (onset times of each run):', concatString

        # Run command
        run_shell_cmd('rm -v ' + conf.nextInputFilename[-1] + '_allruns+orig*',logname)
        run_shell_cmd('3dTcat -prefix ' + conf.nextInputFilename[-1] + '_allruns ' + runList,logname)

        # Remove intermediate analysis file to save disk space
        rm_file = glob.glob(conf.nextInputFilename[-1] + 'r_*+????.????.gz')
        if rm_file: 
            run_shell_cmd('rm -v ' + rm_file,logname)





class talairachAlignment():

    def __init__(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append(conf.nextInputFilename[-1] + '_tlrc_al')

    def run(self, conf):    
        logname = conf.logname
        os.chdir(conf.subjfMRIDir)


        #### Talairach transform anatomical image
        print '-Run @auto_tlrc to talairach transform anatomical T1 image-'
        run_shell_cmd('@auto_tlrc -base ' + conf.atlasAnat + ' -input anat_mprage_skullstripped+orig -no_ss',logname)
        run_shell_cmd('ln -s ' + conf.atlasAnat + ' .',logname)
        run_shell_cmd('3dcopy anat_mprage_skullstripped+tlrc anat_mprage_skullstripped_tlrc.nii.gz', logname) #format into NIFTI format

        # Create Mask
        run_shell_cmd("3dcalc -overwrite -a anat_mprage_skullstripped+tlrc -expr 'is positive(a)' -prefix " + conf.subjMaskDir + "/wholebrain_mask.nii.gz" ,logname)
        # Link anatomical image to mask directory for checking alignment
        run_shell_cmd('ln -s anat_mprage_skullstripped_tlrc.nii.gz ' + conf.subjMaskDir,logname)


        print '-Run align_epi_anat.py to align EPIs to MPRAGE, motion correct, and Talairach transform EPIs (output in 222 space)-'

        print 'Make sure Python is version 2.6 or greater (ColeLabMac should be version 2.7)'
        run_shell_cmd('python -V',logname)

        # Correcting for motion, aligning fMRI data to MPRAGE, and aligning fMRI data to Talairach template [applying all transformation at once reduces reslicing artifacts]
        # [You could alternatively analyze all of the data, then Talairach transform the statistics (though this would make extraction of time series based on Talairached ROIs difficult)]
        # Visit for more info: http://afni.nimh.nih.gov/pub/dist/doc/program_help/align_epi_anat.py.html

        run_shell_cmd('align_epi_anat.py -overwrite -anat anat_mprage_skullstripped+orig -epi ' + conf.nextInputFilename[-1] + '+orig -epi_base 10 -epi2anat -anat_has_skull no -AddEdge -epi_strip 3dSkullStrip -ex_mode quiet -volreg on -deoblique on -tshift off -tlrc_apar anat_mprage_skullstripped+tlrc -master_tlrc ' +  conf.atlasEPI,logname)

        # Convert to NIFTI
        run_shell_cmd('3dcopy ' + conf.nextInputFilename[-1] + '_tlrc_al+tlrc ' + conf.nextInputFilename[-1] + '_tlrc_al.nii.gz',logname)
        run_shell_cmd('cp ' + conf.nextInputFilename[-1] + "_vr_motion.1D allruns_motion_params.1D",logname)





class checkMotionParams():

    def __init__(self, conf, showPlot=True):
        self.conf = conf
        self.showPlot = showPlot

    def run(self, conf):
        logname = conf.logname
        os.chdir(conf.subjfMRIDir)

        # Plotting motion parameters
        if self.showPlot == True:
            run_shell_cmd('1dplot -sep_scl -plabel ' + str(conf.subjID) + "Motion -volreg allruns_motion_params.1D'[0..5]'",logname)

        run_shell_cmd('echo "Mean, standard deviation, and absolute deviation of subject\'s motion in mm (left to right), by x,y,z direction (top to bottom):" > MotionInfo.txt',logname)
        run_shell_cmd("3dTstat -mean -stdev -absmax -prefix stdout: allruns_motion_params.1D'[0..2]'\\'" + " >> MotionInfo.txt",logname)
        run_shell_cmd('cat MotionInfo.txt',logname)





class timeSeriesExtraction():

    def __init__(self, conf):
        self.conf = conf

    def run(self, conf):

        logname = conf.logname
        os.chdir(conf.subjfMRIDir)

        print '--Extract time series from white matter, ventricle masks--'
        run_shell_cmd('3dmaskave -quiet -mask ' + conf.subjMaskDir + conf.subjID + '_wmMask_func_eroded.nii.gz ' + conf.nextInputFilename[-1] + '.nii.gz > ' + conf.subjID + '_WM_timeseries.1D',logname)
        run_shell_cmd('3dmaskave -quiet -mask ' + conf.subjMaskDir + conf.subjID + '_ventricles_func_eroded.nii.gz ' + conf.nextInputFilename[-1] + '.nii.gz > ' + conf.subjID + '_ventricles_timeseries.1D',logname)


        print '--Extract whole brain signal--'        
        os.chdir(conf.subjMaskDir)

        if conf.hcpData == False: # no need to run @auto_tlrc on hcpdata
            # Transform aseg to TLRC space
            run_shell_cmd('@auto_tlrc -apar ' + conf.subjfMRIDir + 'anat_mprage_skullstripped_tlrc.nii.gz -input ' + conf.subjID + '_fs_seg.nii.gz',logname)

        run_shell_cmd("3dcalc -overwrite -a " + conf.subjID + "_fs_seg.nii.gz -expr 'ispositive(a)' -prefix " + conf.subjID + '_wholebrainmask.nii.gz',logname)

        # Resample to functional space
        run_shell_cmd('3dresample -overwrite -master ' + conf.subjfMRIDir + conf.nextInputFilename[-1] + '.nii.gz -inset ' + conf.subjID + '_wholebrainmask.nii.gz -prefix ' + conf.subjID + '_wholebrainmask_func.nii.gz',logname)

        # Dilate mask by 1 functional voxel (just in case the resampled anatomical mask is off by a bit)
        run_shell_cmd("3dLocalstat -overwrite -nbhd 'SPHERE(-1)' -stat 'max' -prefix " + conf.subjID + '_wholebrainmask_func_dil1vox.nii.gz ' + conf.subjID + '_wholebrainmask_func.nii.gz',logname)

        os.chdir(conf.subjfMRIDir)
        run_shell_cmd('3dmaskave -quiet -mask ' + conf.subjMaskDir + conf.subjID + '_wholebrainmask_func_dil1vox.nii.gz ' + conf.nextInputFilename[-1] + '.nii.gz > ' + conf.subjID + '_wholebrainsignal_timeseries.1D',logname)



class runGLM():

    def __init(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append('NuissanceResid_' + conf.nextInputFilename[-1])

    def run(self, conf):    

        logname = conf.logname
        os.chdir(conf.subjfMRIDir)

        run_shell_cmd('cp Movement_Regressors_Rest_allruns.1D allruns_motion_params.1D', logname)

        run_shell_cmd('1d_tool.py -overwrite -infile ' + conf.subjID + '_WM_timeseries.1D -derivative -write ' + conf.subjID + '_WM_timeseries_deriv.1D', logname)
        run_shell_cmd('1d_tool.py -overwrite -infile ' + conf.subjID + '_ventricles_timeseries.1D -derivative -write ' + conf.subjID + '_ventricles_timeseries_deriv.1D', logname)
        run_shell_cmd('1d_tool.py -overwrite -infile ' + conf.subjID + '_wholebrainsignal_timeseries.1D -derivative -write ' + conf.subjID + '_wholebrainsignal_timeseries_deriv.1D', logname)

        print 'Run GLM to remove nuisance time series (motion, white matter, ventricles)'
        input = '-input ' + conf.nextInputFilename[-1] + '.nii.gz '
        mask = '-mask ' + conf.subjMaskDir + conf.subjID + '_gmMask_func_dil1vox.nii.gz '
        # concat = '-concat ' + '"' + conf.concatString + '" '
        concat = ''
        polort = '-polort 1 '
        num_stimts = '-num_stimts 12 '
        stimfile1 = '-stim_file 1 ' + conf.subjID + '_WM_timeseries.1D -stim_label 1 WM '
        stimfile2 = '-stim_file 2 ' + conf.subjID + '_ventricles_timeseries.1D -stim_label 2 Vent '
        stimfile3 = '-stim_file 3 ' + conf.subjID + '_WM_timeseries_deriv.1D -stim_label 3 WMDeriv '
        stimfile4 = '-stim_file 4 ' + conf.subjID + '_ventricles_timeseries_deriv.1D -stim_label 4 VentDeriv '
        stimfile5 = "-stim_file 5 allruns_motion_params.1D'[0]' -stim_base 5 "
        stimfile6 = "-stim_file 6 allruns_motion_params.1D'[1]' -stim_base 6 "
        stimfile7 = "-stim_file 7 allruns_motion_params.1D'[2]' -stim_base 7 "
        stimfile8 = "-stim_file 8 allruns_motion_params.1D'[3]' -stim_base 8 "
        stimfile9 = "-stim_file 9 allruns_motion_params.1D'[4]' -stim_base 9 "
        stimfile10 = "-stim_file 10 allruns_motion_params.1D'[5]' -stim_base 10 "
        # stimfile11 = "-stim_file 11 rest_allruns_motion_params.1D'[6]' -stim_base 11 "
        # stimfile12 = "-stim_file 12 rest_allruns_motion_params.1D'[7]' -stim_base 12 "
        # stimfile13 = "-stim_file 13 rest_allruns_motion_params.1D'[8]' -stim_base 13 "
        # stimfile14 = "-stim_file 14 rest_allruns_motion_params.1D'[9]' -stim_base 14 "
        # stimfile15 = "-stim_file 15 rest_allruns_motion_params.1D'[10]' -stim_base 15 "
        # stimfile16 = "-stim_file 16 rest_allruns_motion_params.1D'[11]' -stim_base 16 "
        stimfile11 = "-stim_file 11 " + conf.subjID + '_wholebrainsignal_timeseries.1D -stim_label 11 WholeBrain '
        stimfile12 = "-stim_file 12 " + conf.subjID + '_wholebrainsignal_timeseries_deriv.1D -stim_label 12 WholeBrainDeriv '
        xsave = '-xsave -x1D xmat_rall.x1D -xjpeg xmat_rall.jpg -errts NuissanceResid_Resids '
        jobs = '-jobs 1 -float -noFDR '
        bucket = '-bucket NuissanceResid_outbucket_' + conf.nextInputFilename[-1] + '+tlrc -overwrite' 

        glm_command = '3dDeconvolve ' + input + mask + concat + polort + num_stimts + stimfile1 + stimfile2 + stimfile3 + stimfile4 + stimfile5 + stimfile6 + stimfile7 + stimfile8 + stimfile9 + stimfile10 + stimfile11 + stimfile12 + xsave + jobs + bucket

        run_shell_cmd(glm_command, logname)

        run_shell_cmd('rm NuissanceResid_' + conf.nextInputFilename[-1] + '*', logname)
        run_shell_cmd('3dcopy NuissanceResid_Resids+tlrc NuissanceResid_' + conf.nextInputFilename[-1] + '+tlrc', logname)
        run_shell_cmd('rm NuissanceResid_Resids+tlrc', logname)



class spatialSmoothing():

    def __init__(self, conf):
        self.conf = conf
        self.conf.nextInputFilename.append('smInMask_' + conf.nextInputFilename[-1])

    def run(self, conf):
        logname = conf.logname
        os.chdir(conf.subjfMRIDir)

        print '-Spatially smooth data-'

        run_shell_cmd('3dBlurInMask -input ' + conf.nextInputFilename[-1] + '+tlrc -FWHM ' + str(conf.FWHMSmoothing) + ' -mask ' + conf.subjMaskDir + conf.subjID + '_gmMask_func_dil1vox.nii.gz -prefix smInMask_' + conf.nextInputFilename[-1] + '.nii.gz', logname)

    

