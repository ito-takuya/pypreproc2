#!/usr/bin/env python

# Taku Ito
# 07/03/2014

import os

# util functions:





def ensureDir(f):
	"""
	Ensure directory exists. This is a helper function to 'ensureSubjDirsExist'    
	"""
	d = os.path.dirname(f)
	if not os.path.exists(d):
	    os.makedirs(d)


def ensureSubjDirsExist(conf):
	"""
	This function ensures that subject directories are created, if they don't exist
	"""
	ensureDir(conf.subjDir)
	ensureDir(conf.subjfMRIDir)
	ensureDir(conf.subjMaskDir)
	ensureDir(conf.subjAnalysisDir)
	ensureDir(conf.freesurferDir)



def createLogFile(conf):
	"""
	Creates a log file for each individual subject, and places the log file within each subject's subjDir
	"""
	subj = conf.subjID
	# Output Log file
	# Default get time and date:
	from datetime import datetime
	i = str(datetime.now())
	time = datetime.now()
	datestr = str(time.month) + '-' + str(time.day) + '-' + str(time.year) + '_' + str(time.hour) + ':' + str(time.minute)

	if conf.logname == None:
		logname = conf.subjDir + 'pypreproc_' + datestr + '.log'
		print '-----------Outputting log for subj', subj, 'in subjDir-----------'
		print 'The log for subject', subj, 'will be located in output in', logname 
		print 'View the output to ensure that data processing was performed smoothly!'
		print 'This processing stream runs the following steps:'
		newtext = open(logname, 'a')
		newtext.write('This processing stream runs the fllowing steps: \n')
		if conf.prepareData == True:
		    print 'Data preparation'
		    newtext.write('MPRAGE preparation \n')
		if conf.prepareEPI == True:
		    print 'EPI preparation'
		    newtext.write('EPI preparation \n')
		if conf.sliceTimeCorrection == True:
		    print 'Slice time correction'
		    newtext.write('Slice time correction \n')
		if conf.concatenateRuns == True:
		    print 'Run concatenation'
		    newtext.write('Run concatenation \n')
		if conf.talairachAlignment == True:
		    print 'Talairach alignment'
		    newtext.write('Talairach alignment \n')
		if conf.checkMotionParams == True:
		    print 'Motion parameter check'
		    newtext.write('Motion parameter check \n')
		if conf.createGMMask == True:
		    print 'Gray matter mask creation'
		    newtext.write('Gray matter mask creation \n')
		if conf.createWMMask == True:
		    print 'White matter mask creation'
		    newtext.write('White matter mask creation \n')
		if conf.createVentricleMask == True:
		    print 'Ventricle mask creation'
		    newtext.write('Ventricle mask creation \n')
		if conf.timeSeriesExtraction == True:
		    print 'Timeseries extraction'
		    newtext.write('Timeseries extraction \n')
		if conf.spatialSmoothing == True:
		    print 'Spatial smoothing'
		    newtext.write('Spatial smoothing \n')
		if conf.runGLM == True:
		    print 'Single subject GLMs'
		    newtext.write('Single subject GLMs \n')
		newtext.close()

		conf.logname = logname # update conf object
		
	return conf


### OUTDATED AS OF 07/15/2014
# def updateYAML(conf, sconfs, configfile):
# 	"""
# 	This is kind of an ugly hack to have nextInputFilename updated... not ideal. 
# 	"""
# 	print 'updating yaml file...'
# 	conf.nextInputFilename = sconfs[0].nextInputFilename

# 	# Deleting old YAML, creating a new (temporary) one with updated parameters (just nextInputFilename)
# 	# create temporary file
# 	fh, abs_path = mkstemp()
# 	newyaml = open(abs_path, 'w')
# 	oldyaml = open(configfile)
# 	for line in oldyaml:
# 		if line.startswith('nextInputFilename'):
# 			newyaml.write('nextInputFilename : ' + str(conf.nextInputFilename) + '\n')
# 		else: 
# 			newyaml.write(line)
# 	# close temp file
# 	newyaml.close()
# 	close(fh)
# 	oldyaml.close()
# 	# remove original yaml file
# 	remove(configfile)
# 	# rename temp file to original yaml file's name
# 	move(abs_path, configfile)