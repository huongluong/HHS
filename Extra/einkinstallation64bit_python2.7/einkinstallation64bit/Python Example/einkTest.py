"""
Demo program for the E Ink library. If Pillow is installed it will display an image on the screen.
If it is not installed it will display four boxes.
"""

from eink import *
noPIL = False
try:
	from PIL import Image
except:
	noPIL = True

Sys_info = SystemInfo()

IT8951_Cmd_SysInfo(Sys_info)

gulPanelW = Sys_info.uiWidth
gulPanelH = Sys_info.uiHeight

# initialize
IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 0, (Sys_info.uiImageBufBase), 1)

# set full white
srcW = "\xFF" * (gulPanelW*gulPanelH)
IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

if noPIL:
	# partial load(200x200, 4 times) & display(400x400)
	src = "\xFF" * (200*200)
	IT8951_Cmd_LoadImageArea(src, (Sys_info.uiImageBufBase), 0, 0, 200, 200, gulPanelW, gulPanelH)
	
	src = "\x00" * (200*200)
	IT8951_Cmd_LoadImageArea(src, (Sys_info.uiImageBufBase), 200, 200, 200, 200, gulPanelW, gulPanelH)
	
	src = "\x30" * (200*200)
	IT8951_Cmd_LoadImageArea(src, (Sys_info.uiImageBufBase), 0, 200, 200, 200, gulPanelW, gulPanelH)
	
	src = "\x80" * (200*200)
	IT8951_Cmd_LoadImageArea(src, (Sys_info.uiImageBufBase), 200, 0, 200, 200, gulPanelW, gulPanelH)
	
	IT8951_Cmd_DisplayArea(0, 0, 400, 400, 2, (Sys_info.uiImageBufBase), 1)
else:
	# open image and convert to image compatible with device
	im = Image.open("UPCA_1D.bmp") # Replace with greyscale image you would like to load onto the display
	imstr = im.tobytes()
	# load in image
	IT8951_Cmd_LoadImageArea(imstr, (Sys_info.uiImageBufBase), 0, 0, im.width, im.height, gulPanelW, gulPanelH)

	# display loaded image
	IT8951_Cmd_DisplayArea(0, 0, im.width, im.height, 2, (Sys_info.uiImageBufBase), 1)

IT8951_CloseDevice()