#Taku Ito
#05/19/2014
#Main objects for pypreproc
from run_shell_cmd import run_shell_cmd
import os

#***********************  SKIP  ***********************#
# Helper functions:

# Ensure directory exists    
def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
#********************************************************#

#**********************  PARAMETERS SECTION  **********************#
### EDIT AS NECESSARY

#### Execute Controls:
# If you wish to execute the following commands, enter them as 'True'.  
# If you do not wish to execute a particular perprocessing command, enter them as 'False'
# You may NOT leave them blank, otherwise the script will fail in error.
prepareMPRAGE = False                # prepares the anatomical MPRAGE image; also runs freesurfer unless specificed otherwise (see line 41)
prepareEPI = False                   # prepares the functional EPI images
sliceTimeCorrection = False          # runs slice time correction on the epi images. Make sure you know what the acquisition pattern is for this command!
concatenateRuns = False              # concatenates all the functional runs into a single run      
epiAlignment = False                 # aligns the functional, epi images to a template (MNI_EPI template)
checkMotionParams = False            # checks the motion parameters
createGMMask = True                 # creates a gray matter mask using Freesurfer output
createWMMask = False                 # creates a white matter mask using Freesurfer output
createVentricleMask = False          # creates a ventricle mask using Freesurfer output
timeseriesExtraction = False         # extracts the time series using the gray, white, and ventricle masks
spatialSmoothing = False             # smooths the epi/functional images according to the FWHMSmoothing paramater (see line 53)
afni2nifti = False                   # converts final output from AFNI to NIfTI format
# normalizeSignal = False             # normalizes signal; this functionality is not yet available in this version!
#Default False
# skipFreesurfer = True              # if 'True', will skip Freesurfer's 'recon-all' command in the 'prepareMPRAGE' execution block


# Main parameter set up
listOfSubjects = ['401']                # indicate the subject directories in single quotations
runsPerSubj = 10                      # indicate the number of runs per subject
basedir = '/Volumes/Drobot/scratchdisk/taku_output/' # indicate the base directory (should be your base output directory)
scriptsDir = basedir + '/scripts/'               # make sure this correctly points to your scripts directory
atlasDir = '/Applications/afni/'                 # if you're using the Cole Lab Server, you don't need to change this.
AFNI_loc = '/Applications/afni/afni'             # if you're using the Cole Lab Server, you don't need to change this.   
FS_loc = '/Applications/freesurfer/bin/freesurfer' # if you're using the Cole Lab Server, you don't need to change this.
TR = '1s'                             # indicate the TR in seconds for the scan
numTRs = 528                          # indicate the number of TRs per run
FWHMSmoothing = 6                     # indicate the smoothing parameter you want.  6mm is defaulted.
ANALYSISNAME = 'AFNItutorial'       # what is the analysis name of this project?
#Select the slice acquisition order. For Siemens TRIO (standard EPI sequence): alt+z when you have an odd number of slices, alt+z2 when you have an even number of slices
tpattern='alt+z'                


class Command():
    """
    The building block of this framework.  
    This object interfaces with the command line and runs it's input to the terminal.
    """
    def __init__(self, input=None, output=None, logname=None, pwd=None):
        self.input = input
        self.output = output
        self.logname = logname
        self.pwd = pwd

    def input(self, input):
        self.input = input
        return self.input

    def output(self, output):
        self.output
        return self.output

    def changeLogname(self, logname):
        self.logname = logname
        return self.logname

    def run(self):
        print 'Running:', self.input
        run_shell_cmd(self.input, self.logname, cwd=self.pwd)


class ExecuteBlock():
    """
    Abstract class for all execution blocks.
    """
    def __init__(self, commands = [], comments = [], config = {}):
        self.commands = commands
        # self.name = name #name of the execute block (e.g., Preparing MPRAGES)
        self.comments = comments
        self.config = config #configuration parameters for the execute block

    def showCommands(self):
        commands = {}
        for num in range(len(self.commands)):
            commands[num] =  self.commands[num].input
        return commands

    def addCommand(self, command):
        self.commands.extend(command)
        return self.commands

    def delCommand(self, commandIndex):
        del self.commands[commandIndex]
        return self.commands

    def run(self):
        for command in self.commands:
            command.run()


class Pipeline():
    
    """
    Abstract representation for all pipelines
    """
    def __init__(self, blocks=[], name=None):
        self.blocks = blocks #list of blocks
        self.name = name #string

    def addBlock(self, block):
        self.blocks.extend(block)
        return self.blocks

    def delBlock(self, blockIndex):
        del self.blocks[blockIndex]
        return self.blocks

    def run(self):
        for block in self.blocks:
            block.run()





