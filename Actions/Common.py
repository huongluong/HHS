import win32api
import os
import sys

# get harddrive
#drives = win32api.GetLogicalDriveStrings()
#drives = drives.split("\x00")

# Initilize working path
workingpath = "C:\\"

# get working path folder
#for drive in drives:
#    listfilesandfolders = os.listdir(drive)
#    workingfolderflag = [x for x in listfilesandfolders if x == "Keyboard"]
#    if len(workingfolderflag) > 0:
#        workingpath = drive + workingfolderflag[0] + "\\"
#        break

# get working folder
workingfolder = workingpath + "HHS\\"

# set working folder
globaldict = {'workingfolder': workingfolder
             ,'logfolder': workingfolder + "Logs\\"
             ,'screenshotfolder': workingfolder + "Logs\\Screenshot\\"
             ,'dbfile': workingfolder + "Data\\TestOCR_LabelID.xls"
             ,'readlbtimeout': 25.0
             ,'resettimeout': 5.0
             ,'revAlabel': workingfolder + 'Data\\RevA.png'
             ,'displayflag': 'pc'
             ,'ocrfolder' : workingfolder + 'Labels\\OCR\\Tmp\\'
             ,'stoptransmitdatatimeout': 5.0}
globals().update(globaldict)

if globals()['displayflag'].upper() != "PC":
    globals()['sampleimage'] = workingfolder + "Labels\\Resize\\Common\\ascii127_sample.png"
    globals()['bcoutputfolder'] = workingfolder + "Labels\\Resize\\Labelsets\\"
    globals()['negativefolder'] = workingfolder + "Labels\\Resize\\NegativeLabels\\"
    globals()['settingfolder'] = workingfolder + "Labels\\Resize\\Settings\\"
    globals()['revAlabel'] = workingfolder + 'Labels\\Resize\\Common\\RevA.png'
    globals()['labelcountryext'] = ".png"
    
