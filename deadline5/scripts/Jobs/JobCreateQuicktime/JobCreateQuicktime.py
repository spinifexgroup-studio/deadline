'''
Create a quicktime from deadline monitor - uses nuke to do the job
TODO:
- fix 2.15GB bug
- eat some poo
- add status bar when submitting
'''


from System.IO import *
from System.Text import *

from Deadline.Scripting import *

from datetime import date

import os
import shutil
import ConfigParser

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
	dialogHeight = 430
	labelWidth = 100
	tabHeight = 600
	padding = 24
	smallControlWidth = dialogWidth-labelWidth-padding
	fullControlWidth = dialogWidth-labelWidth-padding
	
	scriptDialog = DeadlineScriptEngine.GetScriptDialog()
	scriptDialog.SetSize( dialogWidth+padding, dialogHeight )
	scriptDialog.SetTitle( 'Create Quicktime' )
	
	# Start Settings Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Movie Settings', False )
	# FPS Range Slider
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'FPSLabel', 'LabelControl', 'FPS', labelWidth, -1 )
	scriptDialog.AddRangeControl ( 'FPSRangeBox', 'RangeControl', 30, 1, 60, 0, 1, fullControlWidth, -1 )
	scriptDialog.EndRow()
	'''
	# FPS Range Popup
	fps = ('25', '30', '50', '60')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'ResolutionLabel', 'LabelControl', 'Resolution', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'FPSRangeBox' , 'ComboControl', fps[1], fps, smallControlWidth, -1 )
	scriptDialog.EndRow()
	'''
	# Resolution Popup
	resolutions = ('Full Resolution', 'Half Resolution', 'Third Resolution', 'Quarter Resolution')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'ResolutionLabel', 'LabelControl', 'Resolution', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'ResolutionComboBox' , 'ComboControl', resolutions[1], resolutions, smallControlWidth, -1 )
	scriptDialog.EndRow()
	# Codec Popup
	codecs = ('Animation','H.264','ProRes 422')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'CodecLabel', 'LabelControl', 'Codec', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'CodecComboBox' , 'ComboControl', codecs[2], codecs, smallControlWidth, -1 )
	scriptDialog.EndRow()
	'''
	# Bitrate Range
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'BitRateLabel', 'LabelControl', 'H.264 Bit Rate', labelWidth, -1 )
	scriptDialog.AddRangeControl ( 'BitRateRangeBox', 'RangeControl', 8000, 1000, 20000, 0, 1000, fullControlWidth, -1 )
	scriptDialog.EndRow()
	'''

	# End Settings group
	scriptDialog.EndGroupBox( False )
	
	# Start Location Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Save Location', False )
	# Add Radio Buttons
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationLabel', 'LabelControl', 'Location', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDirSame", "RadioControl", False, "Same Directory", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel1', 'LabelControl', '', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDirParent", "RadioControl", False, "Parent Directory", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel2', 'LabelControl', '', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDir2dWip", "RadioControl", True, "2D/_Renders/WIP", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel3', 'LabelControl', '', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDir3dWip", "RadioControl", False, "3D/Renders/_WIP", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	# End Location group 
	scriptDialog.EndGroupBox( False )

	# Start Settings Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Other Settings', False )
	# Slate Checkbox
	scriptDialog.AddRow()
	scriptDialog.AddSelectionControl( 'SlateCheckBox', 'CheckBoxControl', False, 'Show slate on first frame', dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	# Frames Checkbox
	scriptDialog.AddRow()
	scriptDialog.AddSelectionControl( 'FramesCheckBox', 'CheckBoxControl', False, 'Show frame numbers', dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	# Date Checkbox
	scriptDialog.AddRow()
	scriptDialog.AddSelectionControl( 'AppendDateCheckBox', 'CheckBoxControl', True, 'Append date to filename', dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	# End Location group 
	scriptDialog.EndGroupBox( False )

	
	# Submit and Cancel buttons
	scriptDialog.AddRow()
	aboutButton = scriptDialog.AddControl( 'AboutButton', 'ButtonControl', '?', 20, -1 )
	aboutButton.ValueModified += AboutButtonPressed
	scriptDialog.AddControl( 'DummyLabel1', 'LabelControl', '', 20,-1 )
	cancelButton = scriptDialog.AddControl( 'CancelButton', 'ButtonControl', 'Cancel', 100, -1 )
	cancelButton.ValueModified += CancelButtonPressed
	submitButton = scriptDialog.AddControl( 'SubmitButton', 'ButtonControl', 'Submit', 100, -1)
	submitButton.ValueModified += SubmitButtonPressed
	scriptDialog.EndRow()
	
	# Read in config File
	configFile = ClientUtils.GetCurrentUserHomeDirectory() + "/settings/JobCreateQuicktimeSettings.ini"
	ReadStickySettings( scriptDialog, configFile )
	
	scriptDialog.ShowDialog( False )


########################################################################
## Helper Functions
########################################################################

def ReadStickySettings( dialog, configFile ):
	if FileExists( configFile ):
		config = ConfigParser.ConfigParser()
		config.read( configFile )
		if config.has_section( 'Sticky' ):
			dialogControl = 'CodecComboBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				dialog.SetValue( dialogControl, configValue )
			dialogControl = 'FPSRangeBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				dialog.SetValue( dialogControl, configValue )
			dialogControl = 'ResolutionComboBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				dialog.SetValue( dialogControl, configValue )
			dialogControl = 'AppendDateCheckBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
			dialogControl = 'SlateCheckBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
			dialogControl = 'FramesCheckBox'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
			dialogControl = 'RadioDirSame'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
			dialogControl = 'RadioDirParent'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
			dialogControl = 'RadioDir2dWip'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )
				
			dialogControl = 'RadioDir3dWip'
			if config.has_option( 'Sticky', dialogControl ):
				configValue = config.get( 'Sticky', dialogControl )
				if configValue == 'True':
					dialog.SetValue( dialogControl, True )
				else:
					dialog.SetValue( dialogControl, False )


def WriteStickySettings( dialog, configFile ):
	config = ConfigParser.ConfigParser()
	config.add_section( "Sticky" )
	
	config.set( "Sticky", "CodecComboBox", dialog.GetValue( 'CodecComboBox' ) )
	config.set( "Sticky", "FPSRangeBox", dialog.GetValue( 'FPSRangeBox' ) )
	config.set( "Sticky", "ResolutionComboBox", dialog.GetValue( 'ResolutionComboBox' ) )
	config.set( "Sticky", "AppendDateCheckBox", dialog.GetValue( 'AppendDateCheckBox' ) )
	config.set( "Sticky", "SlateCheckBox", dialog.GetValue( 'SlateCheckBox' ) )
	config.set( "Sticky", "FramesCheckBox", dialog.GetValue( 'FramesCheckBox' ) )
	config.set( "Sticky", "RadioDirSame", dialog.GetValue( 'RadioDirSame' ) )
	config.set( "Sticky", "RadioDirParent", dialog.GetValue( 'RadioDirParent' ) )
	config.set( "Sticky", "RadioDir2dWip", dialog.GetValue( 'RadioDir2dWip' ) )
	config.set( "Sticky", "RadioDir3dWip", dialog.GetValue( 'RadioDir3dWip' ) )
	
	fileHandle = open( configFile, "w" )
	config.write( fileHandle )
	fileHandle.close()
	
	
def GetScaleAmount ( resolution ):
	scaleAmount = 1.0
	if resolution=='Half Resolution':
		scaleAmount = 0.5
	elif resolution=='Third Resolution':
		scaleAmount = 0.33
	elif resolution=='Quarter Resolution':
		scaleAmount = 0.25
	return scaleAmount		
	
	

########################################################################
## Button Functions
########################################################################

def AboutButtonPressed( *args ):
	scriptDialog.ShowMessageBox ( "Written by Daniel Harkness, Spinifex Group\n\nGithub:\nhttps://github.com/spinifexgroup-studio/deadline\n\nGithub Script Path:\n/scripts/Jobs/JobCreateQuicktime"  , 'About' )


def CancelButtonPressed( *args ):
	scriptDialog.CloseDialog()


def SubmitButtonPressed( *args ):
	global scriptDialog
	submitResultsString = ""
	
	# Get list of jobs
	jobs = JobUtils.GetSelectedJobs()
	numJobs = len( jobs )
	
	# Get Data from Dialog Box
	codec = str( scriptDialog.GetValue( 'CodecComboBox' ) )
	# bitRate = int( scriptDialog.GetValue( 'BitRateRangeBox' ) )
	frameRate = int( scriptDialog.GetValue( 'FPSRangeBox' ) )
	resolution = str( scriptDialog.GetValue( 'ResolutionComboBox' ) )
	shouldAppendLocation = scriptDialog.GetValue ( 'AppendDateCheckBox' )
	shouldWriteSlate = scriptDialog.GetValue ( 'SlateCheckBox' )
	shouldWriteFrames = scriptDialog.GetValue ( 'FramesCheckBox' )
	shouldWriteToSameDir = scriptDialog.GetValue ( 'RadioDirSame' )
	shouldWriteToParentDir = scriptDialog.GetValue ( 'RadioDirParent' )
	shouldWriteTo2dWipDir = scriptDialog.GetValue ( 'RadioDir2dWip' )
	shouldWriteTo3dWipDir = scriptDialog.GetValue ( 'RadioDir3dWip' )
	
	# Get Scale Factor
	scaleAmount = GetScaleAmount ( resolution )
		
	# Get Nuke App Path	
	nukePath = ''
	if IsRunningOnMac():
		nukePath = '/Applications/Nuke6.3v4/Nuke6.3v4.app/Contents/MacOS/Nuke6.3v4'
	else:
		nukePath = 'C:/Program Files/Nuke6.3v4/Nuke6.3.exe'
		if not FileExists (nukePath):
			nukePath = 'C:/Program Files/Nuke6.3v1/Nuke6.3.exe'
	if not FileExists (nukePath):
		CloseDialog()	
		scriptDialog.ShowMessageBox ( "Cannot run wihout Nuke 6.3 installed"  , 'Error' )
		return

	# Get directories
	pluginDirectory = RepositoryUtils.GetScriptsDirectory() + '/Jobs/JobCreateQuicktime'
	templateNukeScript = pluginDirectory + '/JobCreateQuicktimeNukeTemplate.nk'
	nukePythonScript = pluginDirectory + '/ModifyNukeTemplate.py'

	currentUserHomeDirectory = ClientUtils.GetCurrentUserHomeDirectory()
	currentUserTempDirectory = currentUserHomeDirectory + '/temp'
		
	# Copy Font for checking Nuke script locally
	fontPath = pluginDirectory+'/Arial.ttf'
	try:
		shutil.copyfile ( fontPath , currentUserTempDirectory+'/Arial.ttf' )
	except:
		pass

	# Debugging
	debugFile = currentUserTempDirectory+'/JobCreateQuicktimeDebug.txt'
	debugFileHandle = open( debugFile, 'w' )
	
	debugFileHandle.write ( str(codec)+'\n' )
	'''
	debugFileHandle.write ( str(bitRate)+'\n' )
	debugFileHandle.write ( str(frameRate)+'\n' )
	debugFileHandle.write ( str(resolution)+'\n' )
	debugFileHandle.write ( str(scaleAmount)+'\n' )
	debugFileHandle.write ( '\n' )
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
			moviePath = outputDirectory + "/" + Path.GetFileNameWithoutExtension( outputPath )
			moviePath = moviePath.replace("_#","").replace(".#","").replace("[#","").replace("#]","").replace("#","")
			
			# Build Directory of writing one level up
			if shouldWriteToParentDir:
				moviePath = PathUtils.ToPlatformIndependentPath ( moviePath ).replace('\\','/')
				moviePathSplit = moviePath.split ('/')
				newMoviePath = ''
				for k in range ( 0, len (moviePathSplit) - 2 ):
					pathItem = moviePathSplit[k]
					if pathItem != '':
						newMoviePath = newMoviePath + '/' + pathItem
				moviePath = newMoviePath + '/' + moviePathSplit[ len(moviePathSplit) - 1 ]
			
			# Build Directory if Writing to WIP directories
			if shouldWriteTo2dWipDir or shouldWriteTo3dWipDir:
				moviePath = RepositoryUtils.CheckPathMapping( moviePath , True )
				moviePathSplit = moviePath.split ('/')
				newMoviePath = ''
				# Iterate through list till we get to '2_Studio' folder structure
				for pathItem in moviePathSplit:
					# Check for null strings - prevents // in path
					if pathItem != '':
						newMoviePath = newMoviePath + '/' + pathItem
						if pathItem == '2_Studio':
							if shouldWriteTo2dWipDir:
								newMoviePath = newMoviePath + '/2D/_Renders/WIP'
							if shouldWriteTo3dWipDir:
								newMoviePath = newMoviePath + '/3D/Renders/_WIP'
							# Make a date folder if we are making dated files
							if shouldAppendLocation:
								# ISO date no dashes
								dateString = str(date.today() ).replace('-','')
								newMoviePath = newMoviePath + '/' + dateString
								if not os.path.exists (newMoviePath):
									os.mkdir (newMoviePath)
							# Finish up the path and break		
							moviePath = newMoviePath + '/' + moviePathSplit[ len(moviePathSplit) - 1 ]
							break
			
			# Append date to file in form _YYYY-MM-DD_VV.mov
			if shouldAppendLocation:
				dateString = str ( date.today() ).replace('-','')
				haveFoundDatedFileName = False
				k = 1
				while not haveFoundDatedFileName:
					versionString = '{0:02d}'.format(k)
					k = k + 1
					newMoviePath = moviePath + '_' + dateString + '_' + versionString + '.mov'
					if not FileExists (newMoviePath):
						moviePath = newMoviePath
						haveFoundDatedFileName = True
			else:
				moviePath = moviePath + '.mov'
			
			debugFileHandle.write ( moviePath+'\n' )
			
			# Get some information about the job
			sceneFile = JobUtils.GetDataFilename( i )
			firstFrame = JobUtils.GetFirstFrame( i )
			lastFrame = JobUtils.GetLastFrame( i )
			
			# Create Nuke Script for submission
			nukeInputSequence = outputPath
			submissionNukeScript = currentUserTempDirectory + '/JobCreateQuicktimeNukeSubmissionScript.nk'
			
			nukePythonScript = RepositoryUtils.CheckPathMapping ( nukePythonScript, True ).replace('\\','/')
			templateNukeScript = RepositoryUtils.CheckPathMapping ( templateNukeScript, True ).replace('\\','/')
			submissionNukeScript = RepositoryUtils.CheckPathMapping ( submissionNukeScript, True ).replace('\\','/')
			nukeInputSequence = RepositoryUtils.CheckPathMapping ( nukeInputSequence, True ).replace('\\','/')
			moviePath = RepositoryUtils.CheckPathMapping ( moviePath, True ).replace('\\','/')
			fontPath = RepositoryUtils.CheckPathMapping ( fontPath, True ).replace('\\','/')
			
			nukeArgList = [ '-t', nukePythonScript, templateNukeScript , submissionNukeScript , nukeInputSequence , moviePath, fontPath, codec ]
			for k in range ( 1, len (nukeArgList) ):
				nukeArgList[k] = '\"' + nukeArgList[k] + '\"'
			nukeArgList.extend( [ str(firstFrame) , str(lastFrame) , str(scaleAmount) , str(frameRate), str(shouldWriteSlate), str(shouldWriteFrames) ] )
			nukeArgs = ' '.join( nukeArgList )
			nukeProcess = ProcessUtils.SpawnProcess ( nukePath , nukeArgs, currentUserTempDirectory )
			if not ProcessUtils.WaitForExit ( nukeProcess, 10000 ): # Wait up to ten seconds for script to be made
				return #nuke failed

			# Create job info file
			jobInfoFile = currentUserTempDirectory + ("/nuke_quicktime_submit_info.job")
			fileHandle = open( jobInfoFile, "w" )
			fileHandle.write( "Plugin=Nuke\n" )
			fileHandle.write( "Name=%s [CREATE QUICKTIME]\n" % job.JobName )
			comment = ''
			if shouldAppendLocation:
				comment = comment + 'dated, '
			if shouldWriteSlate: 
				comment = comment + 'slated, '
			if shouldWriteToSameDir:
				comment = comment + 'in sequence directory'
			if shouldWriteToParentDir:
				comment = comment + 'in sequence parent'
			if shouldWriteTo2dWipDir:
				comment = comment + 'in 2D WIP'
			if shouldWriteTo3dWipDir:
				comment = comment + 'in 3D WIP'

			fileHandle.write( "Comment=%s\n" % comment )
			fileHandle.write( "Department=%s\n" % "Pure Awesome" )
			fileHandle.write( "Pool=%s\n" % "2d_nuke_qt" )
			fileHandle.write( "Group=%s\n" % "2d_mac" )
			fileHandle.write( "Priority=%s\n" % str(job.JobPriority) )
			fileHandle.write( "MachineLimit=1\n" )
			fileHandle.write( "ConcurrentTasks=1\n" )
			fileHandle.write( "Frames=%s\n" % str(job.JobFrames) )
			fileHandle.write( "ChunkSize=100000\n")
			
			if job.JobStatus != 'Completed':
				fileHandle.write( "JobDependencies=%s\n" % job.JobId )
			fileHandle.close()

			# Create the plugin info file
			pluginInfoFile = currentUserTempDirectory + ("/nuke_quicktime_plugin_info.job")
			fileHandle = open( pluginInfoFile, "w" )
			fileHandle.write( "Version=%s.%s\n" % (6, 3) )
			fileHandle.close()

			submitString = ClientUtils.ExecuteCommandAndGetOutput ( ( jobInfoFile , pluginInfoFile , submissionNukeScript ) )
			submitResultsString = submitResultsString+submitString+'\n'
			
			
			# Debugging
			
			debugFileHandle.write ( str(shouldWriteSlate)+'\n' )			
			debugFileHandle.write ( str(shouldWriteFrames)+'\n' )			
			debugFileHandle.write ( str(nukeArgs)+'\n' )		
			
			debugFileHandle.write ( '\n' )
			
		
		
	debugFileHandle.close()
	configFile = currentUserHomeDirectory + "/settings/JobCreateQuicktimeSettings.ini"
	WriteStickySettings( scriptDialog, configFile )
	scriptDialog.CloseDialog()
	scriptDialog.ShowMessageBox ( submitResultsString , 'Results of Submission' )

	