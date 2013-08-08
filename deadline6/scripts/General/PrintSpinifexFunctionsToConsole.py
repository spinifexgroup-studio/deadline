'''
test job script
'''


from System.IO import *
from System.Text import *


from Deadline.Scripting import *
from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

from datetime import date

import os
import shutil
import ConfigParser
import time
import threading
import Spinifex

########################################################################
## Globals
########################################################################

 
		

########################################################################
## Main Function Called By Deadline
########################################################################

def __main__():

	reload(Spinifex)

	# Get list of jobs
	jobs = JobUtils.GetSelectedJobs()
	numJobs = len( jobs )
	
	# Iterate through selected jobs
	for i in range( 0, numJobs ):
		job = jobs [i]
		outputDirectories = job.JobOutputDirectories
		outputFilenames = job.JobOutputFileNames
		
		# Iterate thrugh renders in job
		for j in range ( 0, len (outputDirectories) ):
			dir = outputDirectories[j]
			Spinifex.GetStudioRoot ( dir )
			
			print ("Parent Directory is: %s" % Spinifex.GetParentDir( dir ) )
			print ("Dated Directory is: %s" % Spinifex.AppendDateToPathWithVersion( dir, '.mov' ) )
			
