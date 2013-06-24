from Deadline.Events import *
from Deadline.Scripting import *

from System import *
from System.Diagnostics import *
from System.IO import *

# import random, string
import os, sys, re, traceback
import threading
import time

######################################################################
## This is the function that Deadline calls to get an instance of the
## main DeadlineEventListener class.
######################################################################
def GetDeadlineEventListener():
	return MyEvent()
 
######################################################################
## This is the main DeadlineEventListener class for MyEvent.
######################################################################
class MyEvent (DeadlineEventListener):
	def OnJobFinished( self, job ):
	
		outputDirectories = job.JobOutputDirectories
		outputFilenames = job.JobOutputFileNames
		paddingRegex = re.compile("[^\\?#]*([\\?#]+).*")
 
		# Submit a QT job for each output sequence.
		for i in range( 0, len(outputFilenames) ):


			outputDirectory = outputDirectories[i]
			outputFilename = outputFilenames[i]
			
			# Don't continue on quicktimes
			if not outputFilename.lower().endswith( ".mov" ):
				outputPath = Path.Combine(outputDirectory,outputFilename).replace("//","/")

				inputFilename = outputPath
				movieName = outputDirectory + "/" + Path.GetFileNameWithoutExtension( outputPath ).replace("_#","").replace(".#","").replace("#","") + "_preview"
				frameRange = FrameUtils.Parse ( str (job.JobFrames), 1)

	
				# Setup file paths
				nukeSourceFile = "/Volumes/RESOURCES/05_Motion_Studio_Tools/development/deadline/event_plugins/SlatedQuicktimeGen/nuke/slate_v001.nk"
				randomString = ""
				#randomString = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(5))
				nukeDestFile = GetTempDirectory()+"/slate_v001_submit_"+randomString+".nk"

				# open files for read/write
				sourceHandle = open ( nukeSourceFile, "r" )
				destHandle = open( nukeDestFile, "w" )

				# replace data in nuke script
				for line in sourceHandle:
					if "InputSequenceFirstFrame 1000" in line:
						line = line.replace ("InputSequenceFirstFrame 1000", "InputSequenceFirstFrame " + str(frameRange[0]) )
					if "InputSequenceLastFrame 1000" in line:
						line = line.replace ("InputSequenceLastFrame 1000", "InputSequenceLastFrame " + str(frameRange[-1]) )
					if "_InputSequence_" in line:
						line = line.replace ("_InputSequence_", ("\""+str(inputFilename)+"\"") )
					if "_JobName_" in line:
						line = line.replace ("_JobName_", str(job.JobName) )
					if "_Project_" in line:
						line = line.replace ("_Project_", "" ) 				#shotgun metadata
					if "_Sequence_" in line:
						line = line.replace ("_Sequence_", "" )  				#shotgun metadata
					if "_Shot_" in line:
						line = line.replace ("_Shot_", "" ) 					#shotgun metadata
					if "_Frames_" in line:
						line = line.replace ("_Frames_", str(job.JobFrames) )
					if "_Version_" in line:
						line = line.replace ("_Version_", "")		#shotgun metadata
					if "_FramePath_" in line:
						line = line.replace ("_FramePath_", outputPath)
					if "_ProjectPath_" in line:
						line = line.replace ("_ProjectPath_", str(job.JobAuxiliarySubmissionFileNames[1]))
					if "_Comments_" in line:
						line = line.replace ("_Comments_", str(job.JobComment) )
					if "_FileDestination_" in line:
						line = line.replace ("_FileDestination_.mov", ("\""+movieName+".mov\""))
					destHandle.write ( line )

				# Write and close files
				destHandle.close()
				sourceHandle.close()
			
				# Create job info file
				jobInfoFile = GetTempDirectory() + ("/nuke_submit_info%s.job" % randomString)
				fileHandle = open( jobInfoFile, "w" )
				fileHandle.write( "Plugin=Nuke\n" )
				fileHandle.write( "Name=%s [SLATED QUICKTIME]\n" % job.JobName )
				fileHandle.write( "Comment=Autosubmitted Job making QT from %s\n" % job.JobName )
				fileHandle.write( "Department=%s\n" % "Pure Awesome" )
				fileHandle.write( "Pool=%s\n" % "2d_nuke" )
				fileHandle.write( "Group=%s\n" % "2d_mac" )
				fileHandle.write( "Priority=%s\n" % str(job.JobPriority-1) )
				fileHandle.write( "MachineLimit=1\n" )
				fileHandle.write( "ConcurrentTasks=1\n" )
				fileHandle.write( "Frames=%s\n" % str(job.JobFrames) )
				fileHandle.write( "ChunkSize=100000\n")
				fileHandle.close()
				
				# Create the plugin info file
				pluginInfoFile = GetTempDirectory() + ("/nuke_plugin_info%s.job" % randomString)
				fileHandle = open( pluginInfoFile, "w" )
				fileHandle.write( "SceneFile=%s\n" % nukeDestFile )
				fileHandle.write( "Version=%s.%s\n" % (6, 3) )
				fileHandle.close()
				
				'''
				# Get the deadlinecommand executable (we try to use the full path on OSX).
				deadlineCommand = "deadlinecommand"
				if os.path.exists( "/Applications/Deadline/Resources/bin/deadlinecommand" ):
					deadlineCommand = "/Applications/Deadline/Resources/bin/deadlinecommand"
		
				# Submit the job to Deadline
				args = "\"" + jobInfoFile + "\" \"" + pluginInfoFile + "\""
				os.popen( deadlineCommand + " " + args)
				'''
				ClientUtils.ExecuteCommand ( ( jobInfoFile , pluginInfoFile ) )
