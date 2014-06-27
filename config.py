# Taku Ito
# 05/30/2014
# Creates config file to get correct inputs for execution blocks

import os


class config():
	"""
	Creates a configuration object (that writes to a .conf file) containing all necessary data parameters.
	Each parameter has its own attribute, with the value of the attribute being the parameter.
	"""
	# initialize empty parameters
	def __init__(self, config=None):
		# Either initialize the config object's attributes to None, or input a config file and update/re-update this config object's attributes.
		if config==None:
			self.baseDir = None
			self.scriptsDir = None
			self.atlasDir = None
			self.AFNIDir = None
			self.FSDir = None
			self.numRuns = None
			self.numTRs = None
			self.TR_length = None
			self.smoothingParam = None
			self.tpattern = None
			self.listOfSubjs = None
			self.analysisName = None
			self.rawDataDir = None
			self.timingFiles = None
			self.t1_image = None
			self.epi_series = None
			self.name = None
		else:
			attr = parseTextFile(config)
			for key in attr:
				setattr(self, key, initial_data[key])



	def getBaseDir(self):
		string = raw_input('Give your base output directory: ')
		string = string.strip()
		self.baseDir = string

	def getScriptsDir(self):
		string = raw_input('Give the scripts directory [default: basedir/scripts/]: ')
		string = string if string else self.baseDir + '/scripts/'
		string = string.strip()
		self.scriptsDir = string

	def getAtlasDir(self):
		string = raw_input('Give the directory containing all atlases (anatomical and functional [default: /Applications/afni/]: ')
		string = string if string else '/Applications/afni/'
		string = string.strip()
		self.atlasDir = string

	def getAFNIdir(self):
		string = raw_input('Give the directory containing AFNI [default: /Applications/afni/afni]: ')
		string = string if string else '/Applications/afni/afni'
		string = string.strip()
		self.AFNIdir = string

	def getFS_loc(self):
		string = raw_input('Give the directory containing Freesurfer [default: /Applications/freesurfer/bin/freesurfer]: ')
		string = string if string else '/Applications/freesurfer/bin/freesurfer'
		string = string.strip()
		self.FSdir = string

	def getDataParams(self):
		numRuns = raw_input('How many runs per subject?: ')
		numRuns = int(numRuns.strip())
		self.numRuns = numRuns

		numTRs = raw_input('How many TRs per run?: ')
		numTRs = int(numTRs.strip())
		self.numTRs = numTRs

		TR_length = raw_input('How long is each TR (in seconds, just input number): ')
		TR_length = TR_length.strip()
		TR_length = TR_length + 's'
		self.TR_length = TR_length

		smoothingParam = raw_input('What should the smoothing parameter be (FWHM), in mm: ')
		smoothingParam = int(smoothingParam.strip())
		self.smoothingParam = smoothingParam

		tpattern = raw_input('Input the slice acquisition order. For Siemens Trio (standard EPI sequence), alt+z when you have an odd number of slices, alt+z2 when you have an even number of slices: ')
		tpattern = tpattern.strip()
		self.tpattern = tpattern

	def getSubjects(self):
		listOfSubjs = raw_input('Input the subject IDs, delimited by commas: ')
		listOfSubjs = listOfSubjs.strip()
		listOfSubjs = listOfSubjs.split(',')
		self.listOfSubjs = listOfSubjs

	def getAnalysisName(self):
		analysisName = raw_input('What is the name of this project called: ')
		analysisName = analysisName.strip()
		self.analysisName = analysisName

	def getRawDataDir(self):
		print 'Input the raw data for each subject:'
		print "Note, indicate subject number by '%subj'"
		print "For example, if you have subjects 401 and 402, and their raw data directory is: /projects/preprocessingDir/rawdata/401/, and /projects/preprocessingDir/rwadata/402/, you would indicate this by inputting '/projects/preprocessingDir/rawdata/%subj' "
		string = raw_input("Give the directory of the raw data for each subject: ")
		string = string.strip()
		string = string.split('%subj')
		# Note to self, when constructing a subject's raw data directory, remember that self.rawDataDir is a 2 element list
		self.rawDataDir = string

	def getTimingFiles(self):
		string = raw_input("If applicable, give the stimulus timing files. Note, all timing files for all subjects should be in the same directory. Enter nothing if not applicable: ")
		string = string.strip()
		self.timingFiles = string

	def rawDataParams(self):
		sampleSubj = self.listOfSubjs[0]
		sampleRawDataDir = self.rawDataDir[0] + sampleSubj + self.rawDataDir[1]
		rawDataContents = os.listdir(sampleRawDataDir)
		rawDataContents = dict(enumerate(rawDataContents))
		for key,value in zip(rawDataContents.keys(), rawDataContents.values()):
			print key, ':', value

		t1_image = raw_input('Indicate the directory (by the number to its left) which directory holds the T1, anatomical scan: ')
		t1_image = rawDataContents[int(t1_image)] #get the true value
		self.t1_image = t1_image

		epi_series = raw_input('Indicate the directories (by the number to its left), which directories holds the EPI/BOLD scans IN SEQUENTIAL ORDER.  The order you input them now is the order they will be concatenated as in the future preprocessing.  Separate the numbers by a "," and no spaces in between commas (e.g., "1,2,3,4)": ')
		epi_series = epi_series.strip()
		epi_series = epi_series.split(',')
		i=0
		for key in epi_series:
			key = int(key)
			epi_series[i] = rawDataContents[key]
			i += 1

		self.epi_series = epi_series # returns a list of all BOLD scan directory names 


	def generateConfFile(self):
		string = raw_input('Give the name of your configuration file: ')
		string = string if string else "default.conf"
		string = string if (len(string) > 5 and string[-5:] == ".conf") else string + ".conf"
	    # Make sure that file doesn't already exist
		if os.path.exists(string):
			print "File already exists."
			return
		else:
			self.name = string

	def write2Conf(self):
		newtext = open(self.name, 'w')
		for key,value in zip(self.__dict__.keys(), self.__dict__.values()):
			newtext.write(str(key) + ' = ' + str(value) + '\n')
		newtext.close()


	def run(self):
		# gather all inputs (run all methods)
		self.generateConfFile()
		self.getBaseDir()
		self.getScriptsDir()
		self.getAtlasDir()
		self.getAFNIdir()
		self.getFS_loc()
		self.getDataParams()
		self.getSubjects()
		self.getAnalysisName()
		self.getRawDataDir()
		self.getTimingFiles()
		self.rawDataParams()
		self.write2Conf()







# Helper functions:

# Ensure directory exists    
def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def parseTextFile(file):
	""""
	Parses a text file of parameters/variables separated by equal signs, and returns a string
	Intended for use of parsing *.conf files
	"""
	dic = {}
	with open(file) as f:
		for line in f:
			(key, val) = line.split('=')
			key = key.strip()
			val = val.strip()

			dic[key] = val

	return dic








