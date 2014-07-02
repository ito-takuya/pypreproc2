# Taku Ito
# Specific execute blocks, e.g., prepareMPRAGE, epiAlignment, etc.

sys.path.append('preprocbin')
from workflows import *
import os
import glob

def prepareMPRAGE(conf, logname):
	"""
	Input is each subject's subjConf, derived from general config
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






