import nuke
import os
import sys

'''
Usage: NUKE replaceWritePaths.py <nuke_script> <new_nuke_script> <read_path> <write_path> <first_frame> <last_frame> .....'
'''
# Set Variables
inScript = sys.argv[1]
outScript = sys.argv[2]
inPath = sys.argv[3]
outPath = sys.argv[4]
fontPath = sys.argv[5]
firstFrame = int ( sys.argv[6] )
lastFrame = int ( sys.argv[7] )
reformatScale = float ( sys.argv[8] )
fps = float ( sys.argv[9] )
codec = sys.argv[10]
isSlateVisible = sys.argv[11]

# Open Script
nuke.scriptOpen( inScript )

# Set Font File
for n in nuke.allNodes():
    if n.Class() == 'Text':
        n.knob('font').setValue(fontPath)
    

# Replace Read Node Data
readNode = nuke.toNode('inputSequence')
readNode.knob('file').setValue(inPath)
readNode.knob('first').setValue(firstFrame)
readNode.knob('last').setValue(lastFrame)
readNode.knob('origfirst').setValue(firstFrame)
readNode.knob('origlast').setValue(lastFrame)

# Change Resolution
scaleNode = nuke.toNode('scaleDown')
scaleNode.knob('scale').setValue(reformatScale)

# Change Write Node
writeNode = nuke.toNode('outputMovie')
writeNode.knob('file').setValue(outPath)
if codec == 'Animation':
	writeNode.knob('codec').setValue('rle ')
	writeNode.knob('settings').setValue('0000000000000000000000000000019a7365616e0000000100000001000000000000018676696465000000010000000e00000000000000227370746c000000010000000000000000726c6520000000000020000003ff000000207470726c000000010000000000000000000003ff001e000000000001000000246472617400000001000000000000000000000000000000530000010000000100000000156d70736f00000001000000000000000000000000186d66726100000001000000000000000000000000000000187073667200000001000000000000000000000000000000156266726100000001000000000000000000000000166d70657300000001000000000000000000000000002868617264000000010000000000000000000000000000000000000000000000000000000000000016656e647300000001000000000000000000000000001663666c67000000010000000000000000004400000018636d66720000000100000000000000006170706c00000014636c75740000000100000000000000000000001c766572730000000100000000000000000003001c00010000')
	writeNode.knob('keyframerate').setValue(1)
if codec == 'H264':
	writeNode.knob('codec').setValue('avc1')
	writeNode.knob('settings').setValue('0000000000000000000000000000019a7365616e0000000100000001000000000000018676696465000000010000000e00000000000000227370746c00000001000000000000000061766331000000000018000003ff000000207470726c000000010000000000000000000003ff001e000000000019000000246472617400000001000000000000000000000000000000530000010000000100000000156d70736f00000001000000000000000000000000186d66726100000001000000000000000000000000000000187073667200000001000000000000000000000000000000156266726100000001000000000000000000000000166d70657300000001000000000000000000000000002868617264000000010000000000000000000000000000000000000000000000000000000000000016656e647300000001000000000000000000000000001663666c67000000010000000000000000004400000018636d66720000000100000000000000006170706c00000014636c75740000000100000000000000000000001c766572730000000100000000000000000003001c00010000')
	writeNode.knob('keyframerate').setValue(fps)
if codec == 'ProRes 422':
	writeNode.knob('codec').setValue('apcn')
	writeNode.knob('settings').setValue('000000000000000000000000000001cc7365616e000000010000000100000000000001b876696465000000010000000f00000000000000227370746c0000000100000000000000006170636e000000000018000003ff000000207470726c00000001000000000000000000000000001e000000000000000000246472617400000001000000000000000000000000000000530000010000000100000000156d70736f00000001000000000000000000000000186d66726100000001000000000000000000000000000000187073667200000001000000000000000000000000000000156266726100000001000000000000000000000000166d70657300000001000000000000000000000000002868617264000000010000000000000000000000000000000000000000000000000000000000000016656e647300000001000000000000000000000000001663666c67000000010000000000000000004400000018636d66720000000100000000000000006170706c00000014636c75740000000100000000000000000000003263646563000000010000000000000000696370746e636c630002000200020100000000010000000100010000ff010000001c766572730000000100000000000000000003001c00010000')
writeNode.knob('fps').setValue(fps)

# Change Slate Switch
slateSwitch = nuke.toNode('slateSwitch')
if isSlateVisible == 'True':
	slateSwitch.knob('which').setValue(True)
else:
	slateSwitch.knob('which').setValue(False)

# Save Script
nuke.scriptSave( outScript )