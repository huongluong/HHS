# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import os
import logging
import sys, re
import time

from eink import *
sys.path.append('C:\\HHS\\Actions')
# import DBv2
import Clipboard
import KeyUtil
import Process
import datetime
import GUI
import ext
import random
import string
import wx    # pip install -U wxPython
import Common
import shutil
import ctypes
from PIL import Image
from xlrd.timemachine import xrange
#from eink import *
#from PIL import Image

#####################################
def StartProgram(programname):
    try:
        os.startfile(programname)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
        
def CaptureScreen(screenshotpath="C:\\Temp.png", xsrc=0, ysrc=0, w=500, h=500):
    try:
        app = wx.App(False)
        s = wx.ScreenDC()
        b = wx.Bitmap(w, h)
        m = wx.MemoryDCFromDC(s)
        m.SelectObject(b)
        m.Blit(0, 0, w, h, s, xsrc, ysrc)
        m.SelectObject(wx.NullBitmap)
        b.SaveFile(screenshotpath, wx.BITMAP_TYPE_PNG)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)    
        
def CreateRandomString():
    randomstring = ""
    try:
        # get date and time
        currentdatetime = datetime.datetime.now()
        randomstring = str(currentdatetime).replace(":", "").replace(" ", "").replace("-", "").replace(".", "")
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return randomstring

# create xml language
def CreateLanguageXML(workingfolder="C:\\Keyboard\\CountryMode\\Data\\",strlanguageID="0409:00000409"):
    # open template
    f = open(workingfolder + "Data\\Template.txt", 'r')
    lines = f.readlines()
    f.close()

    # join to string
    strlines = "".join(lines)

    # get current ID
    currentID = strlines[strlines.find(" ID") + 5: strlines.find("Default") - 2]

    # replace to a new id
    newstrlines = strlines.replace(currentID, strlanguageID)

    # write to a new file
    f = open(workingfolder + "Data\\language.xml","w")
    f.write(newstrlines)
    f.close()
    
# create txt language for windowXP
def CreateLanguageTXT(workingfolder="C:\\Keyboard\\CountryMode\\Data\\",strlanguageID="0409:00000409", languagegroup="2"):
    # open template
    f = open(workingfolder + "Data\\locale.txt", 'w')
    
    # write header
    f.write("[RegionalSettings]\n")
    
    # write content
    # get 4 chars in language string
    inputid = strlanguageID[0:4]
    f.write("Language=" + inputid + "\n")
    f.write("LanguageGroup=" + str(languagegroup) + "\n")
    f.write("SystemLocale=" + inputid + "\n")
    f.write("UserLocale=" + inputid + "\n")
    f.write("InputLocale=" + strlanguageID + "\n")
    f.write("UserLocale_DefaultUser=" + strlanguageID + "\n")
    f.write("InputLocale_DefaultUser=" + strlanguageID + "\n")   

    # close file
    f.close()


def OpenImage(imagefilepath):
    try:        
        os.startfile(imagefilepath)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def CloseImage(imagefilepath):
    try:
        # kill image by its window title
        # some image paths contain / and some contain \\
        # replace all \\ to /
        imagefilepath = imagefilepath.replace("\\", "/")
        
        # get image name
        tmp = imagefilepath.split('/')
        imgname = tmp[len(tmp) - 1]
        Process.Process().KillProcessByWindowTitle(imgname)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def SelectAndCopyClipboard():
    result = ""    
   
    # clear clipboard
    Clipboard.Clipboard().ClearClipboard()
    time.sleep(0.5)
    
    # use for winword and notpad
    # back to home
    KeyUtil.KeyUtil().BackHome()
    time.sleep(0.5)
           
    # select all
    KeyUtil.KeyUtil().SelectAll2()
    time.sleep(0.5)
        
    # copy
    KeyUtil.KeyUtil().Copy2()
    time.sleep(0.5)
    
    # copy data and get clipboard
    result = Clipboard.Clipboard().GetClipboard()
    time.sleep(0.5)
    
    # copy clipboard again by ctrl + a/crtl + c to make sure data was got
    if len(result) == 0:
        # press ctrl+a again
        KeyUtil.KeyUtil().SelectAll()
        time.sleep(0.5)
        
        # copy ctrl + c
        KeyUtil.KeyUtil().Copy()
        time.sleep(0.5)
        
        # copy data and get clipboard
        result = Clipboard.Clipboard().GetClipboard()
        time.sleep(0.5)        
         
    
    # In case select all is slow
    # make sure data was received
    #i = 1
    #while len(result) == 0 and i <= 20:
        #time.sleep(1.0)
        #KeyUtil.KeyUtil().Copy2()
        #result = Clipboard.Clipboard().GetClipboard()
        #i = i + 1
    
    # clear clipboard
    Clipboard.Clipboard().ClearClipboard()            
           
    # wait a bit for another loop
    time.sleep(0.5)

    return result

def GetCapNumState():
    capnumstatedict = {}
    try:
        # get caplock state
        caplockstate = KeyUtil.KeyUtil().IsCapsLockOn()
        
        # get numlock state
        numlockstate = KeyUtil.KeyUtil().IsNumLockOn()
        capnumstatedict = {"Caplock": caplockstate, "Numlock": numlockstate}
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return capnumstatedict
        
def SetCapNumState(capnumstatedict):
    try:
        capstate = capnumstatedict["Caplock"]  
        numstate = capnumstatedict["Numlock"]
        KeyUtil.KeyUtil().SetCaplock(capstate)
        time.sleep(0.5)
        
        KeyUtil.KeyUtil().SetNumlock(numstate)
        time.sleep(0.5)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
        
def WaitAndFocusWindow(windowtitle, waitingtimeout=1.0):
    try:
        if waitingtimeout > 0:
            time.sleep(waitingtimeout)
        GUI.Window(windowtitle).BringToFront(3.0)        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def ClearEink():
    Sys_info = SystemInfo()

    IT8951_Cmd_SysInfo(Sys_info)

    gulPanelW = Sys_info.uiWidth
    gulPanelH = Sys_info.uiHeight

    # initialize
    IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

    # set full white
    srcW = b"\xFF" * (gulPanelW*gulPanelH)
    IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
    IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)


def LoadAndDisplayImageOnEink(imagefilepath=None):
    try: 
        Sys_info = SystemInfo()
        IT8951_Cmd_SysInfo(Sys_info)

        gulPanelW = Sys_info.uiWidth
        gulPanelH = Sys_info.uiHeight

        # initialize
        IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

        # set full white
        srcW = "\xFF" * (gulPanelW*gulPanelH)
        IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
        IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

        # open image and convert to image compatible with device
        im = Image.open(imagefilepath) # Replace with greyscale image you would like to load onto the display
        imstr = im.tobytes()
        
        # load in image
        # [Nam Nguyen, 18-Oct-2019] Currently use coordinate 600, 300.
        IT8951_Cmd_LoadImageArea(imstr, (Sys_info.uiImageBufBase), 600, 300, im.width, im.height, gulPanelW, gulPanelH)

        # display loaded image
        IT8951_Cmd_DisplayArea(600, 300, im.width, im.height, 2, (Sys_info.uiImageBufBase), 1)

        IT8951_CloseDevice()
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
def LoadOCRAndDisplayOCROnEink(imagefilepath=None):
    try:
        Sys_info = SystemInfo()
        IT8951_Cmd_SysInfo(Sys_info)

        gulPanelW = Sys_info.uiWidth
        gulPanelH = Sys_info.uiHeight

        # initialize
        IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 0, (Sys_info.uiImageBufBase), 1)

        # set full white
        srcW = b"\xFF" * (gulPanelW * gulPanelH)
        IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
        IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

        # open image and convert to image compatible with device
        im = Image.open(imagefilepath)  # Replace with greyscale image you would like to load onto the display
        imstr = im.tobytes()

        # load in image
        # [Nam Nguyen, 18-Oct-2019] Currently use coordinate 600, 300.
        IT8951_Cmd_LoadImageArea(imstr, (Sys_info.uiImageBufBase), 600,450 , im.width, im.height, gulPanelW, gulPanelH)

        # display loaded image
        IT8951_Cmd_DisplayArea(600, 450, im.width, im.height, 2, (Sys_info.uiImageBufBase), 1)

        IT8951_CloseDevice()
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def DisplayImage(exttype="pc", exthandleobj=None, imagefilepath=None, displaytimeout=5.0, resizeflag=False, resizeproperties="-filter LanczosSharp -background white -resize 600x800 -rotate 90 -gravity center -extent 600x800 -colorspace Gray -dither FloydSteinberg -quality 100 -define png:color-type=0 -define png:bit-depth=8"):
    # Nam Nguyen, 05-05-2017: added rezie
    destinationfilepath = ""
    if resizeflag:
        tmpfolder = Common.workingfolder + "Labels\\Tmp\\"
        
        # get image name
        if "/" in imagefilepath:
            imagename = imagefilepath[imagefilepath.rfind("/") + 1:]
        else:
            imagename = imagefilepath[imagefilepath.rfind("\\") + 1:]
        
        # move image file to tmp folder
        destinationfilepath = tmpfolder + imagename
        shutil.copy(imagefilepath, destinationfilepath)
        time.sleep(0.2)
        
        # start resize image
        cmdresize = "convert.exe " + destinationfilepath + " " + resizeproperties + " " + destinationfilepath
        os.system(cmdresize)        
        time.sleep(0.1)
        imagefilepath = destinationfilepath
    
    if exttype.upper() == "PC":
        # open label programming image file        
            OpenImage(imagefilepath)

            # wait for image open and read
            time.sleep(displaytimeout)
        
            # close label programming
            CloseImage(imagefilepath)
    # [Nam Nguyen, 18-Oct-2019]: Add eink device, need to install eink driver first
    elif exttype.upper() in ["KINDLE", "EPD"]:
        
        # use kindle or epd
        ext.Ext(exttype).uploadImage(imagefilepath)
        
        # clear external device: epd or kindle
        ext.Ext(exttype).clearScreen(exthandleobj, 1)
        
        # display label 
        if "/" in imagefilepath:
            imagename = imagefilepath[imagefilepath.rfind("/") + 1:]
        else:
            imagename = imagefilepath[imagefilepath.rfind("\\") + 1:]
        
        ext.Ext(exttype).displayImage(exthandleobj, imagename)
            
        # wait for scanner read
        time.sleep(displaytimeout)
            
        # clear external device again
        ext.Ext(exttype).clearScreen(exthandleobj, 1)
        time.sleep(0.2)
            
        # delete image
        ext.Ext(exttype).deleteImage(exthandleobj, imagename)
        time.sleep(0.1)

    # Use eink
    elif exttype.upper() == "EINK":
        # clear, display and load image
        LoadAndDisplayImageOnEink(imagefilepath)
        
        # wait for scanner read
        time.sleep(displaytimeout)
        
        # Clear eink
        ClearEink()
        
    
    # remove resize image
    if len(destinationfilepath) > 0 and os.path.exists(destinationfilepath):
        os.remove(destinationfilepath)
        
def CreateOCRPassportText(pptype="", country="", lastname="", firstname="", addname="", ppnum="", dob="", sex="", expdate="", personalnum=""):
    passportcontent = []
    try:
        countrylist = ['AFG', 'ALB', 'DZA', 'ASM', 'AND', 'AUT', 'AGO', 'AIA', 'ATA', 'ATG', 'ARG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN', 'BOL', 'BIH', 'BWA', 'BVT', 'BRA', 'IOT', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR', 'CAN', 'CPV', 'CYM', 'CHL', 'CHN', 'CXR', 'CCK', 'COL', 'COM', 'COK', 'CRI', 'CIV', 'HRV', 'CUB', 'CYP', 'CZE', 'PRK', 'COD', 'DNK', 'DJI', 'DMA', 'DOM', 'TMP', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'ETH', 'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'FXX', 'GUF', 'PYF', 'GAB', 'GMB', 'GEO', 'D', 'GHA', 'GIB', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GIN', 'GNB', 'GUY', 'HTI', 'HMD', 'VAT', 'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 'ISR', 'ITA', 'JAM', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LIE', 'LTU', 'LUX', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MHL', 'MTQ', 'MRT', 'MUS', 'MYT', 'MEX', 'FSM', 'MCO', 'MNG', 'MSR', 'MAR', 'MOZ', 'MMR', 'NAM', 'NRU', 'NPL', 'NLD', 'ANT', 'NTZ', 'NCL', 'NZL', 'NIC', 'NER', 'NGA', 'NIU', 'NFK', 'MNP', 'NOR', 'OMN', 'PAK', 'PLW', 'PAN', 'PNG', 'PRY', 'PER', 'PHL', 'PCN', 'POL', 'PRT', 'PRI', 'QAT', 'KOR', 'MDA', 'REU', 'ROM', 'RUS', 'RWA', 'SHN', 'KNA', 'LCA', 'SPM', 'VCT', 'WSM', 'SMR', 'STP', 'SAU', 'SEN', 'SYC', 'SLE', 'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SGS', 'ESP', 'LKA', 'SDN', 'SUR', 'SJM', 'SWZ', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'THA', 'MKD', 'TGO', 'TKL', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'TCA', 'TUV', 'UGA', 'UKR', 'ARE', 'GBR', 'GBD', 'GBN', 'GBO', 'GBP', 'GBS', 'TZA', 'USA', 'UMI', 'URY', 'UZB', 'VUT', 'VEN', 'VNM', 'VGB', 'VIR', 'WLF', 'ESH', 'YEM', 'ZAR', 'ZMB', 'ZWE', 'UNO', 'UNA', 'XXA', 'XXB', 'XXC', 'XXX']
        
        # get passport type
        tmppptype = "<"
        if len(pptype) == 1:
            tmppptype = pptype
        
        # get country name
        tmpcountry = ""
        if len(country) > 0 and country.upper() != "RANDOM" and country.upper() in countrylist:
            tmpcountry = country
        elif country.upper() == "RANDOM":
            tmpcountry = random.choice(countrylist)
        
        tmpcountry = tmpcountry + ''.join("<" for _ in range(3-len(tmpcountry)))
        
        # get last name
        tmplastname = ""
        if (len(lastname) > 0 and lastname.upper() != "RANDOM"):
            tmplastname = lastname
        elif lastname.upper() == "RANDOM":
            tmplastname = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
            
        # get first name
        tmpfirstname = ""
        if (len(firstname) > 0 and firstname.upper() != "RANDOM"):
            tmpfirstname = firstname
        elif firstname.upper() == "RANDOM":
            tmpfirstname = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
      
        # get additional name
        tmpaddname = ""
        if (len(addname) > 0 and addname.upper() != "RANDOM"):
            tmpaddname = addname
        elif addname.upper() == "RANDOM":
            tmpaddname = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
            
        # get passport line 1 content
        ppl1p1 = "P" + tmppptype + tmpcountry + tmplastname + "<<" + tmpfirstname + "<" + tmpaddname
        ppl1p2 = ''.join("<" for _ in range(44-len(ppl1p1)))
        ppl1content = ppl1p1 + ppl1p2
        
        ####### PASSPORT LINE 2 ###########
        # get passport number
        tmpppnum = ""
        if (len(ppnum) > 0 and ppnum.upper() != "RANDOM"):
            tmpppnum = ppnum
        elif ppnum.upper() == "RANDOM":
            #tmpppnum = 'B' + ''.join(random.choice(string.digits) for _ in range(7))
            tmpppnum = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
            
        # passport number needs 9 digits
        if len(tmpppnum) < 9:
            tmpppnum = tmpppnum + ''.join("<" for _ in range(9-len(tmpppnum)))
        
        # calculate check digit index 10
        w = [7, 3, 1]
        tmpw = [[x for x in w] for i in xrange(13)]
        weightlist = sum(tmpw, [])
        charsmapping = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '<': 0, 'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35}
        listtmpnumvalue = [int(charsmapping[str(x)]) for x in list(tmpppnum)]
        sumppnumvalueandweight = sum([listtmpnumvalue[i]*weightlist[i] for i in range(len(listtmpnumvalue))])
        chkdigitindx10 = divmod(sumppnumvalueandweight, 10)[1]
        
        # get dob
        tmpdob = ""
        if (len(dob) > 0 and dob.upper() != "RANDOM"):
            tmpdob = dob
        elif dob.upper() == "RANDOM":
            year = random.randint(1930, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            tmpdob = str(year)[-2:] + str(month).zfill(2) + str(day).zfill(2)

        tmpdob = tmpdob + ''.join("<" for _ in range(6-len(tmpdob)))
        
        # get check digit index 20
        listdobvalue = [int(charsmapping[str(x)]) for x in list(tmpdob)]
        sumdobvalueandweight = sum([listdobvalue[i]*weightlist[i] for i in range(len(listdobvalue))])
        chkdigitindx20 = divmod(sumdobvalueandweight, 10)[1]
        
        # get sex
        tmpsex = ""
        sexlist = ['M', 'F', '<']
        if len(sex) > 0 and sex.upper() != "RANDOM" and sex.upper() in sexlist:
            tmpsex = sex
        elif sex.upper() == "RANDOM":
            tmpsex = random.choice(sexlist)
            
        tmpsex = tmpsex + ''.join("<" for _ in range(1-len(tmpsex)))
            
        # get expiration date
        tmpexpdate = ""
        if (len(expdate) > 0 and expdate.upper() != "RANDOM"):
            tmpexpdate = expdate
        elif expdate.upper() == "RANDOM":
            now = datetime.datetime.now()            
            year = random.randint(now.year, now.year + 10)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            tmpexpdate = str(year)[-2:] + str(month).zfill(2) + str(day).zfill(2)
            
        tmpexpdate = tmpexpdate + ''.join("<" for _ in range(6-len(tmpexpdate)))
        # get check digit index 28
        listexpdatevalue = [int(charsmapping[str(x)]) for x in list(tmpexpdate)]
        sumexpdatevalueandweight = sum([listexpdatevalue[i]*weightlist[i] for i in range(len(listexpdatevalue))])
        chkdigitindx28 = divmod(sumexpdatevalueandweight, 10)[1]
        
        # get personal number
        tmppersonalnum = ""
        if (len(personalnum) > 0 and personalnum.upper() != "RANDOM"):
            tmppersonalnum = personalnum
        elif personalnum.upper() == "RANDOM":
            tmppersonalnum = ''.join(random.choice(string.digits) for _ in range(9))

        if len(tmppersonalnum) < 14:
            tmppersonalnum = tmppersonalnum + ''.join("<" for _ in range(14-len(tmppersonalnum)))
        
        # calculate check digit index 43
        listpersonalnum = [int(charsmapping[str(x)]) for x in list(tmppersonalnum)]
        sumpersonalnumvalueandweight = sum([listpersonalnum[i]*weightlist[i] for i in range(len(listpersonalnum))])
        chkdigitindx43 = divmod(sumpersonalnumvalueandweight, 10)[1]
        
        # calculate check digit index 44
        contentwithcheckdigit = tmpppnum + str(chkdigitindx10) + tmpdob + str(chkdigitindx20) + tmpexpdate + str(chkdigitindx28) + tmppersonalnum + str(chkdigitindx43)
        listcontentwcheckvalue = [int(charsmapping[str(x)]) for x in list(contentwithcheckdigit)]
        sumcontentwcheckvalueandweight = sum([listcontentwcheckvalue[i]*weightlist[i] for i in range(len(listcontentwcheckvalue))])
        chkdigitindx44 = divmod(sumcontentwcheckvalueandweight, 10)[1]
        
        # get content passport line 2
        ppl2content = tmpppnum + str(chkdigitindx10) + tmpcountry + tmpdob + str(chkdigitindx20) + tmpsex + tmpexpdate + str(chkdigitindx28) + tmppersonalnum + str(chkdigitindx43) + str(chkdigitindx44)
        
        # return passport 2 lines
        passportcontent = [ppl1content, ppl2content]
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)    
    return passportcontent


def CreateOCRPostalText(postaltype="", ccleading0="", clientcode="", aieleading0="", amountineuro="", acleading0="", accountnumber="", additionalchar=False):
    postalcontent = []
    try:
        postaltext = ""
        # get postaltype
        listpostaltype = ["674", "451", "896", "247"]
        tmppostaltype = "451"
        if len(postaltype) > 0 and postaltype.upper() != "RANDOM" and postaltype in listpostaltype:
            tmppostaltype = postaltype
        elif postaltype.upper() == "RANDOM":
            tmppostaltype = random.choice(listpostaltype)
        
        leading0valuelist = ["Yes", "No"]
        
        # get client code
        tmpclientcode = ""
        if tmppostaltype in ["674", "896", "247"]:
            if len(clientcode) == 18:
                tmpclientcode = clientcode
            elif len(clientcode) > 0 and len(clientcode) <= 16 and clientcode.upper() != "RANDOM":
                tmpclientcode = clientcode.zfill(16) + str(divmod(int(clientcode), 93)[1])
            elif clientcode.upper() == "RANDOM":
                
                # get leading 0
                tmccleading0 = "Yes"
                if len(ccleading0) > 0 and ccleading0.upper() != "RANDOM":
                    tmccleading0 = ccleading0
                if ccleading0.upper() == "RANDOM":
                    tmccleading0 = random.choice(leading0valuelist)
                
                randomclientcode = ""
                randomclientcodelen = 16
                if tmccleading0.upper() == "YES":
                    randomclientcodelen = random.randint(1, 15)
                
                randomclientcode = ''.join(random.choice(string.digits) for _ in range(randomclientcodelen))
                randomclientcode = randomclientcode.zfill(16)
                tmpclientcode = randomclientcode + str(divmod(int(randomclientcode), 93)[1])
                
        # get amount in Euro       
        tmpamountineuro = ""
        if tmppostaltype in ["896", "247"]:
            if len(amountineuro) == 11:
                tmpamountineuro = amountineuro
            elif len(amountineuro) > 0 and len(amountineuro) < 11 and amountineuro.upper() != "RANDOM":
                tmpamountineuro = amountineuro.zfill(11)
            elif amountineuro.upper() == "RANDOM":
                
                # get leading 0
                tmpaieleading0 = "Yes"
                if len(aieleading0) > 0 and aieleading0.upper() != "RANDOM":
                    tmpaieleading0 = aieleading0
                if aieleading0.upper() == "RANDOM":
                    tmpaieleading0 = random.choice(leading0valuelist)
                
                randomaielenp1 = 8
                randomaiep1 = ""
                randomaiep2 = ""
                if tmpaieleading0.upper() == "YES":
                    randomaielenp1 = random.randint(1, 7)
                
                randomaiep1 = ''.join(random.choice(string.digits) for _ in range(randomaielenp1))
                randomaiep1 = randomaiep1.zfill(8)
                randomaiep2 = ''.join(random.choice(string.digits) for _ in range(2))
                tmpamountineuro = randomaiep1 + "+" + randomaiep2
        
        # get account number
        tmpaccountnumber = ""
        if len(accountnumber) > 0 and accountnumber.upper() != "RANDOM":
            tmpaccountnumber = accountnumber
        if accountnumber.upper() == "RANDOM":
            randomaccountlen = 12
            
            # get leading 0
            tmpacleading0 = "Yes"
            if len(acleading0) > 0 and acleading0.upper() != "RANDOM":
                tmpacleading0 = acleading0
            if acleading0.upper() == "RANDOM":
                tmpacleading0 = random.choice(leading0valuelist)
                
            if tmpacleading0.upper() == "YES":
                randomaccountlen = random.randint(1, 11)
            
            tmpaccountnumber = ''.join(random.choice(string.digits) for _ in range(randomaccountlen))
            tmpaccountnumber = tmpaccountnumber.zfill(12)  
        
        if additionalchar == False:
            postaltext = tmpclientcode + tmpamountineuro + tmpaccountnumber + tmppostaltype
        else:
            if len(tmpclientcode) > 0:
                tmpclientcode = "<" + tmpclientcode + ">"
            if len(tmpamountineuro) > 0:
                tmpamountineuro = tmpamountineuro + ">"
            
            postaltext = tmpclientcode + "      " + tmpamountineuro + "  " + tmpaccountnumber + "<  " + tmppostaltype + ">"
        
        # get expect data after
        expectpostaldata = tmpclientcode + "      " + tmpamountineuro + "  " + tmpaccountnumber.zfill(12) + "<  " + tmppostaltype + ">"
        
        postalcontent = [postaltext, tmppostaltype, expectpostaldata]    
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)          
    return postalcontent

def getCurrentLanguageHex():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    # Made up of 0xAAABBBB, AAA = HKL (handle object) & BBBB = language ID
    klid = user32.GetKeyboardLayout(thread_id)

    # Language ID -> low 10 bits, Sub-language ID -> high 6 bits
    # Extract language ID from KLID
    lid = klid & (2**16 - 1)

    # Convert language ID from decimal to hexadecimal
    lid_hex = hex(lid)    
    
    return lid, lid_hex
