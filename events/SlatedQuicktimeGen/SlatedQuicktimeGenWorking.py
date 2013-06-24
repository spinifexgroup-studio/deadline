nukeSourceFile = "/Volumes/RESOURCES/05_Motion_Studio_Tools/deadline/event_plugins/SlatedQuicktimeGen/nuke/slate_v001.nk"
nukeDestFile = "/Volumes/DeadlineRepository/temp/slate_v001_submit.nk"

sourceHandle = open ( nukeSourceFile, "r" )

destHandle = open( nukeDestFile, "w" )
for line in sourceHandle:
	if "_Project_" in line:
		line = line.replace ("_Project_", "_Replace_")
	if "_Sequence_" in line:
		line = line.replace ("_Sequence_", "_Replace_")
	if "_Shot_" in line:
		line = line.replace ("_Shot_", "_Replace_")
	if "_Frames_" in line:
		line = line.replace ("_Frames_", "_Replace_")
	if "_Date_" in line:
		line = line.replace ("_Date_", "_Replace_")
	if "_Version_" in line:
		line = line.replace ("_Version_", "_Replace_")
	if "_Source_" in line:
		line = line.replace ("_Source_", "_Replace_")
	if "_Comments_" in line:
		line = line.replace ("_Comments_", "_Replace_")
	if "_fileDestination_" in line:
		line = line.replace ("_fileDestination_", "_Replace_")
	destHandle.write ( line )



destHandle.write ( str(sourceHandle) )
destHandle.close()
sourceHandle.close()
