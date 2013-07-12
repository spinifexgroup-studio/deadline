import nuke
import os
import sys

'''
Usage: NUKE replaceWritePaths.py <nuke_script> <new_nuke_script> <read_path> <write_path> <first_frame> <last_frame> .....'
'''
# Set Variables
print sys.argv
inScript = sys.argv[1]
outScript = sys.argv[2]
inPath = sys.argv[3]
outPath = sys.argv[4]
format = sys.argv[5]
firstFrame = int ( sys.argv[6] )
lastFrame = int ( sys.argv[7] )
reformatScale = float ( sys.argv[8] )
fps = float ( sys.argv[9] )

# Open Script
nuke.scriptOpen( inScript )
    

# Replace Read Node Data
node = nuke.toNode('inputSequence')
node.knob('file').setValue(inPath)
node.knob('first').setValue(firstFrame)
node.knob('last').setValue(lastFrame)
node.knob('origfirst').setValue(firstFrame)
node.knob('origlast').setValue(lastFrame)

# Change Resolution
node = nuke.toNode('scaleDown')
node.knob('scale').setValue(reformatScale)

# Set Write Path
allNodes = nuke.allNodes()
for node in allNodes:
	if node.Class() == 'Write':
		node['disable'].setValue(True)
		node.knob('file').setValue(outPath)

# Undisable the write node of the format we are using
node = nuke.toNode('outputSameAsInput')
if format == 'EXR':
	node = nuke.toNode('outputEXR')
if format == 'TGA':
	node = nuke.toNode('outputTGA')
if format == 'JPG':
	node = nuke.toNode('outputJPG')
if format == 'ProRes 444':
	node = nuke.toNode('outputProRes')
	node.knob('fps').setValue(fps)
node['disable'].setValue(False)

# Save Script
nuke.scriptSave( outScript )