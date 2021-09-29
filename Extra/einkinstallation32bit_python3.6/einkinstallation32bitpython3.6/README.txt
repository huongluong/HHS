eink 32-bit C/C++ library with Python 3.6 wrapper module.

Please contact Ryan Case (ryan.case@datalogic.com) with any questions.

---------------

INSTALLATION

This software requires you to have a 32-bit version of Python installed (a 64-bit version of this software is not available at this time). 
You must have pip installed for this version of Python, and this version of Python must be accessible from your system path
(you can test the latter requirement by entering "python" in your command line and checking that information about the correct version of Python is displayed).

To install dlsdk run the install.bat script from the command line. To uninstall run the uninstall.bat script. 

If you would like to install the driver with a version of Python other than the one that is used when you call 'python' in the command line, 
you can run the install.bat or uninstall.bat scripts from the command line with an argument specifying what Python launcher you would like to use.
Example:
install.bat py -3.6-32
uninstall.bat py -3.6-32

--------------

EINK FUNCTIONS

SystemInfo()
'''
	Initialize SystemInfo object.

	Properties:
	uiStandardCmdNo (int): Standard command number2T-con Communication Protocol
	uiExtendCmdNo (int): Extend command number
	uiSignature (int): 31 35 39 38h (I think this is the signature for the IT8951)
	uiVersion (int): command table version
	uiWidth (int): Panel Width
	uiHeight (int):	Panel Height
	uiUpdateBufBase (int): Update Buffer Address
	uiImageBufBase (int): Image Buffer Address
	uiTemperatureNo (int): Temperature segment number
	uiModeNo (int): Display mode number
	uiFrameCount (SwigPyObject): Frame count for each mode
	uiNumImgBuf (int): Number of image buffer
	uiWbfSFIAddr (int): not sure what this is
	uiReserved (SwigPyObject): not sure what this is
	lpCmdInfoDatas (SwigPyObject): command table pointer
'''


IT8951_Cmd_SysInfo(Sys_info)
'''
	Set system information based on device and establish connection with device. Must be paired with a call to IT8951_CloseDevice when you are finished with the E Ink device.

	Parameters:
	Sys_info (SystemInfo): System info object
'''

IT8951_Cmd_LoadImageArea(srcImg, memAddr, ldX, ldY, ldW, ldH, gulPanelW, gulPanelH)
'''
	Load image image into device.

	Parameters:
	srcImg (str): byte representation of image
	memAddr (int): Image Buffer Address (get from SystemInfo object)
	ldX (int): x coordinate (in pixels) of top left corner of area to load
	ldY (int): y coordinate (in pixels) of top left corner of area to load
	ldW (int): width in pixels of area to load
	ldH (int): height in pixels of area to load
	gulPanelW (int): width in pixels of display (can get from SystemInfo object)
	gulPanelH (int): height in pixels of display (can get from SystemInfo object)
'''

IT8951_Cmd_DisplayArea(dpyX, dpyY, dpyW, dpyH, dpyMode, memAddr, enWaitRdy)
'''
	Display specified area on E Ink screen.

	Parameters:
	dpyX (int): x coordinate (in pixels) of top left corner of area to display
	dpyY (int): y coordinate (in pixels) of top left corner of area to display
	dpyW (int): width in pixels of area to display
	dpyH (int): height in pixels of area to display
	dpyMode (int): type of update the controller will perform
				   1 will only update pixels that have changed
				   2 is for flashing updates (to clear out ghosting)
	memAddr(int): Image Buffer Address (get from SystemInfo object)
	enWaitRdy(int): ensure that current display command will be finished before allowing next command
'''

IT8951_CloseDevice()
'''
	Close connection with E Ink device. Should be called for each call to IT8951_Cmd_SysInfo
'''
