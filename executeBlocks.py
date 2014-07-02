# Taku Ito
# Specific execute blocks, e.g., prepareMPRAGE, epiAlignment, etc.

sys.path.append('preprocbin')
from workflows import *
from run_shell_cmd import run_shell_cmd
import os
import glob

def prepareMPRAGE(conf, logname):
	"""
	DESCRIPTION: Prepares and compiles anatomical MRPRAGE from raw DICOM files.  Not for HCP data use.  For use on a single subject.
	PARAMETERS: 
		conf - a subjectConfig file
		logname - subject's log output filename
	"""
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
        print 'Conveting DICOM...'
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



def prepareEPI(conf, logname):
	"""
	DESCRIPTION: Converts fMRI data to AFNI format from raw DICOMs.
	PARAMETERS: 
		conf - a subjectConfig file
		logname - subject's log output filename
	"""
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
        if conf.numTRsToSkip > 0:
            run_shell_cmd('3dcalc -a epi_r' + str(runNum) + '+orig"[${numTRsToSkip}..$]" -expr ' + "'a' -prefix epi_r" + str(runNum) + ' -overwrite', logname)


