############################################################################
# Created Date: 01-Jan-2021
# Implemented by: Huong Luong
# Test case: OCR Label
############################################################################
#import re
import sys
from PIL import Image
#libsfolder = "C:\\HHS\\Actions\\"
#if libsfolder not in sys.path: sys.path.append(libsfolder)
# IMPORT LIBRARY
from setuptools.msvc import SystemInfo

sys.path.append('C:\HHS\Actions\\')
import eink
import Actions.devicebase as devicebase
import Actions.KeyUtil as KeyUtil
import Actions.ext as ext
import Actions.Utilities as Utilities
import Actions.DBv2 as DBv2
import Actions.Common as Common
import random
import logging
import time
from functools import reduce
# set folder containg logs, data, plan, ...
# Initialize log
randomefilename = Utilities.CreateRandomString()
debuglogname = randomefilename + "_TestOCR_LOG.txt"
debuglogpath = "C:\\HHS\\Logs\\" + debuglogname

# Open log file
#fd = open(debuglogpath, "a")
#logging.basicConfig(filename=debuglogname)
logging.basicConfig(level=logging.INFO,filename=debuglogpath,format='%(asctime)s :: %(levelname)s :: %(message)s')
# open wb
dbplanfile = Common.globaldict['dbfile']
ocrfolder = Common.globaldict['ocrfolder']
wbobj = DBv2.Excel(dbplanfile.openwb())

# open CommonSetting sheet
commonws = DBv2.Excel(dbplanfile, "CommonSetting").openws(wbobj)

# get plan some information
connectserialtimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(1, "Value", commonws))
entersptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(2, "Value", commonws))
writecmdsptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(3, "Value", commonws))
readcmdsptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(4, "Value", commonws))
getallcfgssptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(5, "Value", commonws))
restoresptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(6, "Value", commonws))
changeifsptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(7, "Value", commonws))
resetsptimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(8, "Value", commonws))
readingtimeout = int(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(9, "Value", commonws))
isbtlistsheet = str(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(10, "Value", commonws))
dbreffile = str(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(11, "Value", commonws))
devdisplay = str(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(12, "Value", commonws))
comport = str(DBv2.Excel(dbplanfile, "CommonSetting").GetCellValueByColumnName(13, "Value", commonws))
def ReadDataTable():
    datatablews = DBv2.Excel(dbplanfile,"DataTable").openws(wbobj)
    lstTC = []
    totalrows = DBv2.Excel(dbplanfile,"DataTable").GetTotalRows(datatablews)
    i = 1
    while i < totalrows:
        tcProcedure = str(DBv2.Excel(dbplanfile,"DataTable").GetCellValueByColumnName(i,"Procedure",datatablews))
        tcSetting = str(DBv2.Excel(dbplanfile,"DataTable").GetCellValueByColumnName(i,"Setting",datatablews))
        tcExpected = str(DBv2.Excel(dbplanfile,"DataTable").GetCellValueByColumnName(i,"Label",datatablews))
        dctTestcase = dict()
        dctTestcase["Procedure"] = tcProcedure
        dctTestcase["Setting"] = tcSetting
        dctTestcase["Label"] = tcExpected.split("\n")
        lstTC.append(dctTestcase)
        i=i+1

    return lstTC



# create label base on excel file
# The character "N" (0x4E) shall identify any of following numbers:
lstOCR_A_Number = ["0", "1", "2", "3","4", "5", "6", "7", "8", "9"]
lstOCR_B_Number = ["0", "1", "2", "3","4", "5", "6", "7", "8", "9"]
lstMICR_Number = ["0", "1", "2", "3","4", "5", "6", "7", "8", "9"]

# The character "A" (0x41) shall identify any of following characters:
lstOCR_A_Letter = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R","S", "T", "U", "V", "W", "X", "Y", "Z", "<", ">"]
lstOCR_B_Letter = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R","S", "T", "U", "V", "W", "X", "Y", "Z", "<"]
lstMICR_Letter = ["A", "B", "C", "D"]

# The character "B" (0x42) shall identify any of following character:
lstOCR_A_Alphanumerical = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R","S", "T", "U", "V", "W", "X", "Y", "Z", "<", ">", "="]
lstOCR_B_Alphanumerical = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R","S", "T", "U", "V", "W", "X", "Y", "Z", "<"]
lstMICR_Alphanumerical =  ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D"]
#The character "E" (0x45) shall identify any of following character:
lstOCR_B_ExtendedNumeric = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "<"]
lstOCR_A_ExtendedNumeric = lstOCR_B_ExtendedNumeric
#MICR not support extended numeric

#The character "Y" (0x59) shall identify any of following symbol
lstOCR_B_Symbol = ["<"]
lstOCR_A_Symbol = ["<", ">", "="]

def CreateRandomString(charsetList,number):
    randomstring = ""
    try:
        for i in range(number):
            randomstring = randomstring + random.choice(charsetList)

    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return randomstring

# create OCR image
def CreateOCRImage(ocrtexts,filename):
    ocrimg = ""
    ocrfont = filename[0:4:1]
    wordpath = ""
    try:
        # open word setting with OCRB font , shoud use font 26
        if(ocrfont.upper() == "OCRA"):

            wordpath = Common.workingfolder + "Data\\ocra_font26.doc"

        elif (ocrfont.upper() == "OCRB"):
            wordpath = Common.workingfolder + "Data\\ocrb_font26.doc"

        elif (ocrfont.upper() == "MICR"):
            wordpath = Common.workingfolder + "Data\\micr_font36.doc"

        Utilities.StartProgram(wordpath)
        time.sleep(10)

        for char in ocrtexts:
            #texttype = str(text).replace(" ", "{SPACE}").replace("+", "{+}")
            if(char=="@"):
                KeyUtil.KeyUtil().Type("{ENTER}")
                continue
            if(char==" "):
                KeyUtil.KeyUtil().Type("{SPACE}")
                continue
            KeyUtil.KeyUtil().Type(char)
            time.sleep(1.0)
            # send enter
            #KeyUtil.KeyUtil().Type("{ENTER}")

        # enter some break line
        for i in range(5):
            KeyUtil.KeyUtil().Type("{ENTER}")

            # capture screen text
        # create screenshot name
        screenshotname = filename + ".png"
        #screenshotfoldertmp = Common.workingfolder + "Labels\\OCR\\Tmp\\"
        screenshotfoldertmp = ocrfolder
        screenshotpath = screenshotfoldertmp + screenshotname
        Utilities.CaptureScreen(screenshotpath,544, 300,815, 220)
        #ocrimg = screenshotpath
        ocrimg = screenshotname
        # close word
        time.sleep(1.0)
        KeyUtil.KeyUtil().Type("%{F4}")
        time.sleep(0.5)
        KeyUtil.KeyUtil().Type("%n")
        time.sleep(0.5)

    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return ocrimg

def CreateOCRADataText(label):
    dctOCRTextData = dict()
    dctOCRTextData["OCRAletter1"] = CreateRandomString(lstOCR_A_Letter, 14)
    dctOCRTextData["OCRAletter2"] = CreateRandomString(lstOCR_A_Letter,14)
    dctOCRTextData["OCRAAlphanumerical1"] = CreateRandomString(lstOCR_A_Alphanumerical,24)
    dctOCRTextData["OCRAAlphanumerical2"] = CreateRandomString(lstOCR_A_Alphanumerical,24)
    dctOCRTextData["OCRAExtendedNumeric"] = CreateRandomString(lstOCR_A_ExtendedNumeric,11)
   # dctOCRTextData["strOCR_A_Numeric"] = CreateRandomString(lstOCR_A_Number,10)
    dctOCRTextData["OCRASymbol&Number1"] = CreateRandomString(lstOCR_A_Number,5) + CreateRandomString(lstOCR_A_Symbol,2)
    dctOCRTextData["OCRASymbol&Number2"] = CreateRandomString(lstOCR_A_Number,5) + CreateRandomString(lstOCR_A_Symbol,2)
    return dctOCRTextData

    print('dctOCRTextData = ',dctOCRTextData)
    print('Length of CRTTextData =', dctOCRTextData.__len__())
    return dctOCRTextData
def CreateOCRBDataText():
    # dictionary dctOCRTextData
    dctOCRTextData = dict()
    dctOCRTextData["OCRBletter1"] = CreateRandomString(lstOCR_B_Letter, 14)
    dctOCRTextData["OCRBletter2"] = CreateRandomString(lstOCR_B_Letter, 14)
    dctOCRTextData["OCRBAlphanumerical1"] = CreateRandomString(lstOCR_B_Alphanumerical, 24)
    dctOCRTextData["OCRBAlphanumerical2"] = CreateRandomString(lstOCR_B_Alphanumerical, 24)
    dctOCRTextData["OCRBExtendedNumeric"] = CreateRandomString(lstOCR_B_ExtendedNumeric, 11)
    dctOCRTextData["OCRBSymbolNumber1"] = CreateRandomString(lstOCR_B_Number, 5) + CreateRandomString(
        lstOCR_B_Symbol, 2)
    dctOCRTextData["OCRBSymbolNumber2"] = CreateRandomString(lstOCR_B_Number, 5) + CreateRandomString(
        lstOCR_B_Symbol, 2)
    print('dctOCRTextData = ', dctOCRTextData)
    print('Length of CRTTextData =', dctOCRTextData.__len__())
    return dctOCRTextData
def CreateMICRDataText():
    dctOCRTextData = dict()
    strMICRLetterAndNumber = ""
    for i in range(4):
        strMICRLetterAndNumber = strMICRLetterAndNumber + CreateRandomString(lstMICR_Number, 1) + CreateRandomString(
            lstMICR_Letter, 1)
    dctOCRTextData["MICRLetter&Number"] = strMICRLetterAndNumber
    dctOCRTextData["MICRNumber"] = CreateRandomString(lstMICR_Number, 10)
    dctOCRTextData["MICRAlphanumerical"] = CreateRandomString(lstMICR_Alphanumerical, 14)

    print('dctOCRTextData = ', dctOCRTextData)
    print('Length of CRTTextData =', dctOCRTextData.__len__())
    return dctOCRTextData


#Create OCR A Label Type
def OCRALetter():
   return CreateRandomString(lstOCR_A_Letter, 14)
def OCRAAlphanumerical():
    return CreateRandomString(lstOCR_A_Alphanumerical,24)
def OCRAExtendedNumeric():
    return CreateRandomString(lstOCR_A_ExtendedNumeric,11)
def OCRASymbolAndNumber():
    return CreateRandomString(lstOCR_A_Number,5) + CreateRandomString(lstOCR_A_Symbol,2)


#Create OCR B label Type
def OCRBLetter():
    return CreateRandomString(lstOCR_B_Letter, 14)
def OCRBAlphanumerical():
    return CreateRandomString(lstOCR_B_Alphanumerical, 24)
def OCRBExtendedNumeric():
    return CreateRandomString(lstOCR_B_ExtendedNumeric, 11)
def OCRBSymbolNumber():
    return CreateRandomString(lstOCR_B_Number, 5) + CreateRandomString(lstOCR_B_Symbol, 2)

#Create MICR Label Type
def MICRLetterAndNumber():
    strMICRLetterAndNumber = ""
    for i in range(4):
        strMICRLetterAndNumber = strMICRLetterAndNumber \
                                 + CreateRandomString(lstMICR_Number, 1) \
                                 + CreateRandomString(lstMICR_Letter, 1)
    return strMICRLetterAndNumber
def MICRNumber():
    return CreateRandomString(lstMICR_Number, 10)
def MICRAlphanumerical():
    return CreateRandomString(lstMICR_Alphanumerical, 14)
def OCRATwoLines():
    return CreateRandomString(lstOCR_A_Number,4) \
           + "@" \
           + CreateRandomString(lstOCR_A_Alphanumerical,4) \
           + " " \
           + CreateRandomString(lstOCR_A_Alphanumerical,3)
def OCRAThreeLines():
    return  CreateRandomString(lstOCR_A_Alphanumerical,4) \
            + "@" \
            + CreateRandomString(lstOCR_A_ExtendedNumeric,4) \
            + "@" \
            + CreateRandomString(lstOCR_A_Letter,4)
def OCRBTwoLines():
    return CreateRandomString(lstOCR_B_Number,4) \
           + "@" \
           + CreateRandomString(lstOCR_B_Alphanumerical,4) \
           + " " \
           + CreateRandomString(lstOCR_B_Alphanumerical,3)
def OCRBThreeLines():
    return CreateRandomString(lstOCR_B_Alphanumerical,4) \
           + "@" \
           + CreateRandomString(lstOCR_B_ExtendedNumeric,4) \
           + "@" \
           + CreateRandomString(lstOCR_B_Letter,4)
def MICRTwoLines():
    return CreateRandomString(lstMICR_Alphanumerical,3) \
           + "@" \
           + CreateRandomString(lstMICR_Number,2) \
           + " " \
           + CreateRandomString(lstMICR_Number,1) \
           + CreateRandomString(lstMICR_Letter,1) \
           + CreateRandomString(lstMICR_Number,3)
def MICRThreeLines():
    return CreateRandomString(lstMICR_Alphanumerical,2) \
           + CreateRandomString(lstMICR_Letter,1)\
           + CreateRandomString(lstMICR_Alphanumerical,2) \
           + "@" \
           + CreateRandomString(lstMICR_Number,2) \
           + " " \
           + CreateRandomString(lstMICR_Letter,1) \
           + CreateRandomString(lstMICR_Number,2) \
           + "@"\
           + CreateRandomString(lstMICR_Number,2) \
           + " " \
           + CreateRandomString(lstMICR_Letter,1) \
           + CreateRandomString(lstMICR_Number,2)
def OCRARemoveLetter():
    return CreateRandomString(lstOCR_A_Alphanumerical,2) \
           + CreateRandomString(lstOCR_A_Letter, 1) \
           + CreateRandomString(lstOCR_A_Alphanumerical,2) \
           + " " \
           + CreateRandomString(lstOCR_A_Number,2)\
           + CreateRandomString(lstOCR_A_Letter,1) \
           + CreateRandomString(lstOCR_A_Number,2)
def OCRBRemoveSpace():
    return CreateRandomString(lstOCR_B_Alphanumerical, 2) \
           + CreateRandomString(lstOCR_B_Letter, 1) \
           + CreateRandomString(lstOCR_B_Alphanumerical, 2) \
           + " " \
           + CreateRandomString(lstOCR_B_Number, 2) \
           + CreateRandomString(lstOCR_B_Letter, 1) \
           + CreateRandomString(lstOCR_B_Number, 2)
def OCRARemoveSymbol():
    return CreateRandomString(lstOCR_A_Alphanumerical, 2) \
           + CreateRandomString(lstOCR_A_Letter, 1) \
           + CreateRandomString(lstOCR_A_Alphanumerical, 2) \
           + " " \
           + CreateRandomString(lstOCR_A_Number, 2) \
           + CreateRandomString(lstOCR_A_Symbol, 1) \
           + CreateRandomString(lstOCR_A_Number, 2)
def OCRBRemoveMulti():
    return CreateRandomString(lstOCR_B_Alphanumerical, 2) \
           + CreateRandomString(lstOCR_B_Letter, 1) \
           + CreateRandomString(lstOCR_B_Alphanumerical, 2) \
           + " " \
           + CreateRandomString(lstOCR_B_Number, 2) \
           + CreateRandomString(lstOCR_B_Symbol, 1) \
           + CreateRandomString(lstOCR_B_Number, 2)
def MICRRemoveFirstEndPosition():
    return CreateRandomString(lstMICR_Letter, 1) \
           + CreateRandomString(lstMICR_Alphanumerical, 6) \
           + CreateRandomString(lstMICR_Letter, 1)

def CreateOCRLabel(OCRLabelType):
    switcher = {
        "OCRALetter1" : OCRALetter,
        "OCRALetter2" : OCRALetter,
        "OCRAAlphanumerical1" : OCRAAlphanumerical,
        "OCRAAlphanumerical2" : OCRAAlphanumerical,
        "OCRAExtendedNumeric" : OCRAExtendedNumeric,
        "OCRASymbolAndNumber1" : OCRASymbolAndNumber,
        "OCRASymbolAndNumber2" : OCRASymbolAndNumber,
        "OCRBLetter1" : OCRBLetter,
        "OCRBLetter2" : OCRBLetter,
        "OCRBAlphanumerical1" : OCRBAlphanumerical,
        "OCRBAlphanumerical2" : OCRBAlphanumerical,
        "OCRBExtendedNumeric" : OCRBExtendedNumeric,
        "OCRBSymbolNumber1" : OCRBSymbolNumber,
        "OCRBSymbolNumber2": OCRBSymbolNumber,
        "MICRLetterAndNumber" : MICRLetterAndNumber,
        "MICRNumber" : MICRNumber,
        "MICRAlphanumerical" : MICRAlphanumerical,
        "OCRATwoLines": OCRATwoLines,
        "OCRAThreeLines" : OCRAThreeLines,
        "OCRBTwoLines" : OCRBTwoLines,
        "OCRBThreeLines" : OCRBThreeLines,
        "MICRTwoLines" : MICRTwoLines,
        "MICRThreeLines" : MICRThreeLines,
        "OCRARemoveLetter" : OCRARemoveLetter,
        "OCRBRemoveSpace" : OCRBRemoveSpace,
        "OCRARemoveSymbol1" : OCRARemoveSymbol,
        "OCRARemoveSymbol2": OCRARemoveSymbol,
        "OCRARemoveSymbol3": OCRARemoveSymbol,
        "OCRBRemoveMulti" : OCRBRemoveMulti,
        "MICRRemoveFirstEndPosition1": MICRRemoveFirstEndPosition,
        "MICRRemoveFirstEndPosition2": MICRRemoveFirstEndPosition

    }
    result = switcher.get(OCRLabelType,lambda : "NOT DEFINE THIS LABEL")
    return result()


def CreateLstOCRImage(lstOCRLabelType):
    tmp = dict()
    for OCRLabelName in lstOCRLabelType:
         # random data for each OCRLabelType and also read image
        random_data = CreateOCRLabel(OCRLabelName)
        print(OCRLabelName)
        if random_data == "NOT DEFINE THIS LABEL":
            random_data = "";
            logging.error(OCRLabelName + "does not define")
            continue
        ocrimage = CreateOCRImage(ocrtexts = random_data, filename = OCRLabelName)
        tmp[OCRLabelName] = random_data
    return tmp
def ConvertOCRImageByImageMagic():
    import os
    import subprocess
    batfile = "C:\Keyboard\CountryMode\Extra\ResizeOCRImage.bat"
    os.system(batfile)

def LoadOCRLabel(devicedisplay="kindle", imagepath=None, waitingtime=10, extobj=None):
    try:
        print("Starting: Load label to display device: " + str(devicedisplay))
        if devicedisplay.upper() == "KINDLE":
            if imagepath.find("\\") >= 0:
                imagepath = imagepath.replace("\\", "/")

            imagelabelname = imagepath[imagepath.rfind("/") + 1:]

            # upload image to kindle
            print("Upload image: " + str(imagepath) + " to display device: " + str(devicedisplay))
            ext.Ext(devicedisplay).uploadImage(imagepath)

            # Load image and read
            # open kindle
            if extobj is None:
                print("Open display device: " + str(devicedisplay))
                extobj = ext.Ext(devicedisplay).open()

            if extobj is not None:
                # clear kindle
                print("Clear screen display")
                ext.Ext(devicedisplay).clearScreen(extobj, 1)

                # display image on kindle
                print("Display image: " + imagelabelname)
                ext.Ext(devicedisplay).displayImage(extobj, imagelabelname)

                # waiting
                time.sleep(waitingtime)
                print("Sleep: " + str(waitingtime))

                # clear kindle
                print("Clear screen display")
                ext.Ext(devicedisplay).clearScreen(extobj, 1)

        elif devicedisplay.upper() == "PC":
            Utilities.OpenImage(imagepath)

            time.sleep(waitingtime)

            Utilities.CloseImage(imagepath)

        # [Nam Nguyen, 18-Oct-2019]: Load image by eink
        elif devicedisplay.upper() == "EINK":
            print("Display image on EINK: " + imagepath)
            Utilities.LoadOCRAndDisplayOCROnEink(imagepath)

            time.sleep(waitingtime)
            print("Sleep: " + str(waitingtime))

            # clear eink
            #Utilities.ClearEink()

    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        print(err)


def SettingOnScanner(strCommand):
    #Open host
    #hostobj = devicebase.Device(comport)
    isopen = devicebase.DeviceObject().isOpen()
    # read host
    scanneres = devicebase.DeviceObject().read()
    # Enter sp and write
    devicebase.DeviceObject().write("$S\x0d")
    time.sleep(2)
    enterspstatus = devicebase.DeviceObject().read()
    print("Enter service port $S: " + repr(enterspstatus))
    devicebase.DeviceObject().changeBaudrate(115200)
    devicebase.DeviceObject().changeParity("N")
    devicebase.DeviceObject().changeByteSize(8)
    devicebase.DeviceObject().changeStopbits(1)
    strCommand = "$CSNRM03,CBPVO00," + strCommand + ",Ar\x0d"
    devicebase.DeviceObject().write(strCommand)
    print(strCommand)
    # read host
    scanneres = devicebase.DeviceObject().read()


def RemoveLetter(data,index):
    if len(data) > index:
        data = data[0:index:] + data[index+1::]
    return data
def GetLabelID(OCRLabelType,setting):
   labelID="";
   if "OCRA" in OCRLabelType:
        if "IDCO01" in setting:
            if "OAID" in setting:
                labelID = "$a"
            else:
                labelID = "$o"

   if "OCRB" in OCRLabelType:
        if "IDCO01" in setting:
            if "OBID" in setting:
                labelID = "$b"
            else:
                labelID = "$p"

   if "MIRC" in OCRLabelType:
       if "IDCO01" in setting:
           if "OMID" in setting:
               labelID = "$c"
           else:
               labelID = "$m"
   return labelID
def GetAIMID(OCRLabelType,setting):
    aimid = "";
    if "OCRA" in OCRLabelType:
        if "AIEN01" in setting:
            aimid = "]o1"
    if "OCRB" in OCRLabelType:
        if "AIEN01" in setting:
            aimid = "]o2"
    if "MICR" in OCRLabelType:
        if "AIEN01" in setting:
            aimid = "]o3"
    return aimid
def GenerateExpectedData(OCRLabelType,OCRDataTest,setting):

    if "OCRARemoveLetter" in OCRLabelType:
       OCRDataTest = RemoveLetter(OCRDataTest,index=8)
    if "OCRBRemoveSpace" in OCRLabelType:
        OCRDataTest = RemoveLetter(OCRDataTest,index=5)
    if "OCRARemoveSymbol" in OCRLabelType: #check also OCRARemoveSymbol1 OCRARemoveSympbol2, OCRARemoveSymbol3
        OCRDataTest = RemoveLetter(OCRDataTest,index=8)
    if "OCRBRemoveMulti" in OCRLabelType:
        temp = RemoveLetter(OCRDataTest,index=5)
        OCRDataTest = RemoveLetter(temp,index=7)
    if "MICRRemoveFirstEndPosition" in OCRLabelType:
        temp = RemoveLetter(OCRDataTest,index=0)
        OCRDataTest = RemoveLetter(temp,index=len(temp)-1)
    OCRDataTest = GetAIMID(OCRLabelType,setting) + GetLabelID(OCRLabelType,setting) + OCRDataTest;
    result = OCRDataTest
    return result
def VerifyLabel(expecteddata, actualdata, verifytype):
        result = False
        try:
            if verifytype == "match":
                result = expecteddata == actualdata.encode('utf-8')
            elif verifytype == "diff":
                result = expecteddata != actualdata.encode('utf-8')
            elif verifytype == "timeout":
                result = len(expecteddata) == len(actualdata) == 0
            else:
                print(verifytype + " is invalid")
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return result

######START TEST SCRIPT################

lstDictTestCase = ReadDataTable()
print("lstDictTestCase = ",lstDictTestCase)
lstOCRLabelType = [d['Label'] for d in lstDictTestCase]
print("lstOCRLabelType = ",lstOCRLabelType)
dcmage = dict()
lstOCRLabelType = reduce(lambda x,y:x+y,lstOCRLabelType)
lstOCRLabelType = [i for i in lstOCRLabelType if i] # remove empty string
print ("lstOCRLabelType = ",lstOCRLabelType)



########CREATE OCR IMAGE#################  
#dctOCRImage = CreateLstOCRImage(lstOCRLabelType)
#print("dctOCRImage = ",dctOCRImage)
#ConvertOCRImageByImageMagic()
########END CREATE OCR IMAGE############


"""dctOCRImage = {"OCRBSymbolNumber2": "51236<<",
               "MICRLetterAndNumber": "3C1A0C1B",
               "OCRBSymbolNumber1": "51539<<",
               "MICRNumber": "5722517846",
               "OCRASymbolAndNumber2": "72141<=",
               "OCRBLetter1": "LOQWXC<VTT<JIG",
               "OCRAExtendedNumeric": "6051<96247<",
               "OCRBLetter2": "NEQYHSNRESVKND",
               "MICRAlphanumerical": "D8C774C637297D",
               "OCRASymbolAndNumber1": "10785=>",
               "OCRALetter1": "GVCSOYVYI<IAV<",
               "OCRALetter2": "F>ICMZRIHX<K<Y",
               "OCRBExtendedNumeric": "<27880292<5",
               "OCRAAlphanumerical2": "QALJXZZFG83>2I4J1ZA84AMQ",
               "OCRBAlphanumerical2": "WUW1HURY<RX1KAAFIB96RTTZ",
               "OCRBAlphanumerical1": "N5DCS2VEQ9G52ILTMVL26BQT",
               "OCRAAlphanumerical1": "WI><4MYJZZO8C<0WDEP1H41S"}
"""
#dctOCRImage = {"OCRARemoveLetter":"9LB=6 12K93"}
dctOCRImage = {"OCRALetter1": "LCZUWDDSTLUFPR",
               "MICRNumber": "1754134364",
              "OCRBLetter1": "BZMLNARDNAOLOF"}
hostobj = devicebase.Device(comport)
for testcase in lstDictTestCase:
    SettingOnScanner(testcase["Setting"])
    imgname =  testcase["Label"]
    print("imgname =",imgname)
    for i in imgname:
         imgpath = ocrfolder + i + ".png";
         print(imgpath)
         LoadOCRLabel("EINK", imgpath,waitingtime=10)
         expected = GenerateExpectedData(i,dctOCRImage[i],testcase["Setting"])
         #Open host
         #read host
         response = devicebase.DeviceObject().read()
         print("Response = ", response)
         if(response == "" ):
             logging.error("Testcase name :" + testcase["Procedure"] + ": FAIL")
             logging.info("Setting       :" + testcase["Setting"])
             logging.info("Image path    :" + imgpath)
             logging.info("Expected data : " + expected)
             logging.info("Response data : Scanner can not read, please try manual")
         else:
             lstresponse = response.split('\r')
             response = lstresponse[-1]
             print("Scanner response:",response)
             print("Expected :" + expected)
             result = VerifyLabel(expected,response,"match")
             if result:
                  logging.info("Testcase name :" + testcase["Procedure"] + ": PASS")
                  logging.info("Setting       :" + testcase["Setting"])
                  logging.info("Image path    :" + imgpath)
             else:
                  logging.error("Testcase name :" + testcase["Procedure"] + ": FAIL")
                  logging.info("Setting       :" + testcase["Setting"])
                  logging.info("Image path    :" + imgpath)
             logging.info("Expected data : " + expected)
             logging.info("Response data : " + response)
Utilities.ClearEink()
