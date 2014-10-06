#!/usr/bin/env python

# Taku Ito
# 07/03/2014

# PyPreproc Modular Version 1.0
# Implements a more modular approach in hopes of simplifying and re-using code, and also to make certain pipelines more configurable based on the type of data.
# Requires to use of a config file, (*.conf) to set all pipeline parameters.

import sys
sys.path.append('/projects/ColePreprocessingPipeline/docs/pypreproc2/preprocbin')
from run_shell_cmd import run_shell_cmd
import os
import glob
import maskbin
import config
import utils
import preprocNodes as ppnodes
import analysisNodes as anodes
from multiprocessing import Pool
from tempfile import mkstemp
from shutil import move
from os import remove, close


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
		self.nodes = sconf.Nodes 

	def run(self):
		# Run the pipeline given the order

		# make sconf a local variable
		sconf = self.sconf

		for nodeNum in self.nodes:
			# Get constructor for particular node
			print 'Constructing node for', self.nodes[nodeNum], '...'
			# Make sure the class being instantiated is looking in the correct module
			if isinstance(self.nodes[nodeNum], str):
				if hasattr(ppnodes, self.nodes[nodeNum]):
					callNode = getattr(ppnodes, self.nodes[nodeNum])
					# Instantiate object using callNode()
					nodeObject = callNode(sconf)
				elif hasattr(maskbin, self.nodes[nodeNum]):
					callNode = getattr(maskbin, self.nodes[nodeNum])
					# Instantiate object using callNode()
					nodeObject = callNode(sconf)
			elif isinstance(self.nodes[nodeNum],dict):
				print "Reading in a custom command... Make sure you know what you're doing!"
				# Constructing custom command and instantiating it
				nodeObject = ppnodes.CustomCmd(self.nodes[nodeNum],sconf)
			else:
				raise Exception('Cant find the node', self.nodes[nodeNum], 'in any of the available modules. Please make sure you typed the correct node name.')

			# Now, run only nodes indicated in 'runNodes'
			print nodeObject.conf.nextInputFilename
			if nodeNum in self.sconf.runNodes:
				nodeObject.run()

			# Keep track of sconfs in pipeline, regardless of whether or not a node was run.
			print 'Updating config object...'
			sconf = nodeObject.conf

		return sconf


def runPipeline(sconf):
	"""
	Helper method to run the pipeline, so can be funneled in to multiprocessing module
	"""
	pipe = Pipeline(sconf)
	sconf = pipe.run()
	return sconf

def runParallel(conf):
	"""
	Helper function to run processes in parallel, given nproc parameter in the YAML file
	"""
	sconfs = utils.createSubjConfs(conf)
	pool = Pool(processes=conf.nproc)
	sconfs = pool.map_async(runPipeline, sconfs).get(9999999)
	return sconfs


###################
"""
MAIN METHOD: method will the below commands as an executable
"""
def main(): 

	defaultConfig = '/Volumes/Drobot/scratchdisk/taku_pypreproc2/scripts/preprocTutorial.yaml'
	# Ask for input path
	configfile = raw_input('Give the full path of your configuration file (with a .yaml extension).  [Default: ' + defaultConfig + ']: ')
	# Set default, if nothing is given
	configfile = '/projects/ColePreprocessingPipeline/docs/taku_dev/pypreproc2/preprocTutorial.yaml' if configfile == '' else configfile


	# Creates new config object

	conf = config.Config(configfile)

	# This command runs all single-subject processing
	sconfs = runParallel(conf)

	if sconfs[0].ANOVA['addNode'] == True:
		anova = anodes.GroupANOVA2(sconfs)
		anova.run()
		return sconfs, anova
	else:
		return sconfs

	
if __name__ == "__main__":
	main()



# sconfs = runParallel(conf,sconfs)
# updateYAML(conf, sconfs, configfile)

