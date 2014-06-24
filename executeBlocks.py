# Taku Ito
# Specific execute blocks, e.g., prepareMPRAGE, epiAlignment, etc.

from workflows import *
import os

class prepareMPRAGE(ExecuteBlock):
	def __init__(self, conf, skullstrip=True):
		self.conf = conf
		self.dicomRenameDir = conf.rawDataDir + '/' + conf.t1_image + '/MR*'
		self.baseDir = self.conf.baseDir
		self.subjfMRIDir = self.conf.subjfMRIDir
		self.FSDir = self.conf.FSDir
		self.atlasDir = self.conf.atlasDir
		self.subjMaskDir = self.subjMaskDir
		# Need to know whether to skullstrip using FS or not
		self.skullstrip = skullstrip

		##### Need to edit! # *********************
		self.subj = self.conf.subj

	commands = []
	commands.append("os.chdir(" + self.subjfMRIDir + ")")
	commands.append("print 'Preparing MPRAGE file (anatomical image)'")
	commands.append("# Sort DICOM files (to make sure they will be read in the order they were collected in) using Freesurfer")
	commands.append("print 'Sorting DICOM...'")
	commands.append("dicom-rename " + self.dicomRenameDir + " --o " + self.baseDir + "SortedDICOMs/MPRAGE/MR")
	commands.append("# Convert DICOM files to NIFTI format using Freesurfer")
	commands.append("print 'Converting DICOM...'")
	commands.append("mri_convert " + self.baseDir + "SortedDICOMs/MPRAGE/*-00001.dcm --in_type siemens --out_type nii mprage.nii.gz")
	commands.append("# Remove sorted DICOMs")
	commands.append("rm -rf " + self.baseDir + "SortedDICOMs/MPRAGE")

	commands.append("# Skull strip MPRAGE")
	commands.append("# Use Freesurfer's skullstripping (very slow, but more accurate)")
	if self.skullstrip == True:
		commands.append("recon-all -subject " + str(self.subj) + " -all -sd " + self.FSDir + " -i mprage.nii.gz")
	else:
		commands.append("# recon-all -subject " + str(self.subj) + " -all -sd " + self.FSDir + " -i mprage.nii.gz")

	commands.append("# Convert to NIFTI")
	commands.append('mri_convert --in_type mgz --out_type nii ' + self.FSDir + '/mri/brain.mgz mprage_skullstripped.nii')
	commands.append('# gzip files and removed uncompressed file')
	commands.append('3dcopy mprage_skullstripped.nii mprage_skullstripped.nii.gz')
	commands.append('rm mprage_skullstripped.nii')
	commands.append('3dcopy mprage_skullstripped.nii.gz anat_mprage_skullstripped')
	commands.append('@auto_tlrc -base ' + self.atlasDir + '/MNI_avg152T1+tlrc -input anat_mprage_skullstripped+orig -no_ss')
	commands.append('ln -s ' + self.atlasDir + '/MNI_avg152T1+tlrc* .')
	commands.append("3dcalc -overwrite -a anat_mprage_skullstripped+tlrc -expr 'is positive(a)' -prefix " + self.subjMaskDir + "/wholebrain_mask+tlrc")
	commands.append('ln -s anat_mprage_skullstripped+tlrc* ' + self.subjMaskDir)

	



