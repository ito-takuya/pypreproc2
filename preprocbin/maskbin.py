# Taku Ito
# 06/10/14
# An external module from pypreproc to create gray, white and ventricle masks.

# Import python software modules
import os
from run_shell_cmd import *

def create_gmMask(conf, logname):
	"""
	Creates a gmMask in subjMaskDir
	"""

	# Parse out important parameters for this block
	subj = conf.subjID 
	nextInputFilename = conf.nextInputFilename
	subjMaskDir = conf.subjMaskDir
	subjfMRIDir = conf.subjfMRIDir
	freesurferDir = conf.freesurferDir
	hcpdata = conf.hcpData 
	input = conf.fs_input

	os.chdir(subjMaskDir)

	print '---------------------'
	print 'Creating gray matter mask based on Freesurfer autosegmentation for subject ', subj

	print "Don't worry if the next three commands print out errors... if you are working with HCP-type data, they probably will result in errors"
	run_shell_cmd('cp ' + freesurferDir + '/mri/' + input + ' ./' + str(subj) + '_' + input,logname)
	run_shell_cmd('mri_convert -i ' + str(subj) + '_' + input + ' -ot nii ' + str(subj) + '_fs_seg.nii',logname)
	run_shell_cmd("3dcalc -overwrite -a " + str(subj) + "_fs_seg.nii -expr 'a' -prefix " + str(subj) + '_fs_seg.nii.gz',logname)

	run_shell_cmd('rm ' + str(subj) + '_fs_seg.nii ' + str(subj) + '_' + input,logname) #Delete both mgz and nii 
	print "Any error after this output should be noted and checked... there shouldn't be errors after this flag"


	if input == 'wmparc.nii.gz':
		# use wmparc maskval set 
		maskValSet="8 9 10 11 12 13 16 17 18 19 20 26 27 28 47 48 49 50 51 52 53 54 55 56 58 59 60 96 97 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032 2033 2034 2035"
		maskValSet = maskValSet.split(' ')
	else:
		# Using aseg (not aparc+aseg)
		maskValSet = [8, 9, 10, 11, 12, 13, 16,17, 18, 19, 20, 26,27, 28, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 96, 97, 3, 42]

	#Add segments to mask
	maskNum = 1
	for maskval in maskValSet:
	    if maskNum == 1:
	        run_shell_cmd('3dcalc -a ' + str(subj) + '_fs_seg.nii.gz -expr "equals(a,' + str(maskval) + ')" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	    else:
	        run_shell_cmd('3dcalc -a ' + str(subj) + '_fs_seg.nii.gz -b ' + str(subj) + 'mask_temp.nii.gz -expr "equals(a,' + str(maskval) + ')+b" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	    
	    maskNum += 1
	    
	# Make mask binary
	run_shell_cmd("3dcalc -a " + str(subj) + "mask_temp.nii.gz -expr 'ispositive(a)' -prefix " + str(subj) + '_gmMask.nii.gz -overwrite',logname)

	if hcpdata == 'False':
		# Transform to TLRC space
		# First convert files from NIfTI to AFNI
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_gmMask.nii.gz ' + subjMaskDir + str(subj) + '_gmMask', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_gmMask.nii.gz',logname)
		# Talairach command using AFNI functions
		run_shell_cmd('@auto_tlrc -apar ' + subjfMRIDir + 'anat_mprage_skullstripped+tlrc -input ' + str(subj) + '_gmMask+orig -overwrite',logname)
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_gmMask+tlrc -prefix ' + str(subj) + '_gmMask_func+tlrc',logname)		
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_gmMask+tlrc ' + subjMaskDir + str(subj) + '_gmMask.nii.gz', logname)
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_gmMask_func+tlrc ' + subjMaskDir + str(subj) + '_gmMask_func.nii.gz', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_gmMask+tlrc* ' + subjMaskDir + '_gmMask_func+tlrc*', logname)
	else:

		# Resample to functional space
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_gmMask.nii.gz -prefix ' + str(subj) + '_gmMask_func.nii.gz',logname)

	# Dilate mask by 1 functional voxel (just in case the resampled anatomical mask is off by a bit)
	run_shell_cmd("3dLocalstat -overwrite -nbhd 'SPHERE(-1)' -stat 'max' -prefix " + str(subj) + '_gmMask_func_dil1vox.nii.gz ' + str(subj) + '_gmMask_func.nii.gz',logname)

	run_shell_cmd('rm ' + str(subj) + 'mask_temp.nii.gz',logname)




def create_wmMask(conf, logname):
	"""
	Creates a wmMask in subjMaskDir
	"""
	# Parse out important parameters for this block
	subj = conf.subjID 
	nextInputFilename = conf.nextInputFilename
	subjMaskDir = conf.subjMaskDir
	subjfMRIDir = conf.subjfMRIDir
	freesurferDir = conf.freesurferDir
	hcpdata = conf.hcpData 
	input = conf.fs_input

	os.chdir(subjMaskDir)
    
	print '---------------------'
	print 'Create white matter mask, and erode it for subject', subj, '(MAKE SURE EROSIAN DOESN\'T REMOVE ALL VENTRICLE VOXELS)'
    
	run_shell_cmd('cp ' + freesurferDir + '/mri/' + input + ' ./' + str(subj) + '_' + input,logname)
	run_shell_cmd('mri_convert -i ' + str(subj) + '_' + input + ' -ot nii ' + str(subj) + '_fs_seg.nii',logname)
	run_shell_cmd("3dcalc -overwrite -a " + str(subj) + "_fs_seg.nii -expr 'a' -prefix " + str(subj) + "_fs_seg.nii.gz",logname)
	# Delete intermediary files
	run_shell_cmd('rm ' + str(subj) + '_fs_seg.nii ' + str(subj) + '_' + input + ' ' + str(subj) + 'mask_temp.nii.gz',logname)

	if input == 'wmparc.nii.gz':
		# use wmparc.nii.gz maskvals
		maskValSet="250 251 252 253 254 255 3000 3001 3002 3003 3004 3005 3006 3007 3008 3009 3010 3011 3012 3013 3014 3015 3016 3017 3018 3019 3020 3021 3022 3023 3024 3025 3026 3027 3028 3029 3030 3031 3032 3033 3034 3035 4000 4001 4002 4003 4004 4005 4006 4007 4008 4009 4010 4011 4012 4013 4014 4015 4016 4017 4018 4019 4020 4021 4022 4023 4024 4025 4026 4027 4028 4029 4030 4031 4032 4033 4034 4035 5001 5002"
		maskValSet = maskValSet.split(' ')
	else:
		# Using aseg (not aparc+aseg)
		# including all white matter
		maskValSet = [2, 7, 41, 46]

	# Add segments to mask
	maskNum = 1
	for maskval in maskValSet:
	    if maskNum == 1:
	        run_shell_cmd("3dcalc -a " + str(subj) + '_fs_seg.nii.gz -expr "equals(a,' + str(maskval) + ')" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	    else:
	        run_shell_cmd('3dcalc -a ' + str(subj) + '_fs_seg.nii.gz -b ' + str(subj) + 'mask_temp.nii.gz -expr "equals(a,' + str(maskval) + ')+b" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	        
	    
	    maskNum += 1
	    
	# Make mask binary
	run_shell_cmd("3dcalc -a " + str(subj) + "mask_temp.nii.gz -expr 'ispositive(a)' -prefix " + str(subj) + '_wmMask.nii.gz -overwrite',logname)

	# Transform to TLRC space
	if hcpdata == 'False':
		# Transform to TLRC space
		# First convert files from NIfTI to AFNI
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_wmMask.nii.gz ' + subjMaskDir + str(subj) + '_wmMask', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_wmMask.nii.gz',logname)
		# Talairach command using AFNI functions
		run_shell_cmd('@auto_tlrc -apar ' + subjfMRIDir + 'anat_mprage_skullstripped+tlrc -input ' + str(subj) + '_wmMask+orig -overwrite',logname)
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_wmMask+tlrc -prefix ' + str(subj) + '_wmMask_func+tlrc',logname)		
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_wmMask+tlrc ' + subjMaskDir + str(subj) + '_wmMask.nii.gz', logname)
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_wmMask_func+tlrc ' + subjMaskDir + str(subj) + '_wmMask_func.nii.gz', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_wmMask+tlrc* ' + subjMaskDir + '_wmMask_func+tlrc*', logname)
	else:

		# Resample to functional space
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_wmMask.nii.gz -prefix ' + str(subj) + '_wmMask_func.nii.gz',logname)

	# Subtract gray matter mask from white matter mask (avoiding negative #s)
	run_shell_cmd('3dcalc -a ' + str(subj) + '_wmMask_func.nii.gz -b ' + str(subj) + "_gmMask_func_dil1vox.nii.gz -expr 'step(a-b)' -prefix " + str(subj) + '_wmMask_func_eroded.nii.gz -overwrite',logname)
	run_shell_cmd('rm ' + str(subj) + 'mask_temp.nii.gz',logname)


def createVentricleMask(conf, logname):
	"""
	Creates ventricle masks in subjMaskDir
	"""

	# Parse out important parameters for this block
	subj = conf.subjID 
	nextInputFilename = conf.nextInputFilename
	subjMaskDir = conf.subjMaskDir
	subjfMRIDir = conf.subjfMRIDir
	freesurferDir = conf.freesurferDir
	hcpdata = conf.hcpData 
	input = conf.fs_input

	os.chdir(subjMaskDir)
        
	print '---------------------'
	print 'Create ventricle mask, and erode it for subject $subjNum (MAKE SURE EROSION DOESN\'T REMOVE ALL VENTRICLE VOXELS)'

	run_shell_cmd('cp ' + freesurferDir + '/mri/' + input + ' ./' + str(subj) + '_' + input,logname)
	run_shell_cmd('mri_convert -i ' + str(subj) + '_' + input + ' -ot nii ' + str(subj) + '_fs_seg.nii',logname)
	run_shell_cmd("3dcalc -overwrite -a " + str(subj) + "_fs_seg.nii -expr 'a' -prefix " + str(subj) + "_fs_seg.nii.gz",logname)
	# Delete intermediary files
	run_shell_cmd('rm ' + str(subj) + '_fs_seg.nii ' + str(subj) + '_' + input + ' ' + str(subj) + 'mask_temp.nii.gz',logname)

	# Using aseg (not aparc+aseg)
	# including ventricles
	maskValSet = [4, 43, 14, 15]
	# Add segments to mask
	maskNum = 1
	for maskval in maskValSet:
	    if maskNum == 1:
	        run_shell_cmd("3dcalc -a " + str(subj) + '_fs_seg.nii.gz -expr "equals(a,' + str(maskval) + ')" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	    else:
	        run_shell_cmd('3dcalc -a ' + str(subj) + '_fs_seg.nii.gz -b ' + str(subj) + 'mask_temp.nii.gz -expr "equals(a,' + str(maskval) + ')+b" -prefix ' + str(subj) + 'mask_temp.nii.gz -overwrite',logname)
	        
	    
	    maskNum += 1

	# Make mask binary
	run_shell_cmd("3dcalc -a " + str(subj) + "mask_temp.nii.gz -expr 'ispositive(a)' -prefix " + str(subj) + '_ventricles.nii.gz -overwrite',logname)

	# Transform to TLRC space
	if hcpdata == 'False':
		# Transform to TLRC space
		# First convert files from NIfTI to AFNI
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_ventricles.nii.gz ' + subjMaskDir + str(subj) + '_ventricles', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_ventricles.nii.gz',logname)
		# Talairach command using AFNI functions
		run_shell_cmd('@auto_tlrc -apar ' + subjfMRIDir + 'anat_mprage_skullstripped+tlrc -input ' + str(subj) + '_ventricles+orig -overwrite',logname)
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_ventricles+tlrc -prefix ' + str(subj) + '_ventricles_func+tlrc',logname)		
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_ventricles+tlrc ' + subjMaskDir + str(subj) + '_ventricles.nii.gz', logname)
		run_shell_cmd('3dcopy ' + subjMaskDir + str(subj) + '_ventricles_func+tlrc ' + subjMaskDir + str(subj) + '_ventricles_func.nii.gz', logname)
		run_shell_cmd('rm -v ' + subjMaskDir + str(subj) + '_ventricles+tlrc* ' + subjMaskDir + '_ventricles_func+tlrc*', logname)
	else:

		# Resample to functional space
		run_shell_cmd('3dresample -overwrite -master ' + subjfMRIDir + nextInputFilename + '.nii.gz -inset ' + str(subj) + '_ventricles.nii.gz -prefix ' + str(subj) + '_ventricles_func.nii.gz',logname)


	# Subtract gray matter mask from white matter mask (avoiding negative #s)
	run_shell_cmd('3dcalc -a ' + str(subj) + '_ventricles_func.nii.gz -b ' + str(subj) + "_gmMask_func_dil1vox.nii.gz -expr 'step(a-b)' -prefix " + str(subj) + '_ventricles_func_eroded.nii.gz -overwrite',logname)
	run_shell_cmd('rm ' + str(subj) + 'mask_temp.nii.gz',logname)            








