#############################################################
# Implemented By : Huong. Luong
# Created Date: 24-Aug-2021
# Description: Automate testcase testcase MT_IC_HostCommandImageCapture in procedure Image Capture_X4X13.doc
# Using file   : C:\Keyboard\CountryMode\Data\SettingImageCapture.xls
#############################################################
import sys
libsfolder = "C:\\HHS\\Actions\\"
if libsfolder not in sys.path: sys.path.append(libsfolder)
import serial
import time
import sys
import os
import logging
from datetime import datetime
import DBv2
import parselog2

IMG_ABORT_MSG = '$b\r'
dctImgType = {'JPEG': '1',
              'TIFF': '3',
              'BMP': '0',
              'JPEG 2000': '2'}


def doRead(ser, term, tout):
    tic = time.time()
    buff = ser.read(1)
    while (((time.time() - tic) < tout) and (not term in buff)):
        buff += ser.read(1)
    return buff

def doReadWithLength(ser,term,tout,length):
    tic = time.time()
    buff = ser.read(1)
    while (((time.time() - tic) < tout) and (not term in buff) and (len(buff)<length)):
        buff += ser.read(1)
    return buff

def char2hex(c):
    if (c >= 48 and c <= 57):
        return c - 48

    if (c >= 65 and c <= 70):
        return c - 65 + 10

    return -1


def hex2int(hexlist):
    ret = 0
    for i, val in (list(enumerate(hexlist))):
        exp = 7 - i
        ret += val * (2 ** (4 * exp))

    return ret


# Press the green button in the gutter to run the script.
def SettingOnScanner(ser, imgFormat):
    cmdStr = '$S,CIPFI00,Ar'
    if (imgFormat == lstImgType[0]):
        cmdStr = cmdStr[:8] + '00' + cmdStr[10:]
    elif (imgFormat == lstImgType[1]):
        cmdStr = cmdStr[:8] + '01' + cmdStr[10:]
    elif (imgFormat == lstImgType[2]):
        cmdStr = cmdStr[:8] + '02' + cmdStr[10:]
    elif (imgFormat == lstImgType[3]):
        cmdStr = cmdStr[:8] + '03' + cmdStr[10:]
    writeCmd(ser, cmdStr)
    time.sleep(float(resetTimeOut))
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    if (raw.decode() == '$>,>,>\r'):
        strInfo = "Setting on scanner successfully and scanner reset"
        PrintAndWriteLog(strInfo, logging.INFO)


def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key


def verifyAbortCapture(response, expected):
    if (response == expected):
        return True
    else:
        return False


def printResult(str, result, expected=None, actual=None):
    tmp1 = ', expected: '
    tmp2 = ', actual: '
    if expected == None:
        tmp1 = ''
        expected = ''
    if actual == None:
        tmp2 = ''
        actual = ''

    if result:
        str = str + "PASSED" + tmp1 + expected + tmp2 + actual
    else:
        str = str + "FAILED" + tmp1 + expected + tmp2 + actual
    PrintAndWriteLog(str, logging.INFO)


def PrintAndWriteLog(strInfo, loglevel=None):
    if loglevel == None:
        loglevel = logging.DEBUG
    print(str(strInfo))
    if (loglevel == logging.INFO):
        logging.info(strInfo)
    elif (loglevel == logging.DEBUG):
        logging.debug(strInfo)
    elif (loglevel == logging.ERROR):
        logging.error(strInfo)
    elif (loglevel == logging.WARNING):
        logging.warning(strInfo)


def writeCmd(ser, cmd):
    cmd = cmd + "\r"
    ser.write(cmd.encode('utf-8'))
    PrintAndWriteLog("Write command: " + str(cmd.encode('utf-8')))


##################################################################
# This method Use to update value of dictionary get from excel sheet
##################################################################
def LoadDictionary(filePath, dctCmdList, sheetName, columnKey, columnValue):
    wbobj = DBv2.Excel(filePath).openwb()
    ws = DBv2.Excel(filePath, sheetName).openws(wbobj)
    row_count = ws.nrows
    i = 1
    while (i < row_count):
        value = str(DBv2.Excel(filePath, sheetName).GetCellValueByColumnName(i, columnValue, ws))
        key = str(DBv2.Excel(filePath, sheetName).GetCellValueByColumnName(i, columnKey, ws))
        dctCmdList[key] = value
        i = i + 1


def verifyImageType(dctImgType, raw, imgFormat):
    # verify image type
    if (raw.decode() != ""):
        returnImageType = get_key(dctImgType, raw.decode()[3])
    else:
        returnImageType = ""
    result = False
    if imgFormat == returnImageType:
        result = True
    printResult("Verify image type: ", result, imgFormat, returnImageType)
    return result


def Run_TC_Image_Capture_Auto(ser, cmd, imgFormat):
    start = time.time()
    cmdName = get_key(dctCmdList, cmd)
    infoStr = "START SCENARIO: " + cmdName + ", Image type: " + imgFormat
    PrintAndWriteLog(infoStr, logging.INFO)
    SettingOnScanner(ser, imgFormat)
    # Step 1: send host command'
    #print("Send host command capture no handshake:" + str(time.ctime()))
    writeCmd(ser, cmd)
    rawstringi = doRead(ser, '\r'.encode('utf-8'), 10)
    resStr = "Scanner reponsed: " + str(rawstringi.decode('utf-8'))
    PrintAndWriteLog(resStr)
    rawbuf = [char2hex(x) for x in rawstringi[4:12]]
    expected_len = hex2int(rawbuf)
    #result1 = verifyImageType(dctImgType, raw, imgFormat)
    #time.sleep(1)
    # Within 2s send command IMG_TX
    if (cmdName == 'HOST_CMD_CAPTURE'):
        writeCmd(ser, dctCmdList["HOST_CMD_IMG_TX"])
    # getdata image
    loop = 1
    if imgFormat == "BMP": loop = 6
    i = 0
    rawimagedata = ser.read(expected_len)
    while (i < loop and rawimagedata != b''):
      rawimagedata = ser.read(expected_len)
      i = i + 1



    result1 = verifyImageType(dctImgType, rawstringi, imgFormat)
    if rawimagedata != "":
        printResult("Verify image: ", True, str(expected_len), str(expected_len))
        result2 = True
    else:
        printResult("Verify image: ", False, str(expected_len), "null")
        result2 = False

    finalResult = result1 and result2

    #time.sleep(5)
    end = time.time();
    total = CountTimeConsumer(start,end)
    if finalResult == True:
        infoStr = "END SCENARIO: PASSED " + cmdName + " Image type: " + imgFormat + ", duration time: " + total
    else:
        infoStr = "END SCENARIO: FAILED " + cmdName + " Image type: " + imgFormat + ", duration time: " + total

    PrintAndWriteLog(infoStr, logging.INFO)
    PrintAndWriteLog("********************************************************************************\r")

def Run_TC_Image_Capture_OnTrigger(ser, cmd, imgFormat):
    start = time.time()
    cmdName = get_key(dctCmdList, cmd)
    infoStr = "START SCENARIO: " + cmdName + " Image type: " + imgFormat
    PrintAndWriteLog(infoStr, logging.INFO)
    SettingOnScanner(ser, imgFormat)
    # Step 1: send host command'
    writeCmd(ser, cmd)

    # Step 2: Don't get trigger and abort image
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)

    # Step 3:  send again host command
    writeCmd(ser, cmd)
    time.sleep(1)
    writeCmd(ser, dctCmdList["HOST_CMD_TRIGGER_ON"])
    rawstringi = doRead(ser, '\r'.encode('utf-8'), 10)
    resStr = "Scanner reponsed: " + str(rawstringi.decode('utf-8'))
    PrintAndWriteLog(resStr)
    rawbuf = [char2hex(x) for x in rawstringi[4:12]]
    expected_len = hex2int(rawbuf)

    if (cmdName == "HOST_CMD_CAPTURE_ON_TRIGGER"):
        writeCmd(ser, dctCmdList["HOST_CMD_IMG_TX"])
    #get image data
    loop = 1
    if imgFormat == "BMP": loop = 6
    i = 0
    rawimagedata = ser.read(expected_len)
    if rawimagedata != b'':
        result2 = True
    else:
        result2 = False
    while (i < loop and rawimagedata != b''):
        rawimagedata = ser.read(expected_len)
        i = i + 1

    if result2:
        printResult("Verify image: ", True, str(expected_len), str(expected_len))
    else:
        printResult("Verify image: ", False, str(expected_len), "null")

    result1 = verifyImageType(dctImgType, rawstringi, imgFormat)
    finalResult = result1 and result2
    time.sleep(5)
    if finalResult == True:
        infoStr = "END SCENARIO: PASSED " + cmdName + " Image type: " + imgFormat
    else:
        infoStr = "END SCENARIO: FAILED " + cmdName + " Image type: " + imgFormat
    end = time.time()
    CountTimeConsumer(start,end)
    PrintAndWriteLog(infoStr, logging.INFO)
    PrintAndWriteLog("********************************************************************************\r")

def Run_TC_Image_MultiCapture_OnTrigger(ser, cmd, imgFormat):
    start = time.time()
    cmdName = get_key(dctCmdList, cmd)
    infoStr = "START SCENARIO: " + cmdName + ", Image type: " + imgFormat
    PrintAndWriteLog(infoStr, logging.INFO)
    SettingOnScanner(ser, imgFormat)
    # Step 1: send host command'
    writeCmd(ser, cmd)

    # Step 2: Don't get trigger and abort image
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)

    # Step 3:  send again host command
    writeCmd(ser, cmd)
    time.sleep(1)
    times = 2
    result = [False, False]
    for x in range(times):
        tmp = "Times :" + str(x + 1)
        PrintAndWriteLog(tmp, logging.INFO)
        writeCmd(ser, dctCmdList["HOST_CMD_TRIGGER_ON"])
        rawstringi = doRead(ser, '\r'.encode('utf-8'), 10)
        resStr = "Scanner reponsed: " + str(rawstringi.decode('utf-8'))
        PrintAndWriteLog(resStr)
        rawbuf = [char2hex(x) for x in raw[4:12]]
        expected_len = hex2int(rawbuf)

        if (cmdName == "HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER"):
            writeCmd(ser, dctCmdList["HOST_CMD_IMG_TX"])
            #time.sleep(1)
        #get imagedata raw
        loop = 1
        if imgFormat == "BMP": loop = 6
        i = 0
        rawimagedata = ser.read(expected_len)
        while (i < loop and rawimagedata != b''):
            rawimagedata = ser.read(expected_len)
            i = i + 1

        if rawimagedata != b'':
            printResult("Verify image: ", True, str(expected_len), str(expected_len))
            result2 = True
        else:
            printResult("Verify image: ", False, str(expected_len), "null")
            result2 = False
        result1 = verifyImageType(dctImgType, rawstringi, imgFormat)
        result[x] = result1 and result2

    finalResult = result[0] and result[1]

    # Step 4: exit multi capture trigger
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)

    if finalResult == True:
        infoStr = "END SCENARIO: PASSED " + cmdName + " Image type: " + imgFormat
    else:
        infoStr = "END SCENARIO: FAILED " + cmdName + " Image type: " + imgFormat
    end = time.time();
    CountTimeConsumer()
    PrintAndWriteLog(infoStr, logging.INFO)
    PrintAndWriteLog("********************************************************************************\r")

def Run_TC_Image_Capture_OnDecode(ser, cmd, imgFormat):
    start = time.time()
    cmdName = get_key(dctCmdList, cmd)
    infoStr = "START SCENARIO: " + cmdName + ", Image type: " + imgFormat
    PrintAndWriteLog(infoStr, logging.INFO)
    SettingOnScanner(ser, imgFormat)
    # Step 1: send host command'
    writeCmd(ser, cmd)

    # Step 2: Don't get trigger and abort image
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)

    # Step 3:  send again host command
    writeCmd(ser, cmd)
    time.sleep(1)
    # Show image
    LoadImage(imagePath)
    # Press trigger
    writeCmd(ser, dctCmdList["HOST_CMD_TRIGGER_ON"])
    time.sleep(1)
    # Close image
    CloseImage(imagePath)
    datalabel = doRead(ser, '\r'.encode('utf-8'), 10)
    resStr = "Scanner reponsed: " + str(datalabel.decode('utf-8'))
    PrintAndWriteLog(resStr)

    rawstringi = doRead(ser, '\r'.encode('utf-8'), 10)
    resStr = "Scanner reponsed: " + str(rawstringi.decode('utf-8'))
    PrintAndWriteLog(resStr)
    rawbuf = [char2hex(x) for x in rawstringi[4:12]]
    expected_len = hex2int(rawbuf)

    # Send img_tx if handshake
    if (cmdName == "HOST_CMD_CAPTURE_ON_DECODE"):
        writeCmd(ser, dctCmdList["HOST_CMD_IMG_TX"])
    #get imagedata
    loop = 1
    if imgFormat == "BMP": loop = 6
    i = 0
    rawimagedata = ser.read(expected_len)
    if rawimagedata !=b'':
        result2 = True
    else:
        result2 = False
    while (i < loop and rawimagedata != b''):
        rawimagedata = ser.read(expected_len)
        i = i + 1
    if(result2):
        printResult("Verify image: ", True, str(expected_len), str(expected_len))
    else:
        printResult("Verify image: ", False, str(expected_len), "null")

    result1 = verifyImageType(dctImgType, rawstringi, imgFormat)
    finalResult = result1 and result2
    time.sleep(5)
    if finalResult == True:
        infoStr = "END SCENARIO: PASSED " + cmdName + " Image type: " + imgFormat
    else:
        infoStr = "END SCENARIO: FAILED " + cmdName + " Image type: " + imgFormat
    end = time.time()
    total = CountTimeConsumer()
    PrintAndWriteLog(infoStr, logging.INFO)
    PrintAndWriteLog("********************************************************************************\r")

def Run_TC_Image_Capture_MultiCapture_OnDecode(ser, cmd, imgFormat):
    start = time.time()
    cmdName = get_key(dctCmdList, cmd)
    infoStr = "START SCENARIO: " + cmdName + " Image type: " + imgFormat
    PrintAndWriteLog(infoStr, logging.INFO)
    SettingOnScanner(ser, imgFormat)
    # Step 1: send host command'
    writeCmd(ser, cmd)

    # Step 2: Don't get trigger and abort image
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)

    # Step 3:  send again host command
    writeCmd(ser, cmd)
    time.sleep(1)
    times = 2
    result = [False, False]
    for x in range(times):
        tmp = "Times :" + str(x + 1)
        PrintAndWriteLog(tmp)
        #imagePath =  "UPCA_1.png"
        # Show image
        LoadImage(imagePath)

        # Press trigger
        writeCmd(ser, dctCmdList["HOST_CMD_TRIGGER_ON"])

        # Close image
        time.sleep(1)
        CloseImage(imagePath)

        datalabel = doRead(ser, '\r'.encode('utf-8'), 10)
        resStr = "Scanner reponsed: " + str(datalabel.decode('utf-8'))
        PrintAndWriteLog(resStr)
        rawstringi = doRead(ser, '\r'.encode('utf-8'), 10)
        resStr = "Scanner reponsed: " + str(rawstringi.decode('utf-8'))
        PrintAndWriteLog(resStr)
        rawbuf = [char2hex(x) for x in rawstringi[4:12]]
        expected_len = hex2int(rawbuf)

        # Send img_tx if handshake
        if (cmdName == "HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE"):
            writeCmd(ser, dctCmdList["HOST_CMD_IMG_TX"])

        loop = 1
        if imgFormat == "BMP": loop = 6
        i = 0
        rawimagedata = ser.read(expected_len)
        if rawimagedata != b'':
            result2 = True
        else:
            result2 = False
        while (i < loop and rawimagedata != b''):
            rawimagedata = ser.read(expected_len)
            i = i + 1
        if result2:
            printResult("Verify image: ", True, str(expected_len), str(expected_len))
        else:
            printResult("Verify image: ", False, str(expected_len), "null")

        result1 = verifyImageType(dctImgType, rawstringi, imgFormat)
        result[x] = result1 and result2

    finalResult = result[0] and result[1]
     # Step exit multi capture trigger
    writeCmd(ser, dctCmdList["HOST_CMD_ABORT_IMAGE_CAPTURE"])
    time.sleep(3)
    raw = doRead(ser, '\r'.encode('utf-8'), 10)
    printResult("Verify abort capture: ", verifyAbortCapture(raw.decode(), IMG_ABORT_MSG))
    time.sleep(1)
    if finalResult == True:
        infoStr = "END SCENARIO: PASSED " + cmdName + " Image type: " + imgFormat
    else:
        infoStr = "END SCENARIO: FAILED " + cmdName + " Image type: " + imgFormat
    end = time.time()
    CountTimeConsumer()
    PrintAndWriteLog(infoStr, logging.INFO)
    PrintAndWriteLog("********************************************************************************\r")

def LoadImage(imagepath):
    try:
        os.startfile(imagepath)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def CloseImage(imagepath):
    try:
        os.system("taskkill /IM \"Microsoft.Photos.exe\" /F")
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def CountTimeConsumer(start,end):
    total = end - start
    formatfloat = "{:.2f}".format(total)
    PrintAndWriteLog("Time consume : " + str(formatfloat),logging.INFO)
    return str(formatfloat)

if __name__ == '__main__':
    # configure the serial connections (the parameters differs on the device you are connecting to)

    filename = "ImageCaptureLog_" + datetime.now().strftime("%d%m%Y_%H%M") + '.txt'
    #currentfolder = os.getcwd();
    #folderLog = currentfolder + "\Log"
    #if not os.path.exists(folderLog):
    #   os.makedirs(folderLog)

    #logfilepath = folderLog + "\\" + filename
    #settingFile = currentfolder + "\\" + "Setting.xls"

    #This part use to apply the hard code to C:\\HHS
    currentfolder = "C:\\HHS"
    folderLog = currentfolder + "\\Logs"
    if not os.path.exists(folderLog):
        os.makedirs(folderLog)
    logfilepath = folderLog + "\\" + filename
    settingFile = currentfolder + "\\Data\\" + "SettingImageCapture.xls"
    imagePath = currentfolder + "\\Data\\" + "UPCA_1.png"""

    
    # Read excel file
    wbobj = DBv2.Excel(settingFile).openwb()
    commonws = DBv2.Excel(settingFile, "CommonSetting").openws(wbobj)
    port = str(DBv2.Excel(settingFile, "CommonSetting").GetCellValueByColumnName(1, "Value", commonws))
    resetTimeOut = str(DBv2.Excel(settingFile, "CommonSetting").GetCellValueByColumnName(2, "Value", commonws))
    logLevel = str(DBv2.Excel(settingFile, "CommonSetting").GetCellValueByColumnName(3, "Value", commonws))
    product = str(DBv2.Excel(settingFile, "CommonSetting").GetCellValueByColumnName(4, "Value", commonws))
    if logLevel == "DEBUG":
        logging.basicConfig(level=logging.DEBUG, filename=logfilepath,
                            format='%(asctime)s :: %(levelname)s :: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, filename=logfilepath,
                            format='%(asctime)s :: %(levelname)s :: %(message)s')
    dctCmdList = {'HOST_CMD_CAPTURE': 'x00012A2A0000',
                  'HOST_CMD_IMG_TX': 'x03012A2A0000',
                  'HOST_CMD_CAPTURE_NO_HANDSHAKE': 'x008110100001',
                  'HOST_CMD_CAPTURE_ON_TRIGGER': 'x010000000000',
                  'HOST_CMD_CAPTURE_ON_TRIGGER_NO_HANDSHAKE': 'x018110100000',
                  'HOST_CMD_ABORT_IMAGE_CAPTURE': 'x04012A2A0000',
                  'HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER': 'x011120200001',
                  'HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER_NO_HANDSHAKE': 'x019030300101',
                  'HOST_CMD_CAPTURE_ON_DECODE': 'x02012A2A0000',
                  'HOST_CMD_CAPTURE_ON_DECODE_NO_HANDSHAKE': 'x028000000000',
                  'HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE': 'x021040200100',
                  'HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE_NO_HANDSHAKE': 'x029000000000',
                  'HOST_CMD_TRIGGER_ON': 'X'
                  # 'HOST_CMD_TRIGGER_OFF':'T\r'
                  }
    LoadDictionary(settingFile, dctCmdList, "CommandList", "CmdName", "CmdText")
    # port = 'COM10'
    ser = serial.Serial(
        # port=sys.argv[1],
        port=port,
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS,
        timeout=10
    )
    ser.isOpen()
    lstImgType = list(dctImgType.keys())
    ws = DBv2.Excel(settingFile, "Plan").openws(wbobj)
    tcyesrows = DBv2.Excel(settingFile, "Plan").GetRowIndexesByFilter(product, "yes", "=", ws)
    start = time.time()
    for tcrow in tcyesrows:
        tcname = str(DBv2.Excel(settingFile, "Plan").GetCellValueByColumnName(tcrow, "Testcase Name", ws))
        imgType = str(DBv2.Excel(settingFile, "Plan").GetCellValueByColumnName(tcrow, "ImageType", ws))
        count = str(DBv2.Excel(settingFile, "Plan").GetCellValueByColumnName(tcrow, "How Many Times ?", ws))
        i = 0
        if tcname == 'Image Capture Auto':
            while (i < float(count)):
                Run_TC_Image_Capture_Auto(ser, dctCmdList["HOST_CMD_CAPTURE"], imgType)
                i = i + 1
        elif tcname == 'Image Capture Auto without HandShake':
            while (i < float(count)):
                Run_TC_Image_Capture_Auto(ser, dctCmdList["HOST_CMD_CAPTURE_NO_HANDSHAKE"], imgType)
                i = i + 1
        elif tcname == 'Single Capture on Trigger':
            while(i < float(count)):
                Run_TC_Image_Capture_OnTrigger(ser, dctCmdList["HOST_CMD_CAPTURE_ON_TRIGGER"], imgType)
                i = i + 1
        elif tcname == 'Single Capture on Trigger without HandShake':
            while (i < float(count)):
                Run_TC_Image_Capture_OnTrigger(ser, dctCmdList["HOST_CMD_CAPTURE_ON_TRIGGER_NO_HANDSHAKE"], imgType)
                i = i + 1
        elif tcname == 'Multiple Capture on Trigger':
            while (i < float(count)):
                Run_TC_Image_MultiCapture_OnTrigger(ser, dctCmdList["HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER"], imgType)
                i = i + 1
        elif tcname == 'Multiple Capture on Trigger without HandShake':
            while (i < float(count)):
                Run_TC_Image_MultiCapture_OnTrigger(ser, dctCmdList["HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER_NO_HANDSHAKE"],
                                               imgType)
                i = i + 1
        elif tcname == 'Single Capture on Decode':
            while (i < float(count)):
                Run_TC_Image_Capture_OnDecode(ser, dctCmdList["HOST_CMD_CAPTURE_ON_DECODE"], imgType)
                i = i + 1
        elif tcname == 'Single Capture on Decode without HandShake':
            while (i < float(count)):
                Run_TC_Image_Capture_OnDecode(ser, dctCmdList["HOST_CMD_CAPTURE_ON_DECODE_NO_HANDSHAKE"], imgType)
                i = i + 1
        elif tcname == 'Multiple Capture on Decode':
            while (i < float(count)):
                Run_TC_Image_Capture_MultiCapture_OnDecode(ser, dctCmdList["HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE"], imgType)
                i = i + 1
        elif tcname == 'Multiple Capture on Decode without HandShake':
            while (i < float(count)):
               Run_TC_Image_Capture_MultiCapture_OnDecode(ser,
                                                       dctCmdList["HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE_NO_HANDSHAKE"],
                                                       imgType)
               i = i + 1
    ser.close()
    #parselog2.ParseLog(logfilepath)
