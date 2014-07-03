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

configfile = '/projects/IndivRITL/docs/scripts/pypreproc/pilotPreproc.conf'

# Creates new conf file
conf = config.config(configfile)
sconf = config.subjConfig(conf,'001t')
sconf = utils.createLogFile(sconf[0])
sconf = block.prepareMPRAGE(sconf, sconf.logname)
sconf = block.prepareEPI(sconf, sconf.logname)
sconf = block.concatenateRuns(sconf, sconf.logname)
sconf = block.talairachAlignment(sconf, sconf.logname)
sconf = block.checkMotionParams(sconf, sconf.logname)





# create an array of sconfs for all subjects
sconfs_list = []
for subj in conf.listOfSubjects:
	sconfs_list.append(config.subjConfig(conf,subj))


