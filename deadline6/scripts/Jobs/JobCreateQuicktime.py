'''
Create a quicktime from deadline monitor - uses nuke to do the job
TODO:
- fix 2.15GB bug
- add status bar when submitting
'''


from System.IO import *
from System.Text import *

from Deadline.Scripting import *
from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

from datetime import date

import os
import shutil
import ConfigParser
import threading
import platform

########################################################################
## Globals
########################################################################

scriptDialog = None
settings = None

########################################################################
##  Threads To do core logic
########################################################################


class workThread ( threading.Thread):
	def __init__(self, threadID, name ):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
	def run(self):
		global scriptDialog
		
		print "\n\n\n\n"
		print "//////////////////////////////////////////////////////////////////////////////////////////"
		print "//////////////////////////////////////////////////////////////////////////////////////////"
		print "//////////////////////////////////////////////////////////////////////////////////////////\n"

		print "Starting " + self.name
		SubmitJobs()
		print "Exiting " + self.name


########################################################################
## Main Function Called By Deadline
########################################################################

def __main__():
	global scriptDialog
	global settings
	global progressBarControl
	
	dialogWidth = 250
	dialogHeight = 430
	labelWidth = 100
	tabHeight = 600
	padding = 24
	smallControlWidth = dialogWidth-labelWidth-padding
	fullControlWidth = dialogWidth-labelWidth-padding
	
	scriptDialog = DeadlineScriptDialog()
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
	#scriptDialog.AddControl( 'LocationLabel', 'LabelControl', 'Location', labelWidth, -1 )
	scriptDialog.AddControl( 'LocationLabel', 'LabelControl', 'Same Directory', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDirSame", "RadioControl", False, "Same Directory", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel1', 'LabelControl', 'Parent Directory', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDirParent", "RadioControl", False, "Parent Directory", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel2', 'LabelControl', '2D/_Renders/WIP', labelWidth, -1 )
	scriptDialog.AddRadioControl( "RadioDir2dWip", "RadioControl", True, "2D/_Renders/WIP", "LocationGroup", smallControlWidth, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'LocationDummyLabel3', 'LabelControl', '3D/Renders/_WIP', labelWidth, -1 )
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
	
	# Progress Bar
	# scriptDialog.AddRow()
	# progressBarControl = scriptDialog.AddRangeControl( "ProgressBox", "ProgressBarControl", 1, 1, 100, 0, 0, dialogWidth, -1 )
	# scriptDialog.EndRow()

	
	# Submit and Cancel buttons
	scriptDialog.AddRow()
	aboutButton = scriptDialog.AddControl( 'AboutButton', 'ButtonControl', '?', 20, -1 )
	aboutButton.ValueModified.connect(AboutButtonPressed)
	scriptDialog.AddControl( 'DummyLabel1', 'LabelControl', '', 20,-1 )
	cancelButton = scriptDialog.AddControl( 'CancelButton', 'ButtonControl', 'Cancel', 100, -1 )
	cancelButton.ValueModified.connect(CancelButtonPressed)
	submitButton = scriptDialog.AddControl( 'SubmitButton', 'ButtonControl', 'Submit', 100, -1)
	submitButton.ValueModified.connect(SubmitButtonPressed)
	scriptDialog.EndRow()
	
	
	
	# Read in config File
	configFile = ClientUtils.GetCurrentUserHomeDirectory() + "/settings/JobCreateQuicktimeSettings.ini"
	ReadStickySettings( scriptDialog, configFile )
	
	scriptDialog.ShowDialog( True )


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
	
	
def SubmitJobs( *args ):
	
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
	pluginDirectory = RepositoryUtils.GetCustomPluginsDirectory() + '/JobCreateQuicktime'
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
			outputPath = Path.Combine(outputDirectory,outputFilename).replace("\\","/").replace("//","/")
			moviePath = outputDirectory + "/" + Path.GetFileNameWithoutExtension( outputPath )
			
			# maya ????? bug fix
			if job.JobPlugin == "MayaBatch" or job.JobPlugin == "MayaCmd":
				moviePath = moviePath.replace("?","#")
			
			moviePath = moviePath.replace("_#","").replace(".#","").replace("[#","").replace("#]","").replace("#","")
			
			# Build Directory of writing one level up
			if shouldWriteToParentDir:
				moviePath = PathUtils.ToPlatformIndependentPath ( moviePath ).replace("\\","/").replace("//","/")
				moviePathSplit = moviePath.split ('/')
				fileName = moviePathSplit[ len(moviePathSplit) - 1 ]
				newMoviePath = ''
				for k in range ( 0, len (moviePathSplit) - 2 ):
					pathItem = moviePathSplit[k]
					if pathItem != '':
						newMoviePath = newMoviePath + '/' + pathItem
				outputDirectory = newMoviePath
				outputFilename = fileName
				moviePath = newMoviePath + '/' + fileName
				
			print ( "The os is %s" % platform.system() )
			
			# Build Directory if Writing to WIP directories
			if shouldWriteTo2dWipDir or shouldWriteTo3dWipDir:
				moviePath = RepositoryUtils.CheckPathMapping( moviePath , True ).replace("\\","/")
				
				moviePathSplit = moviePath.split ('/')
				fileName = moviePathSplit[ len(moviePathSplit) - 1 ]
				newMoviePath = ''
				# Iterate through list till we get to 2D or 3D directory
				for k in range ( 0, len (moviePathSplit)):
					popItem = moviePathSplit.pop()
					if popItem == '2D' or popItem == '3D':
						for pathItem in moviePathSplit:
							# Check for null strings - prevents // in path
							if pathItem != '':
								newMoviePath = newMoviePath + '/' + pathItem
						if shouldWriteTo2dWipDir:
							newMoviePath = newMoviePath + '/2D/_Renders/WIP'
						if shouldWriteTo3dWipDir:
							newMoviePath = newMoviePath + '/3D/Renders/_WIP'
						# Make a date folder if we are making dated files
						if shouldAppendLocation:
							# ISO date no dashes
							dateString = str(date.today() ).replace('-','')
							newMoviePath = newMoviePath + '/' + dateString
							
							# Fix windows paths
							if platform.system() == 'Windows':
								newMoviePath = newMoviePath[1:]
								# add // if not a drive letter
								if newMoviePath[1] != ":":
									newMoviePath = "//" + newMoviePath

							if not os.path.exists (newMoviePath):
								os.mkdir (newMoviePath)
						# Finish up the path and break		
						outputDirectory = newMoviePath
						outputFilename = fileName
						moviePath = newMoviePath + '/' + fileName
						
						break
						
				'''
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
				'''
			
			# Append date to file in form _YYYY-MM-DD_VV.mov
			if shouldAppendLocation:
				dateString = str ( date.today() ).replace('-','')
				haveFoundDatedFileName = False
				k = 1
				while not haveFoundDatedFileName:
					versionString = '{0:02d}'.format(k)
					k = k + 1
					appendDate = '_' + dateString + '_' + versionString + '.mov'
					newMoviePath = moviePath + appendDate
					if not FileExists (newMoviePath):
						moviePath = newMoviePath
						outputFilename = outputFilename + appendDate
						haveFoundDatedFileName = True
			else:
				moviePath = moviePath + '.mov'
				outputFilename = outputFilename +'.mov'
							
			# Get some information about the job
			# sceneFile = JobUtils.GetDataFilename( i )
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

			# Fix for maya ????? bug
			comment = ''
			if job.JobPlugin == "MayaBatch" or job.JobPlugin == "MayaCmd":
				nukeInputSequence = nukeInputSequence.replace('?','#')
				comment = 'USING ???? MAYA BUG FIX >>> '
			
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
			comment = comment + resolution.replace("Resolution","res") + ', ' + codec + ', '
			if shouldAppendLocation:
				comment = comment + 'dated, '
			if shouldWriteSlate: 
				comment = comment + 'slated, '
			if shouldWriteToSameDir:
				comment = comment + 'in seq dir'
			if shouldWriteToParentDir:
				comment = comment + 'in seq parent'
			if shouldWriteTo2dWipDir:
				comment = comment + 'in 2D WIP'
			if shouldWriteTo3dWipDir:
				comment = comment + 'in 3D WIP'

			fileHandle.write( "Comment=%s  >>>  %s\n" % (comment.upper(), outputFilename) )
			fileHandle.write( "Department=%s\n" % "Autobots" )
			fileHandle.write( "Pool=%s\n" % "nuke" )
			fileHandle.write( "Group=%s\n" % "mac" )
			fileHandle.write( "Priority=%s\n" % str(job.JobPriority) )
			fileHandle.write( "MachineLimit=1\n" )
			fileHandle.write( "ConcurrentTasks=1\n" )
			fileHandle.write( "Frames=%s\n" % str(job.JobFrames) )
			fileHandle.write( "ChunkSize=100000\n")
			fileHandle.write( "OutputDirectory0=%s\n" %  outputDirectory )
			fileHandle.write( "OutputFilename0=%s\n" %  outputFilename )

			
			if job.JobStatus != 'Completed':
				fileHandle.write( "JobDependencies=%s\n" % job.JobId )
			fileHandle.close()

			# Create the plugin info file
			pluginInfoFile = currentUserTempDirectory + ("/nuke_quicktime_plugin_info.job")
			fileHandle = open( pluginInfoFile, "w" )
			fileHandle.write( "Version=%s.%s\n" % (6, 3) )
			fileHandle.close()

			submitString = ClientUtils.ExecuteCommandAndGetOutput ( ( jobInfoFile , pluginInfoFile , submissionNukeScript ) )
			
			# Print submission results to console - we only dsplay result of final submission
			print "---------------------------------------------------------------------------------\n"
			print submitString
			# Print some info to console
			print ( "Nuke Args = %s\n" % nukeArgs )
			
			
			# Update progress Bar
			
			progress = int (100.0/numJobs)
			progress = (i+1)*progress
			if (i+1) >= numJobs:
				progress = 100
			# scriptDialog.SetValue( "ProgressBox", progress )
			# progressBarControl.repaint()
			print ("Create Quicktime: Perecent of jobs submitted: " + str(progress) + "\n" )
		

########################################################################
## Button Functions
########################################################################

def AboutButtonPressed( *args ):
	global scriptDialog
	scriptDialog.ShowMessageBox ( "Written by Daniel Harkness, Spinifex Group\n\nGithub:\nhttps://github.com/spinifexgroup-studio/deadline\n\nGithub Script Path:\n/scripts/Jobs/JobCreateQuicktime"  , 'About' )


def CancelButtonPressed( *args ):
	global scriptDialog
	scriptDialog.CloseDialog()

def SubmitButtonPressed( *args ):
	global scriptDialog

	workerThread = workThread (1, "Create Quicktime Thread")
	workerThread.start()

	configFile = ClientUtils.GetCurrentUserHomeDirectory() + "/settings/JobCreateQuicktimeSettings.ini"
	WriteStickySettings( scriptDialog, configFile )

	scriptDialog.CloseDialog()
	scriptDialog.ShowMessageBox ( "Your jobs will start appearing in the monitor soon.\n\nFull submission results are in the console.", 'Results of Submission' )

	