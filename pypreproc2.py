#!/usr/bin/env python

# Taku Ito
# 07/03/2014

# PyPreproc Modular Version 1.0
# Implements a more modular approach in hopes of simplifying and re-using code, and also to make certain pipelines more configurable based on the type of data.
# Requires to use of a config file, (*.conf) to set all pipeline parameters.

import sys
sys.path.append('preprocbin')
from run_shell_cmd import run_shell_cmd
import os
import glob
import maskbin
import config
import utils
import preprocNodes as ppnodes
from multiprocessing import Pool
from tempfile import mkstemp
from shutil import move
from os import remove, close


# Creating a list of subject config files (an iterable to be input)
def createSubjConfs(conf):
	"""
	DESCRIPTION: Takes the config object constructed from the YAML file, and creates an array of subject config objects to be returned
	PARAMETERS:
		conf - the config object (parsed from the YAML file) 
	"""
	sconfs = [] 
	subjCount = 0
	for subj in conf.listOfSubjects:
		sconfs.append(config.SubjConfig(conf,subj))
		utils.ensureSubjDirsExist(sconfs[subjCount])
		utils.createLogFile(sconfs[subjCount])
		subjCount += 1
	return sconfs

class Pipeline():
	"""
	DESCRIPTION: PyPreproc2 Pipeline object for single subjects
	PARAMETERS:
		sconf - array of all subject config objects.
	"""

	def __init__(self,sconf):
		# sconf is a single subject's config object
		self.sconf = sconf

		# Just get out the first subject's nodes, since they sould be the same for all nodes.
		# self.nodes is a key:value pairing for numbering of nodes and nodes to execute
		self.nodes = sconfs.Nodes 

	def run(self):
		# Run the pipeline given the order

		# make sconf a local variable
		sconf = self.sconf

		for node in range(len(self.nodes)):
			# Get constructor for particular node
			callNode = getattr(ppnodes, self.nodes[node])
			# Instantiate object using callNode()
			nodeObject = callNode(sconf)
			# Now, run only nodes indicated in 'runNodes'
			if node in self.sconf.runNodes:
				node.run()

			# Keep track of sconfs in pipeline, regardless of whether or not a node was run.
			sconf = nodeObject.conf.nextInputFilename

		return sconf

def runPipeline(sconf):
	"""
	Helper method to run the pipeline, so can be funneled in to multiprocessing module
	"""
	pipe = Pipeline(sconf)
	pipe.run()

def runParallel(conf):
	"""
	Helper function to run processes in parallel, given nproc parameter in the YAML file
	"""
	sconfs = createSubjConfs(conf)
	pool = Pool(processes=conf.nproc)
	sconfs = pool.map_async(runPipeline, sconfs).get(9999999)
	return sconfs


###################
"""
MAIN METHOD: method will the below commands as an executable
"""
def main(): 

	defaultConfig = '/projects/IndivRITL/docs/scripts/pypreproc/pilotPreproc.yaml'
	# Ask for input path
	configfile = raw_input('Give the full path of your configuration file (with a .yaml extension).  [Default: ' + defaultConfig + ']: ')
	# Set default, if nothing is given
	configfile = '/projects/IndivRITL/docs/scripts/pypreproc/pilotPreproc.yaml' if configfile == '' else configfile


	# Creates new conf file
	conf = config.Config(configfile)

	runParallel(conf)


	
if __name__ == "__main__":
	main()



# sconfs = runParallel(conf,sconfs)
# updateYAML(conf, sconfs, configfile)

