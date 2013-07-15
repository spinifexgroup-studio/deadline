'''
Create proxies deadline monitor - uses nuke to do the job
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
	
	dialogWidth = 300
	dialogHeight = 265
	labelWidth = 100
	tabHeight = 600
	padding = 24
	smallControlWidth = dialogWidth-labelWidth-padding
	fullControlWidth = dialogWidth-labelWidth-padding
	
	scriptDialog = DeadlineScriptDialog()
	scriptDialog.SetSize( dialogWidth+padding, dialogHeight )
	scriptDialog.SetTitle( 'Create Proxy' )
	
	# Start Settings Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Format Settings', False )
	
	# Resolution Popup
	resolutions = ('Full Resolution', 'Half Resolution', 'Third Resolution', 'Quarter Resolution')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'ResolutionLabel', 'LabelControl', 'Resolution', labelWidth, -1 )
	scriptDialog.AddComboControl ( 'ResolutionComboBox' , 'ComboControl', resolutions[1], resolutions, smallControlWidth, -1 )
	scriptDialog.EndRow()
	# Format Popup
	formats = ('Same as Input','EXR','TGA','JPG','ProRes 4444')
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'FormatLabel', 'LabelControl', 'Format', labelWidth, -1 )
	formatCombo = scriptDialog.AddComboControl ( 'FormatComboBox' , 'ComboControl', formats[0], formats, smallControlWidth, -1 )
	formatCombo.ValueModified.connect(FormatComboModified)
	scriptDialog.EndRow()
	# FPS Range Slider
	scriptDialog.AddRow()
	scriptDialog.AddControl( 'FPSLabel', 'LabelControl', 'ProRes FPS', labelWidth, -1 )
	scriptDialog.AddRangeControl ( 'FPSRangeBox', 'RangeControl', 30, 1, 60, 0, 1, fullControlWidth, -1 )
	scriptDialog.EndRow()


	# End Settings group
	scriptDialog.EndGroupBox( False )
		
	# Start Location Group
	scriptDialog.AddGroupBox( 'GroupBox', 'Save Location (Sub Dir Preferred)', False )
	# Add Radio Buttons
	
	'''
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirSub", "RadioControl", True, "Sub Directory: filedir/proxy/filename", "LocationGroup", dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirSame", "RadioControl", False, "Same Directory: filedir/filename_proxy", "LocationGroup", dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirParent", "RadioControl", False, "Parent Directory: filedir_proxy/filename", "LocationGroup", dialogWidth-padding, -1 )
	scriptDialog.EndRow()
	'''
	
	
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirSub", "RadioControl", True, "Sub Directory: filedir/proxy/filename", "LocationGroup", 20, -1 )
	scriptDialog.AddControl( 'label1', 'LabelControl', 'Sub Directory: filedir/proxy/filename', dialogWidth-padding-20, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirSame", "RadioControl", False, "Same Directory: filedir/filename_proxy", "LocationGroup", 20, -1 )
	scriptDialog.AddControl( 'label2', 'LabelControl', 'Same Directory: filedir/filename_proxy', dialogWidth-padding-20, -1 )
	scriptDialog.EndRow()
	scriptDialog.AddRow()
	scriptDialog.AddRadioControl( "RadioDirParent", "RadioControl", False, "Parent Directory: filedir_proxy/filename", "LocationGroup", 20, -1 )
	scriptDialog.AddControl( 'label3', 'LabelControl', 'Parent Directory: filedir_proxy/filename', dialogWidth-padding-20, -1 )
	scriptDialog.EndRow()
	
	
	# End Location group 
	scriptDialog.EndGroupBox( False )


	# Progress Bar
	scriptDialog.AddRow()
	scriptDialog.AddRangeControl( "ProgressBox", "ProgressBarControl", 1, 1, 100, 0, 0, dialogWidth, -1 )
	scriptDialog.EndRow()


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
	configFile = ClientUtils.GetCurrentUserHomeDirectory() + "/settings/JobCreateProxySettings.ini"
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
			dialogControl = 'FormatComboBox'
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
			dialogControl = 'RadioDirSub'
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
	FormatComboModified()


def WriteStickySettings( dialog, configFile ):
	config = ConfigParser.ConfigParser()
	config.add_section( "Sticky" )
	
	config.set( "Sticky", "FormatComboBox", dialog.GetValue( 'FormatComboBox' ) )
	config.set( "Sticky", "FPSRangeBox", dialog.GetValue( 'FPSRangeBox' ) )
	config.set( "Sticky", "ResolutionComboBox", dialog.GetValue( 'ResolutionComboBox' ) )
	config.set( "Sticky", "RadioDirSub", dialog.GetValue( 'RadioDirSub' ) )
	config.set( "Sticky", "RadioDirSame", dialog.GetValue( 'RadioDirSame' ) )
	config.set( "Sticky", "RadioDirParent", dialog.GetValue( 'RadioDirParent' ) )
	
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

def FormatComboModified ( *args ):
	global scriptDialog
	formatComboValue = scriptDialog.GetValue ( 'FormatComboBox' )
	if formatComboValue == 'ProRes 4444':
		scriptDialog.SetEnabled ( 'FPSLabel', True )
		scriptDialog.SetEnabled ( 'FPSRangeBox', True )
	else:
		scriptDialog.SetEnabled ( 'FPSLabel', False )
		scriptDialog.SetEnabled ( 'FPSRangeBox', False )
		

def AboutButtonPressed( *args ):
	global scriptDialog
	scriptDialog.ShowMessageBox ( "Written by Daniel Harkness, Spinifex Group\n\nGithub:\nhttps://github.com/spinifexgroup-studio/deadline\n\nGithub Script Path:\n/scripts/Jobs/JobCreateProxy"  , 'About' )


def CancelButtonPressed( *args ):
	global scriptDialog
	scriptDialog.CloseDialog()


def SubmitButtonPressed( *args ):
	global scriptDialog
	
	submitResultsString = ''
	
	# Get list of jobs
	jobs = JobUtils.GetSelectedJobs()
	numJobs = len( jobs )
	
	# Get Data from Dialog Box
	format = str( scriptDialog.GetValue( 'FormatComboBox' ) )
	frameRate = int( scriptDialog.GetValue( 'FPSRangeBox' ) )
	resolution = str( scriptDialog.GetValue( 'ResolutionComboBox' ) )
	shouldWriteToSubDir = scriptDialog.GetValue ( 'RadioDirSub' )
	shouldWriteToSameDir = scriptDialog.GetValue ( 'RadioDirSame' )
	shouldWriteToParentDir = scriptDialog.GetValue ( 'RadioDirParent' )
	
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
	pluginDirectory = RepositoryUtils.GetCustomPluginsDirectory() + '/JobCreateProxy'
	templateNukeScript = pluginDirectory + '/JobCreateProxyNukeTemplate.nk'
	nukePythonScript = pluginDirectory + '/ModifyNukeTemplate.py'

	currentUserHomeDirectory = ClientUtils.GetCurrentUserHomeDirectory()
	currentUserTempDirectory = currentUserHomeDirectory + '/temp'
		
	# Debugging
	debugFile = currentUserTempDirectory+'/JobCreateProxyDebug.txt'
	debugFileHandle = open( debugFile, 'w' )
	
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
			inputPath = Path.Combine(outputDirectory,outputFilename).replace("//","/")
			
			outputFilenameBase, outputFilenameExt = os.path.splitext (outputFilename)
			
			# set submission group to all computers - we'll change it to macs if it's a quicktime
			submitGroup = "all"

			#formats = ('Same as Input','EXR','TGA','JPG','ProRes 4444')
			if not format == 'Same as Input':
				if format == 'EXR':
					outputFilenameExt = '.exr'
				if format == 'TGA':
					outputFilenameExt = '.tga'
				if format == 'JPG':
					outputFilenameExt = '.jpg'
				if format == 'ProRes 4444':
					outputFilenameBase = outputFilenameBase.replace("_#","").replace(".#","").replace("#","")
					outputFilenameExt = '.mov'
					# prores can only be written via mac
					submitGroup = "mac"
			
			# Set up proxy part of filename
			if shouldWriteToSameDir:
				splitSymbol = '#'
				if '.#' in outputFilenameBase:
					splitSymbol = '.#'
				if '_#' in outputFilenameBase:
					splitSymbol = '_#'
				
				outputFilenameBase = outputFilenameBase.split(splitSymbol,1)[0] + '_proxy' + splitSymbol + outputFilenameBase.split(splitSymbol,1)[1]
				
			# Writing to sub directory ?
			if shouldWriteToSubDir:
				outputDirectory = outputDirectory + '/proxy'

			# Writing to parent directory ?
			if shouldWriteToParentDir:
				outputDirectory = PathUtils.ToPlatformIndependentPath ( outputDirectory ).replace('\\','/')
				outputDirectorySplit = outputDirectory.split ('/')
				newDirectoryPath = ''
				for k in range ( 0, len (outputDirectorySplit) - 1 ):
					pathItem = outputDirectorySplit[k]
					if pathItem != '':
						newDirectoryPath = newDirectoryPath + '/' + pathItem
				if format == 'ProRes 4444':
					outputDirectory = newDirectoryPath
					outputFilenameBase = outputFilenameBase + '_proxy'
				else:
					outputDirectory = newDirectoryPath + '/' + outputDirectorySplit[ len (outputDirectorySplit) -1 ] + '_proxy'

			# Make Proxy dir if doesn't exist
			if not os.path.exists (outputDirectory):
				os.mkdir (outputDirectory)

			outputFilename = outputFilenameBase + outputFilenameExt
			outputPath = Path.Combine(outputDirectory,outputFilename).replace("//","/")
						
			# Get some information about the job
			sceneFile = JobUtils.GetDataFilename( i )
			firstFrame = JobUtils.GetFirstFrame( i )
			lastFrame = JobUtils.GetLastFrame( i )
			
			# Create Nuke Script for submission
			submissionNukeScript = currentUserTempDirectory + '/JobCreateProxyNukeSubmissionScript.nk'
			
			nukePythonScript = RepositoryUtils.CheckPathMapping ( nukePythonScript, True ).replace('\\','/')
			templateNukeScript = RepositoryUtils.CheckPathMapping ( templateNukeScript, True ).replace('\\','/')
			submissionNukeScript = RepositoryUtils.CheckPathMapping ( submissionNukeScript, True ).replace('\\','/')
			inputPath = RepositoryUtils.CheckPathMapping ( inputPath, True ).replace('\\','/')
			outputPath = RepositoryUtils.CheckPathMapping ( outputPath, True ).replace('\\','/')
			
			nukeArgList = [ '-t', nukePythonScript, templateNukeScript , submissionNukeScript , inputPath , outputPath, format ]
			for k in range ( 1, len (nukeArgList) ):
				nukeArgList[k] = '\"' + nukeArgList[k] + '\"'
			nukeArgList.extend( [ str(firstFrame) , str(lastFrame) , str(scaleAmount) , str(float(frameRate)) ] )
			nukeArgs = ' '.join( nukeArgList )
			nukeProcess = ProcessUtils.SpawnProcess ( nukePath , nukeArgs, currentUserTempDirectory )
			if not ProcessUtils.WaitForExit ( nukeProcess, 10000 ): # Wait up to ten seconds for script to be made
				return #nuke failed

			# Create job info file
			jobInfoFile = currentUserTempDirectory + ("/nuke_proxy_submit_info.job")
			fileHandle = open( jobInfoFile, "w" )
			fileHandle.write( "Plugin=Nuke\n" )
			fileHandle.write( "Name=%s [CREATE PROXY]\n" % job.JobName )
			comment = ''
			if shouldWriteToSubDir:
				comment = comment + 'in sub directory'
			if shouldWriteToSameDir:
				comment = comment + 'in same directory'
			if shouldWriteToParentDir:
				comment = comment + 'in parent directory'

			fileHandle.write( "Comment=%s\n" % comment )
			fileHandle.write( "Department=%s\n" % "Pure Awesome" )
			fileHandle.write( "Pool=%s\n" % "nuke" )
			fileHandle.write( "Group=%s\n" % submitGroup )
			fileHandle.write( "Priority=%s\n" % str(job.JobPriority) )
			fileHandle.write( "MachineLimit=1\n" )
			fileHandle.write( "ConcurrentTasks=1\n" )
			fileHandle.write( "Frames=%s\n" % str(job.JobFrames) )
			fileHandle.write( "ChunkSize=100\n")
			
			if job.JobStatus != 'Completed':
				fileHandle.write( "JobDependencies=%s\n" % job.JobId )
			fileHandle.close()

			# Create the plugin info file
			pluginInfoFile = currentUserTempDirectory + ("/nuke_proxy_plugin_info.job")
			fileHandle = open( pluginInfoFile, "w" )
			fileHandle.write( "Version=%s.%s\n" % (6, 3) )
			fileHandle.close()

			submitString = ClientUtils.ExecuteCommandAndGetOutput ( ( jobInfoFile , pluginInfoFile , submissionNukeScript ) )

			# Print submission results to console - we only dsplay result of final submission
			print "---------------------------------------------------------------------------------\n"
			print submitResultsString
			submitResultsString = submitString
			
			
			# Update progress Bar
			
			progress = int (100.0/numJobs)
			progress = (i+1)*progress
			if progress > 100:
				progress = 100
			scriptDialog.SetValue( "ProgressBox", progress )
			print ("Perecent of jobs submitted: " + str(progress) + "\n" )
			# Debugging
			
			debugFileHandle.write ( str(nukeArgs)+'\n' )					
			debugFileHandle.write ( '\n' )
			
		
		
	debugFileHandle.close()
	configFile = currentUserHomeDirectory + "/settings/JobCreateProxySettings.ini"
	WriteStickySettings( scriptDialog, configFile )
	scriptDialog.CloseDialog()
	scriptDialog.ShowMessageBox ( "Full submission results are in console. Last submission results:\n\n" + submitResultsString , 'Results of Submission' )
	
	