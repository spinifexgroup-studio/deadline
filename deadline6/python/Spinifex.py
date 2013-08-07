'''
Spinifex helper functions

TODO:
- fix 2.15GB bug
- add status bar when submitting
'''

import os


########################################################################
## Helper Functions
########################################################################

def GetStudioRoot ( directory ):
	print ( "Input Directory is: %s" % directory )
	
	# Make directory UNC friendly and split into array
	directory = directory.replace("\\","/")
	directorySplit = directory.split('/')
	
	# Get first item of directory array and prep whether using mac or PC
	studioDirectory = ''
	if directorySplit[1] == '':
		studioDirectory = '/'
		directorySplit.pop(0)
		directorySplit.pop(0)
	else:
		if directorySplit[0] == '':
			directorySplit.pop(0)
			studioDirectory = ''
		else:
			studioDirectory = directorySplit.pop(0)
	
	# Start stripping the array until we get to the 2D or 3D folder	
	while len(directorySplit) > 0:
		popItem = directorySplit.pop()
		if popItem == '2D' or popItem == '3D':
			for pathItem in directorySplit:
				studioDirectory = ("%s/%s" % (studioDirectory,pathItem))
			break
	else:
		studioDirectory = directory
			
	print ( "Studio Directory is: %s" % studioDirectory )
	return studioDirectory
	
	
def GetParentDir (directory):
	return os.path.abspath(os.path.join(directory, os.pardir))