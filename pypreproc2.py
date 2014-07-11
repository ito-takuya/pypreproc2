#!/usr/bin/env python

# Taku Ito
# 07/03/2014

# PyPreproc Modular Version 1.0
# Implements a more modular approach in hopes of simplifying and re-using code, and also to make certain pipelines more configurable based on the type of data.
# Requires to use of a config file, (*.conf) to set all pipeline parameters.

import sys
sys.path.append('preprocbin')
from workflows import *
from run_shell_cmd import run_shell_cmd
import os
import glob
import maskbin
import config
import utils
import executeBlocks as block
from multiprocessing import Pool
from tempfile import mkstemp
from shutil import move
from os import remove, close

configfile = '/projects/IndivRITL/docs/scripts/pypreproc/test.yaml'

# configfile = raw_input('Give the full path of your configuration file (with a .yaml extension): ')

# Creates new conf file
conf = config.Config(configfile)

# Creating a list of subject config files (an iterable to be input)
sconfs = [] 
subjCount = 0
for subj in conf.listOfSubjects:
	sconfs.append(config.SubjConfig(conf,subj))
	utils.ensureSubjDirsExist(sconfs[subjCount])
	utils.createLogFile(sconfs[subjCount])
	subjCount += 1

def pipeline(sconf):
	sconf = block.prepareMPRAGE(sconf)
	sconf = block.prepareEPI(sconf)
	# sconf = block.concatenateRuns(sconf, sconf.logname)
	sconf.nextInputFilename[-1] = 'epi_r1'
	sconf = block.talairachAlignment(sconf)
	sconf = block.checkMotionParams(sconf)
	sconf = maskbin.create_gmMask(sconf)
	sconf = maskbin.create_wmMask(sconf)
	sconf = maskbin.createVentricleMask(sconf)
	sconf = block.timeSeriesExtraction(sconf)
	sconf = block.runGLM(sconf)
	sconf = block.spatialSmoothing(sconf)

	return sconf

def runParallel(conf, sconfs):
	pool = Pool(processes=conf.nproc)
	sconfs = pool.map_async(pipeline, sconfs).get(9999999)
	return sconfs

def updateYAML(conf, sconfs, configfile):
	# This is kind of an ugly hack to have nextInputFilename updated... not ideal. 
	print 'updating yaml file...'
	conf.nextInputFilename = sconfs[0].nextInputFilename

	# Deleting old YAML, creating a new (temporary) one with updated parameters (just nextInputFilename)
	# create temporary file
	fh, abs_path = mkstemp()
	newyaml = open(abs_path, 'w')
	oldyaml = open(configfile)
	for line in oldyaml:
		if line.startswith('nextInputFilename'):
			newyaml.write('nextInputFilename : ' + str(conf.nextInputFilename) + '\n')
		else: 
			newyaml.write(line)
	# close temp file
	newyaml.close()
	close(fh)
	oldyaml.close()
	# remove original yaml file
	remove(configfile)
	# rename temp file to original yaml file's name
	move(abs_path, configfile)


# sconfs = runParallel(conf,sconfs)
# updateYAML(conf, sconfs, configfile)





