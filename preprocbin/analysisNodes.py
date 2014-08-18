# Module for analysis nodes, in particular, group analysis nodes.

import sys
sys.path.append('/projects/ColePreprocessingPipeline/docs/pypreproc2/preprocbin')
from run_shell_cmd import run_shell_cmd
import os
import glob
import maskbin
import re
import utils




class Group(object):
	"""
	DESCRIPTION: Super/parent class for all group analyses.  Essentially just updating conf so that all child classes have correct group directories
	"""
	def __init__(self, conf):
		self.conf = conf

		# Setting up group output directories
		groupDir = conf.basedir + 'group/'
		utils.ensureDir(groupDir)

    	# Group mask directory
		groupMaskDir = groupDir + 'masks/'
		utils.ensureDir(groupMaskDir)

		groupAnalysisDir = groupDir + conf.AnalysisName + 'Analysis/'
		utils.ensureDir(groupAnalysisDir)

		self.conf.groupDir = groupDir
		self.conf.groupMaskDir = groupMaskDir
		self.conf.groupAnalysisDir = groupAnalysisDir

class GroupANOVA2(Group):
    """
    DESCRIPTION: This object deals with running group ANOVAs, in particular for activation studies.

    """
    def __init__(self, sconfs):
        # Input sconfs is an array of all subject confs

        # Get single subject conf for generic parameters
        conf = sconfs[0]
        super(GroupANOVA2, self).__init__(conf)
        self.conf.nextInputFilename.append('GroupANOVA2')
        # Get array of all subjects
        self.sconfs = sconfs


    def run(self):
    	# Make a local variable
        sconfs = self.sconfs
    	conf = self.conf
    	logname = conf.logname
        ANOVA = conf.ANOVA
        numSubjs = len(sconfs) if ANOVA['blevels'] == None else ANOVA['blevels']

    	print '===Starting group analysis==='

    	# Link anatomical files to analysis directory for visualization
    	run_shell_cmd('cp ' + conf.atlasAnat + ' ' + conf.groupAnalysisDir, logname) 

    	# Run ANOVA
    	print '--ANOVA: '
    	os.chdir(conf.groupAnalysisDir)
        
        # set parameters for 3dANOVA2 command
        options = '-DAFNI_FLOATIZE=YES -type ' + str(ANOVA['type']) + ' -alevels ' + str(ANOVA['alevels']) + ' -blevels ' + str(numSubjs) + ' '
        # instantiate number of dsets
        dsets = []
        subbricks = ANOVA['conditions'].values()
        condname = ANOVA['conditions'].keys()
        for condNum in range(1,ANOVA['alevels']+1):
            for subj in range(1,numSubjs+1): 
                dsets.append('-dset ' + str(condNum) + ' ' + str(subj) + ' ' + sconfs[subj-1].subjfMRIDir + conf.nextInputFilename[-2] + "+tlrc'[" + str(subbricks[condNum-1]) + "]' ")
        fa = '-fa ALevel_MainEffect '
        
        amean = ''
        for condNum in range(1,ANOVA['alevels']+1):
            amean += '-amean ' + str(condNum) + ' ' + condname[condNum-1] + 'Mean '

        adiff = ''
        for condNum1 in range(1,ANOVA['alevels']+1):
            for condNum2 in range(1,ANOVA['alevels']+1):
                if condNum1 != condNum2 and condNum1 < condNum2:
                    adiff += '-adiff ' + str(condNum1) + ' ' + str(condNum2) + ' diff' + condname[condNum1-1] + 'Meanvs' + condname[condNum2-1] + 'Mean '
        
        bucket = '-bucket ' 
        for condNum in range(len(condname)):
            bucket += condname[condNum] + '_'
        bucket += 'subjN' + str(numSubjs)

        dsetstring = ''
        for dset in dsets:
            dsetstring += dset
        
        # Compile ANOVA command
        anova_command = '3dANOVA2 ' + options + dsetstring + fa + amean + adiff + bucket
        # Print ANOVA command to console
        print 'ANOVA command: ', anova_command

        run_shell_cmd(anova_command, logname)


    	