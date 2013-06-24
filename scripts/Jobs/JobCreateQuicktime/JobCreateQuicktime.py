from System.IO import *
from System.Text import *

from Deadline.Scripting import *

########################################################################
## Globals
########################################################################
scriptDialog = None
settings = None

########################################################################
## Main Function Called By Deadline
########################################################################

def __main__():
	global scriptDialog
	global settings
	
	dialogWidth = 250
	dialogHeight = 200
	labelWidth = 100
	tabHeight = 600
	padding = 12
	popupWidth = dialogWidth-labelWidth-padding
	fullWidth = dialogWidth-labelWidth-padding
	
	scriptDialog = DeadlineScriptEngine.GetScriptDialog()
	
	scriptDialog.SetSize( dialogWidth+padding, dialogHeight )
	scriptDialog.SetTitle( 'Create Quicktime' )
	
	# Start Settings Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Quicktime Settings', False )
	# FPS Range Slider
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'FPSLabel', 'LabelControl', 'FPS', labelWidth, -1 )
	scriptDialog.AddRangeControl ( 'FPSRangeBox', 'RangeControl', 30, 1, 60, 0, 1, fullWidth, -1 )
	scriptDialog.EndRow()
	'''
	# FPS Range Popup
	fps = ('25', '30', '50', '60')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'ResolutionLabel', 'LabelControl', 'Resolution', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'FPSRangeBox' , 'ComboControl', fps[1], fps, popupWidth, -1 )
	scriptDialog.EndRow()
	'''
	# Resolution Popup
	resolutions = ('Full Resolution', 'Half Resolution', 'Third Resolution', 'Quarter Resolution')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'ResolutionLabel', 'LabelControl', 'Resolution', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'ResolutionComboBox' , 'ComboControl', resolutions[1], resolutions, popupWidth, -1 )
	scriptDialog.EndRow()
	# Codec Popup
	codecs = ('Animation','H.264','ProRes 422')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'CodecLabel', 'LabelControl', 'Codec', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'CodecComboBox' , 'ComboControl', codecs[2], codecs, popupWidth, -1 )
	scriptDialog.EndRow()
	# Bitrate Range
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'BitRateLabel', 'LabelControl', 'H.264 Bit Rate', labelWidth, -1 )
	scriptDialog.AddRangeControl ( 'BitRateRangeBox', 'RangeControl', 8000, 1000, 20000, 0, 1000, fullWidth, -1 )
	scriptDialog.EndRow()
	# Slate Checkbox
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'DummyLabel', 'LabelControl', '', labelWidth, -1 )
	scriptDialog.AddSelectionControl( 'CheckBox', 'CheckBoxControl', False, 'Show slate and frames', fullWidth, -1 )
	scriptDialog.EndRow()
	# End Settings group
	scriptDialog.EndGroupBox( False )
	# Submit and Cancel buttons
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'DummyLabel1', 'LabelControl', '', dialogWidth-232,-1 )
	cancelButton = scriptDialog.AddControl( 'CancelButton', 'ButtonControl', 'Cancel', 100, -1 )
	cancelButton.ValueModified += CancelButtonPressed
	submitButton = scriptDialog.AddControl( 'SubmitButton', 'ButtonControl', 'Submit', 100, -1)
	submitButton.ValueModified += SubmitButtonPressed
	scriptDialog.EndRow()
	
	scriptDialog.ShowDialog( False )


########################################################################
## Helper Functions
########################################################################

def CancelButtonPressed( *args ):
	CloseDialog()


def SubmitButtonPressed( *args ):
	global scriptDialog
	
	# Get list of jobs
	jobs = JobUtils.GetSelectedJobs()
	numJobs = len( jobs )
	
	# Get Data from Dialog Box
	codec = str( scriptDialog.GetValue( 'CodecComboBox' ) )
	bitRate = int( scriptDialog.GetValue( 'BitRateRangeBox' ) )
	frameRate = int( scriptDialog.GetValue( 'FPSRangeBox' ) )
	resolution = str( scriptDialog.GetValue( 'ResolutionComboBox' ) )
	scaleAmount = 1.0
	
	# Get Scale Res
	if resolution=='Half Resolution':
		scaleAmount = 0.5
	elif resolution=='Third Resolution':
		scaleAmount = 0.33
	elif resolution=='Quarter Resolution':
		scaleAmount = 0.25
		
	# Change codec
	# codecs = ('Animation','H.264','ProRes 422')

	if codec == 'Animation':
		codec = 'rle '
	elif codec == 'H.264':
		codec = 'avc1'
	else:
		codec = 'apcn' #ProRes 422

	tempFile = GetTempDirectory()+'/scriptingTemp.txt'
	tempFileHandle = open( tempFile, 'w' )
	# Debugging
	'''
	tempFileHandle.write ( str(codec)+'\n' )
	tempFileHandle.write ( str(bitRate)+'\n' )
	tempFileHandle.write ( str(frameRate)+'\n' )
	tempFileHandle.write ( str(resolution)+'\n' )
	tempFileHandle.write ( str(scaleAmount)+'\n' )
	tempFileHandle.write ( '\n' )
	'''

	# Iterate through selected jobs
	for i in range( 0, numJobs ):
		job = jobs [i]
		outputDirectories = job.JobOutputDirectories
		outputFilenames = job.JobOutputFileNames
		
		# Iterate thrugh renders in job
		for j in range ( 0, len (outputDirectories) ):
			# Get and Set Working Paths
			outputDirectory = outputDirectories[j]
			outputFilename = outputFilenames[j]
			outputPath = Path.Combine(outputDirectory,outputFilename).replace("//","/")
			
			pluginDirectory = RepositoryUtils.GetScriptsDirectory() + '/Jobs/JobCreateQuicktime'
			templateNukeScript = pluginDirectory + '/JobCreateQuicktimeNukeTemplate.nk'

			currentUserHomeDirectory = ClientUtils.GetCurrentUserHomeDirectory()
			currentUserTempDirectory = currentUserHomeDirectory + '/temp'
			submissionNukeScript = currentUserTempDirectory + '/JobCreateQuicktimeNukeSubmissionScript.nk'
			
			# Get some information about the job
			sceneFile = JobUtils.GetDataFilename( i )
			firstFrame = JobUtils.GetFirstFrame( i )
			lastFrame = JobUtils.GetLastFrame( i )
			sequencePath = JobUtils.GetOutputFilename( i , 0 )
			comment = JobUtils.GetCurrentJobValue ( i , 'comment' )
			user = JobUtils.GetCurrentJobValue ( i , 'user' )
			
			# Create Nuke Script for submission
			nukeInputSequence = outputPath
			nukePath = '/Applications/Nuke6.3v4/Nuke6.3v4.app/Contents/MacOS/Nuke6.3v4'
			nukePythonScript = pluginDirectory + '/ModifyNukeTemplate.py'
			nukeArgList = [ '-t', nukePythonScript, templateNukeScript , submissionNukeScript , nukeInputSequence , outputPath ]
			for k in range ( 1, len (nukeArgList) ):
				nukeArgList[k] = '\"' + nukeArgList[k] + '\"'
			nukeArgList.extend( [ str(firstFrame) , str(lastFrame) , str(scaleAmount) , str(frameRate) , codec, ] )
			nukeArgs = ' '.join( nukeArgList )
			nukeProcess = ProcessUtils.SpawnProcess ( nukePath , nukeArgs, currentUserTempDirectory )
			if not ProcessUtils.WaitForExit ( nukeProcess, 10000 ) # Wait up to ten seconds for script to be made
				return #nuke failed

			# Debugging
			'''
			tempFileHandle.write ( str(job.JobName)+'\n' )
			tempFileHandle.write ( str(job.JobPriority)+'\n' )
			tempFileHandle.write ( str(sceneFile)+'\n' )
			tempFileHandle.write ( str(firstFrame)+'\n' )
			tempFileHandle.write ( str(lastFrame)+'\n' )
			tempFileHandle.write ( str(outputDirectory)+'\n' )
			tempFileHandle.write ( str(outputFilename)+'\n' )
			tempFileHandle.write ( str(outputPath)+'\n' )
			tempFileHandle.write ( str(job.JobComment)+'\n' )
			tempFileHandle.write ( str(job.JobUserName)+'\n' )
			tempFileHandle.write ( str(templateNukeScript)+'\n' )
			tempFileHandle.write ( str(submissionNukeScript)+'\n' )			
			tempFileHandle.write ( str(nukePath+' '+nukePythonScript+' '+nukeArgs)+'\n' )			
			tempFileHandle.write ( '\n' )
			
			''''
		
	tempFileHandle.close()
	CloseDialog()


def CloseDialog():
	global scriptDialog
	
	scriptDialog.CloseDialog()
	

	