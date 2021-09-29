# -*- coding: utf-8 -*-
import Common
import Utilities
import time
import logging
import datetime
import Process
import GUI
import File
import KeyUtil
from threading import Thread
import sys
import random
import string
import devicebase as devb
import DB
import os, binascii


def ChangePCKeyboardLayout(os="Win7", languageid="0409:00000409", languagegroupid="1"):
    try:
        if os != "WinXP":        
            Utilities.CreateLanguageXML(Common.workingfolder, languageid)
            
            # wait for file created successfully
            time.sleep(2.0)
            
            # run command line to change system language
            Utilities.StartProgram(Common.langbatchfile)          

            # wait for system applied
            time.sleep(4.0)
        else:
            Utilities.CreateLanguageTXT(Common.workingfolder + "Data\\", languageid, str(languagegroupid))
            
            # wait for file created successfully
            time.sleep(2.0)
            
            # run command line to change system language
            Utilities.StartProgram(Common.langbatchfilexp)

            # wait for system applied. For winxp, it took long time to effect new language, so wait a bot longer
            time.sleep(20.0)        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def ReadLabelProgramming(labelprogramming, exthandleobj=None, timeout=5.0):
    try:
        # read label programming   
        Utilities.DisplayImage(Common.displayflag, exthandleobj, labelprogramming, timeout)
        
        # wait for scanner reset
        time.sleep(Common.resettimeout)
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)        

def VerifyLabel(expecteddata, actualdata, verifytype):
    result = False
    try:
        if verifytype == "match":
            result = expecteddata == actualdata.encode('utf-8')            
        elif verifytype == "diff":
            result = expecteddata <> actualdata.encode('utf-8')
        elif verifytype == "timeout":
            result = len(expecteddata) == len(actualdata) == 0
        else:
            print verifytype + " is invalid"
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return result

def ReadLabel(imagefilepath=None, hostapplication="notepad", hostserial=None, objlog=None, info=None, readinglabeltimeout=5, exthandleobj=None):
    result = ''
    try:
        # open host app to receive data
        if (hostapplication.upper() == "NOTEPAD"):
            appcmd = "notepad.exe"
            appprocess = "notepad.exe"
            apptitle = "Untitled - Notepad"                     
        # if another application --> will open winword.exe
        else:
            appcmd = "winword.exe"
            appprocess = "WINWORD.EXE"
            apptitle = "Document1 - Microsoft Word"              
                
        # implement for USBCOMPOSITE case
        # disable scanner before loading image
        # [Nam Nguyen, 18-Oct-2019] exthandleobj = None -> using PC -> need to use host cmd D or E
        #if exthandleobj is None:
        if Common.displayflag.upper() == "PC":
            if hostserial is not None:
                hostserial.WriteHostData("D")
                time.sleep(1.0)
            else:
                if appprocess == "WINWORD.EXE":
                    # Lock keyboard by Keyfreeze
                    File.Log().ReportLog(objlog, "INFO", "Lock Key")
                    Utilities.StartProgram(Common.keyfreezepath) 
                    time.sleep(2.0)           
                    #KeyUtil.KeyUtil().Type('^%(f)')

        # [Nam Nguyen, 21-Dec-16]: Move start app below open image in case run on tablet and make it focus on app (notepad)
        #if exthandleobj is None:
        if Common.displayflag.upper() == "PC":
            # open image
            Utilities.OpenImage(imagefilepath)
        
            # focus on application by clicking mouse        
            thread3 = Thread(target=Utilities.WaitAndFocusWindow, args=(apptitle, 0, ))       
            thread3.start()        

        # open application
        Utilities.StartProgram(appcmd)
       
        # get start time
        starttime = datetime.datetime.now()
        
        # enable scanner when running with USBCOMPOSITE
        #if exthandleobj is None:
        if Common.displayflag.upper() == "PC":
            if hostserial is not None:
                hostserial.WriteHostData("E")
                time.sleep(1.0)
            else:
                if appprocess == "WINWORD.EXE":
                    # when focusing on host application app, we will freeze keyboard a little seconds
                    time.sleep(1.0)        
            
                    # unlock keyboard by kill keyfreeze or press "Ctrl+Alt+F"
                    File.Log().ReportLog(objlog, "INFO", "Unlock Key")
                    Process.Process().KillProcess("KeyFreeze.exe")            
                    #KeyUtil.KeyUtil().Type('^%(f)')
       
            # because after using thread, screen picture is executed faster than opening image, so need to wait a bit
            time.sleep(1.0)
        
            # take screenshot before reading
            File.Log().LogScreenshot(objlog, "INFO", info)
        
            # wait for application got data
            time.sleep(readinglabeltimeout)
        
            # close image first, then copy and get clipboard
            Utilities.CloseImage(imagefilepath)
        # display image on EPD
        else:
            # take screenshot before reading
            File.Log().LogScreenshot(objlog, "INFO", info)
        
            # clear and display image on external device            
            Utilities.DisplayImage(Common.displayflag, exthandleobj, imagefilepath, readinglabeltimeout)
        
        # get end time
        endtime = datetime.datetime.now()
        
        # wait for image was closed and scanner stopped transmitting data
        #time.sleep(5.0)
        time.sleep(Common.stoptransmitdatatimeout)
        
        # wait until host application receive data successfully
        # for winword app run on Russian country, keyboard layout is different with English keyboard
        # so cannot use ctrl+a or ctrl+c to select all and copy
        result = Utilities.SelectAndCopyClipboard()
        
        difftimetmp =  endtime - starttime
        difftime = difftimetmp.seconds
        
        File.Log().ReportLog(objlog, "INFO", "TOTAL TIME FOR READING LABEL IS: '" + str(difftime) + "' SECONDS")
        
        # get total line
        tmp_result = result.split("\n")
        tmp_result = [x for x in tmp_result if len(x) > 0]
        File.Log().ReportLog(objlog, "INFO", "TOTAL READ LINE ARE: '" + str(len(tmp_result)) + "'")
        
        avaragetime = 0
        if len(tmp_result) > 0:
            avaragetime = float(difftime)/len(tmp_result)
        
        File.Log().ReportLog(objlog, "INFO", "AVARAGE TIME: '" + str(avaragetime) + "'")
        
        # wait for copying successfully
        time.sleep(0.5)        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)   
    return result

def PostReadLabel(hostapplication="notepad"):
    # close unexpected app opened when reading label
    # close host application
    try:
        # open host app to receive data
        if (hostapplication.upper() == "NOTEPAD"):
            appprocess = "notepad.exe"           
        # if another application --> will open winword.exe
        else:
            appprocess = "WINWORD.EXE"           
        
        # close application
        Process.Process().KillProcess(appprocess)
        
        # kill some unexpected programs when reading labels
        Process.Process().KillProcess("CLVIEW.EXE")
        Process.Process().KillProcess("HelpPane.exe")
        Process.Process().KillProcess("iexplore.exe")
        Process.Process().KillProcess("chrome.exe")
        Process.Process().KillProcess("ONENOTE.EXE")
        Process.Process().KillProcess("fixmapi.exe")
        
        # wait for application and image close
        time.sleep(2.0)
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)

def ReadAndVerifyLabel(imagefilepath=None, hostapplication="notepad", hostserial=None, objlog=None,expecteddata=None, verifytype="match", info=None, readinglabeltimeout=5, exthandleobj=None, analyzelogobj=None, analyzeinfo=None, manualinfodicts=None):
    try:
        startinfo = "START IMAGE FILE\t '" + imagefilepath + "'\t" + str(info)
        File.Log().ReportLog(objlog, "INFO", startinfo)           
        
        # print info
        msgInfo = "Image File: '" + imagefilepath + "'\tVerify Type: '" + verifytype + "'\t" + str(info)
        
        # read label and return data
        receivedata = ReadLabel(imagefilepath, hostapplication, hostserial, objlog, msgInfo, readinglabeltimeout, exthandleobj)
       
        capnumdicts = {"ON": 1, "OFF": 0}
        
        # get current num lock and capslock after reading label
        numlockstate = KeyUtil.KeyUtil().IsNumLockOn()
        capslockstate = KeyUtil.KeyUtil().IsCapsLockOn()
        File.Log().ReportLog(objlog, "INFO", "CURRENT CAPSLOCK AND NUMLOCK AFTER READING LABEL: " + str(capslockstate) + ", " + str(numlockstate))
                
        # only get 1 result on app
        actualresult = ""
        if len(receivedata) > 0:
            # [Nam Nguyen, 7-Sep-2016]: Handle case, data receive containing START_ and _END, in case test special data from 0x00 to 0x1f (refer bug 48538)
            # we need to mark START and END because this data including \x0a\x0d in the middle, so hard to recognize the end of data receive.
            listreceivedata = []
            if "START_" in receivedata and "_END" in receivedata:
                listreceivedata = receivedata.split("_END\r\n")
                listreceivedata = [x + "_END" for x in listreceivedata if len(x) > 0]
            else:
                # get actual result, end of data is {CR} but in notepad and winword, end of data is \r\n
                listreceivedata = receivedata.split("\r\n")
            
            # Handle \x0a\x0d in expected data
            if "{CR}" in expecteddata:
                expecteddata = expecteddata.replace("{CR}", "\r\n")
            
            # get longest string in list
            actualresult = max(listreceivedata, key=len)            
            
            ###########################################################
            # exceptional case: if scanner transmitted truncated length
            # print all exceptional cases  
            # remove null value
            tmp_listreceivedata = [x for x in listreceivedata if len(x) > 0]        
            i = 1
            for eachvalue in tmp_listreceivedata:
                if len(expecteddata) != len(eachvalue.encode('utf-8')):
                    msgExcept = "Line: '" + str(i) + "' was not received fully data.\tReceived data is: '" + eachvalue.encode('utf-8') + "'"
                    msgInformation1 = "Image File: '" + imagefilepath + "'\tHost Application: '" + hostapplication + "'\t "
                    msgInformation2 = "\tLength Expected Data: '" + str(len(expecteddata)) + "'\tLength Received Data: '" + str(len(eachvalue.encode('utf-8'))) + "'"
                    msgExcept = msgInformation1.encode('utf-8') + msgExcept + msgInformation2.encode('utf-8')
                    File.Log().ReportLog(objlog, "EXCEPTION", msgExcept)
                # get index of exceptional line
                i = i + 1
 
        # verify
        bverifyFlag = VerifyLabel(expecteddata, actualresult, verifytype)
        
        # some chars will make log not friendly -> replace it to equivalent char
        replacecharsdict = {"\r\n": "{CR}", "\t": "{TAB}"}
        
        # [Nam Nguyen, 7-Sep-2017]: For purpose in logging expected data and result not containing any \r\n
        for specialchar in list(replacecharsdict):
            if specialchar in expecteddata:
                expecteddata = expecteddata.replace(specialchar, replacecharsdict[specialchar])
            
            if specialchar in actualresult:
                actualresult = actualresult.replace(specialchar, replacecharsdict[specialchar])
         
        msgVerify = "\tExpected Data: '" + expecteddata + "'\tActual Data: '" + actualresult.encode('utf-8') + "'"
        msgVerify = msgInfo.encode('utf-8') + msgVerify
        
        # verify caplock numlock state
        # [Nam Nguyen, 15-Mar-2019]: Added step to verify capslock and numlock
        capnumstatuslog = ""
        if manualinfodicts.has_key("capstate") and manualinfodicts.has_key("numstate"):
            expectcapstate = capnumdicts[str(manualinfodicts["capstate"]).upper()]
            expectnumstate = capnumdicts[str(manualinfodicts["numstate"]).upper()]            
            if str(expectcapstate) != str(capslockstate) or str(expectnumstate) != str(numlockstate):
                capnumstatuslog = "/FAIL CAPS/NUM"

        
        # [Nam Nguyen, 19-09-2019]: Add verified language ID hex based on quality task 90709
        # Check language ID after
        # get language after
        langafterresult = Utilities.getCurrentLanguageHex()
        langafterint = langafterresult[0]
        langafterhexstring = langafterresult[1]
        
        # get language before
        langidhexstringbefore = manualinfodicts["Country ID"][:4]
        langidintbefore = int(langidhexstringbefore, 16)
        
        # verify language id
        languagestatuslog = ""
        if langidintbefore <> langafterint:
            languagestatuslog = "/FAIL LANGUAGE ID"
        
        # verify step
        passstatus = ""
        failstatus = ""
        if bverifyFlag:
            passstatus = "PASS" + capnumstatuslog + languagestatuslog
            
            File.Log().ReportLog(objlog, passstatus, msgVerify)
            # Nam Nguyen, 16-Jan-2017: Write info to analyze file  (no need to parselog if use these parameters)
            if analyzelogobj is not None and analyzeinfo is not None:
                analyzelog1 = analyzeinfo + passstatus + "\t\t'"
                analyzelog2 = "'\t\t\t" + str(capslockstate) + "\t" + str(numlockstate) + "\t" + langafterhexstring
                analyzelogobj.write(analyzelog1.encode('utf-8') + expecteddata + "'\t'" + actualresult.encode('utf-8') + analyzelog2.encode('utf-8') + "\n")
        else:
            # [Nam Nguyen, 27-Dec-2017]: Add manual result, because when run with UTF-8 unicode, there are a lot of fails but when manual it passed
            failstatus = "FAIL BY MISMATCH"
            
            if manualinfodicts is not None or len(manualinfodicts) > 0:
                manualresultfile = Common.workingfolder + "Data\\ManualAnalyzeResult.xls"
                manualfilterkeys = ["Encoding Mode", "ALT Mode", "Application", "Country Code", "Country ID", "Label Test"]
                submanualinfodict = dict(filter(lambda i:i[0] in manualfilterkeys, manualinfodicts.iteritems()))
                
                # get expected manual result
                tmpexpectedmanualresult = DB.Excel(manualresultfile, "ManualResult").GetColValuesByFilterCols("Manual Expected", submanualinfodict)
                expectedmanualresult = ""
                if len(tmpexpectedmanualresult) > 0:
                    expectedmanualresult = tmpexpectedmanualresult[0]
                    
                if expectedmanualresult == actualresult and len(actualresult) > 0 and len(capnumstatuslog) == 0:
                    failstatus = "MANUAL PASS"
            
            failstatus = failstatus + capnumstatuslog + languagestatuslog      
            
            screenshotpath = File.Log().LogScreenshot(objlog, "FAIL", msgVerify)
            # Nam Nguyen, 16-Jan-2017: Write info to analyze file  (no need to parselog if use these parameters)
            if analyzelogobj is not None and analyzeinfo is not None:
                analyzelog1 = analyzeinfo + failstatus + "\t\t'"
                analyzelog2 = "'\t" + screenshotpath + "\t\t" + str(capslockstate) + "\t" + str(numlockstate) + "\t" + langafterhexstring
                analyzelogobj.write(analyzelog1.encode('utf-8') + expecteddata + "'\t'" + actualresult.encode('utf-8') + analyzelog2.encode('utf-8') + "\n")
            # wait for taking picture
            time.sleep(0.5)
                       
            # close application
            PostReadLabel(hostapplication)
            
            # read revision A to check scanner alive or not if actual result returned null
            returneddata = actualresult.replace('\r', '')
            returneddata = returneddata.strip(' ')
            
            if len(returneddata) == 0:
                # load and read revisionA label                
                revAinfo = "Read RevisionA label: '" + Common.revAlabel + "'."
                revisionresult = ReadLabel(Common.revAlabel, hostapplication, hostserial, objlog, revAinfo, 5, exthandleobj)
                
                revresult = ''
                if len(revisionresult) > 0:
                    # get actual result
                    listrevisionresult = revisionresult.split("\n")
            
                    # remove \r
                    listrevisionresult = [x.replace('\r', '') for x in listrevisionresult]
            
                    # get longest string in list
                    revresult = max(listrevisionresult, key=len)
                    
                File.Log().LogScreenshot(objlog, "INFO", "Read RevisionA label: '" + Common.revAlabel + "'.\t Return data: '" + revresult.encode('utf-8') + "'.")
                    
                if len(revresult.strip(' ')) > 0:
                    # scanner is still alive                        
                    File.Log().ReportLog(objlog, "INFO", "Scanner is still ALIVE.")
                else:
                    # capture screenshot at that time
                    File.Log().LogScreenshot(objlog, "WARNING", "Scanner maybe DISCONNECTED or CANNOT COPY SYSTEM CLIPBOARD.")
                        
                    # wait for taking picture
                    time.sleep(0.5)
                    
        # post Read label
        PostReadLabel(hostapplication)  
        
        endinfo = "END IMAGE FILE\t '" + imagefilepath + "'\t" + str(info)
        File.Log().ReportLog(objlog, "INFO", endinfo)     
    
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        File.Log().ReportLog(objlog, "WARNING", "UA.ReadAndVerifyLabel::: " + err)
        
def VerifyLabelCombineCapNum(imagefilepath=None, hostapplication="notepad", hostserial=None, objlog=None,expecteddata=None, verifytype="match", info=None, exthandleobj=None, analyzelogobj=None, analyzeinfo=None):
    try:    
        # get label name
        labelname = imagefilepath[imagefilepath.rfind("\\") + 1:imagefilepath.find(".png")]
        
        # combine numlock and capslock
        capslock = {1: 'ON', 0: 'OFF'}
        numlock = {1: 'ON', 0: 'OFF'}
        
        # get caplock and numlock state before reading label
        capnumstatedictbefore = Utilities.GetCapNumState()
        
        # caplock on/off
        for capslockset in capslock:
            # run script to enable capslock
            KeyUtil.KeyUtil().SetCaplock(capslockset)              
                    
            # wait for a bit
            time.sleep(2.0)
                            
            #get capslock state
            capstate = capslock[capslockset]
                    
            # get caplock state
            #capslockstate = KeyUtil.KeyUtil().IsCapsLockOn()            
                             
            # numlock on/off            
            newanalyzeinfo = None
            for numlockset in numlock:
                                 
                # run script to enable capslock
                KeyUtil.KeyUtil().SetNumlock(numlockset)
                    
                # wait for a bit
                time.sleep(5.0)
                                
                # get numlock state
                numstate = numlock[numlockset]
                        
                # get numlock state:
                #numlockstate = KeyUtil.KeyUtil().IsNumLockOn()
                
                # [Nam Nguyen, 17-Jan-2017]: Add analyze log info (no need to use parse log)
                if analyzelogobj is not None and analyzeinfo is not None:
                    newanalyzeinfo = analyzeinfo + capstate + "\t" + numstate + "\t"
                             
                # read and verify
                tmp_info = str(info) + "\tCapslock: '" + capstate + "'\tNumlock: '" + numstate + "'"                
                ReadAndVerifyLabel(imagefilepath, hostapplication, hostserial, objlog, expecteddata, verifytype, tmp_info, exthandleobj=exthandleobj, analyzelogobj=analyzelogobj, analyzeinfo=newanalyzeinfo)
    
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        File.Log().ReportLog(objlog, "WARNING", err)
 
def LoadScannerConfigs(dbfile="C:\\Keyboard\\CountryMode\\Data\\Mondonovo.xls", ifname="RS232-STD", configdict={}, restoredefault=False, timereset=5.0):
    shortconfigssetting = ""
    shortconfigsaftersetting = ""
    fullconfigsdictsetting = {}
    try:        
        if configdict is not None or len(configdict) > 0:
        
            # get serviceport        
            interfaceinfodict = File.File().ReadConfigFile(Common.workingfolder + "Data\\interface.conf")
            ifcontentdict = interfaceinfodict[ifname]
        
            # Open service port        
            devb.Device(ifcontentdict["port"], ifcontentdict["baudrate"], ifcontentdict["bytesize"], ifcontentdict["parity"], ifcontentdict["stopbits"])
        
            # Enter service port
            devb.DeviceObject().write("$S,B00\x0d")
            scannerresponse = devb.DeviceObject().read()            
        
            # wait for enter SP
            time.sleep(1.0)
            
            # if restoredefault true
            if restoredefault:
                #get interface number
                ifdict = {"RS232-STD": "05", "USB-COM": "47", "USBCOM": "47", "RS232-WN": "12", "RS232-OPOS": "13"}
                ifnum = ifdict[ifname]
                restorecmd = "$AE,HA" + str(ifnum) + "\x0d"                
                devb.DeviceObject().write(restorecmd)
                time.sleep(2.0)
                scannerresponse = devb.DeviceObject().read()
                time.sleep(0.2)
        
            # Start setting scanner
            tagnumlist = []
            listshortcfgbefore = []
            fullconfigssetting = []
            for tagname in configdict:
                tagname = str(tagname)              
                tagvalue = str(configdict[tagname])
                
                # get tag num in db file
                tmptagnums = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols("Tag Num", {"Tag Name": tagname})
                
                if len(tmptagnums) > 0:
                    
                    # get tag value size
                    tmptagvaluesize = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols("Value Size (Bytes)", {"Tag Name": tagname})
                    tagsize = 1
                    if len(tmptagvaluesize) > 0:
                        tagsize = int(float(str(tmptagvaluesize[0])))
                    
                    # get tag value type
                    tmptagvaluetypes = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols("Value Type", {"Tag Name": tagname})
                    tagvaluetype = ""
                    if len(tmptagvaluetypes):
                        tagvaluetype = str(tmptagvaluetypes[0])
                    
                    # handle random value
                    if tagvalue.upper() == "RANDOM":
                        if tagvaluetype.upper() in ["LABEL ID", "HEX STRING", "STRING"]:                        
                            randint = random.randint(1, tagsize)
                            tagvalue = binascii.b2a_hex(os.urandom(randint))
                            tagvalue = str(tagvalue).upper()
                        if tagvaluetype.upper() == "ENUMERATION":
                            # get value option
                            tmptagvalueoptions = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols("Value Options", {"Tag Name": tagname})
                            tagvalueoptionstring = ""
                            if len(tmptagvalueoptions) > 0:
                                tagvalueoptionstring = tmptagvalueoptions[0]
                            
                            tagvalueoptions = tagvalueoptionstring.split("\n")
                            numvalueoptions = [x[:x.find("=")] for x in tagvalueoptions if x.find("=") >= 0]
                            numvalueoptions = [x.strip(" ") for x in numvalueoptions]
                            tagvalue = str(random.choice(numvalueoptions))
                        if tagvaluetype.upper() == "RANGE":
                            print "to do"
                    
                    tagnum = str(tmptagnums[0])
                    tagvalue = tagvalue + ''.join("0" for _ in range(tagsize*2 - len(tagvalue)))
                    
                    # get command setting
                    cmd = "$C" + tagnum + tagvalue + "\x0d"
                    
                    # write setting                    
                    devb.DeviceObject().write(cmd)
                    time.sleep(0.2)                    
                    scannerresponse = devb.DeviceObject().read()
                    time.sleep(0.2)
                    tmptagnumlist = tagnumlist.append(tagnum)
                    tmplistshortcfgbefore = listshortcfgbefore.append(cmd.replace("$", "").replace("\x0d", ""))
                
                    tmpfullconfigssetting = fullconfigssetting.append((tagname, tagvalue))
            
            fullconfigsdictsetting = dict((x, y) for x, y in fullconfigssetting)
            
            shortconfigssetting = ",".join(listshortcfgbefore)
            
            # Save and exit SP
            devb.DeviceObject().write("$Ar\x0d")
            scannerresponse = devb.DeviceObject().read()
            
            # wait for reset
            time.sleep(timereset)           
            
            # check scanner again if not effect
            # Enter service port
            devb.DeviceObject().write("$S,B00\x0d")
            scannerresponse = devb.DeviceObject().read()
            time.sleep(1.0)
            
            listshortcfgsafter = []
            for tagnumitem in tagnumlist:
                readcmd = "$c" + tagnumitem + "\x0d"                
                devb.DeviceObject().write(readcmd)
                scannerresponse = devb.DeviceObject().read()    
                valueafter = scannerresponse.replace("$%", "").replace("$>", "").replace("\x0d", "") 
                time.sleep(0.2)                
                tmplistshortcfgsafter = listshortcfgsafter.append("C" + tagnumitem + valueafter)
            
            shortconfigsaftersetting = ",".join(listshortcfgsafter)
            
            devb.DeviceObject().write("$s\x0d")
            scannerresponse = devb.DeviceObject().read()
            time.sleep(0.5)
            
            # close SP
            devb.DeviceObject().close()            
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return fullconfigsdictsetting, shortconfigssetting, shortconfigsaftersetting

def GetExpectedOCRLabel(dbfile="C:\\Keyboard\\CountryMode\\Data\\Mondonovo.xls", ifname="RS232-STD", data=None, configdict={}, ocrlabeltype="passport"):
    expected = ""
    try:
        # get ifclass
        ifclass = ifname
        if ifname in ["USBCOM", "USB-COM"]:
            ifclass = "RS232-STD"
            
        ## GET DEFAULT VALUE OF CONCERN TAGS IN DB XLS
        dbdefaultcol = "Default " + ifclass
        
        listtagsconcern = ["CI_GLOBAL_PREFIX", "CI_GLOBAL_SUFFIX", "CI_ALL_AIM_ID_ENABLE", "CI_LABEL_ID_CONTROL", "CI_CHARACTER_CONVERSION", "CI_CASE_CONVERSION", "CI_OCRB_ENABLE", "CI_LABEL_ID_OCRB", "CI_OCRB_FM"]
        concerntagsandhexvalue = []
        for concerntagname in listtagsconcern:
            
            # get size
            tagsize = 1
            tmptagsize = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols("Value Size (Bytes)", {"Tag Name": concerntagname})
            if len(tmptagsize) > 0:
                tagsize = tmptagsize[0]
            
            # get default hex value on db
            taghexvalue = ""
            tmptaghexvalues = DB.Excel(dbfile, "Configuration").GetColValuesByFilterCols(dbdefaultcol, {"Tag Name": concerntagname})
            
            if len(tmptaghexvalues) > 0:
                taghexvalue = str(tmptaghexvalues[0])
                
                if "." in str(taghexvalue):
                    taghexvalue = str(taghexvalue)[:str(taghexvalue).find(".")]                   
                    
                taghexvalue = taghexvalue.zfill(int(tagsize)*2)
                
                # combine to list
                tmpconcerntagsandhexvalue = concerntagsandhexvalue.append((concerntagname, taghexvalue))
       
        concerntagsandhexvaluedict = dict((x, y) for x, y in concerntagsandhexvalue)
        
        # GET CURRENT VALUE IN CONFIGDICT
        # Update valueset value from configdict to concerntags
        tmpconcerntagsandhexvaluedict = concerntagsandhexvaluedict.update(configdict)
                
        # get global prefix value
        glbprevalue = str(concerntagsandhexvaluedict["CI_GLOBAL_PREFIX"]).decode("hex")
        if glbprevalue.find("\x00") >= 0:
            glbprevalue = glbprevalue[:glbprevalue.find("\x00")]
        #glbprevalue = glbprevalue.strip("\x00")        
        
        # get global suffix value
        glbsufvalue = str(concerntagsandhexvaluedict["CI_GLOBAL_SUFFIX"]).decode("hex")
        if glbsufvalue.find("\x00") >= 0:
            glbsufvalue = glbsufvalue[:glbsufvalue.find("\x00")]        
        #glbsufvalue = glbsufvalue.strip("\x00")
        
        #get global aim value
        glbaimvalue = str(concerntagsandhexvaluedict["CI_ALL_AIM_ID_ENABLE"])
        ocraimvalue = "]o1"
        if glbaimvalue == "00":
            ocraimvalue = ""
        
        # get label id control
        idcontrolvalue = str(concerntagsandhexvaluedict["CI_LABEL_ID_CONTROL"])
        
        # get ocr label id
        ocrlbidvalue = str(concerntagsandhexvaluedict["CI_LABEL_ID_OCRB"]).decode("hex")
        if ocrlbidvalue.find("\x00") >= 0:
            ocrlbidvalue = ocrlbidvalue[:ocrlbidvalue.find("\x00")]
        
        #ocrlbidvalue = ocrlbidvalue.strip("\x00")
        lbidpre = ""
        lbidsuf = ""
        if idcontrolvalue == "01":
            lbidpre = ocrlbidvalue
            lbidsuf = ""
        elif idcontrolvalue == "02":
            lbidpre = ""
            lbidsuf = ocrlbidvalue      
        
        # get ocr enable
        ocrenablevalue = str(concerntagsandhexvaluedict["CI_OCRB_ENABLE"])
        
        # get case conversion
        caseconversionvalue = str(concerntagsandhexvaluedict["CI_CASE_CONVERSION"])
        
        # get char conversion
        charconversionvalue = str(concerntagsandhexvaluedict["CI_CHARACTER_CONVERSION"])
        
        if caseconversionvalue == "01":
            data = data.upper()
        elif caseconversionvalue == "02":
            data = data.lower()
            
        # char con do later
        # Addtion char for postal <>
        additionalpostalchar = str(concerntagsandhexvaluedict["CI_OCRB_FM"])
        if additionalpostalchar == "01":
            data = data.replace(" ", "").replace("<", "").replace(">", "").replace("+", "")
        
        if (ocrlabeltype.upper() == "PASSPORT" and str(ocrenablevalue) == "02") or (ocrlabeltype.upper() == "POSTAL" and str(ocrenablevalue) == "01"):
            expected = str(glbprevalue) + str(lbidpre) + str(ocraimvalue) + str(data) + str(lbidsuf) + str(glbsufvalue)
        
    except:
        err = str(sys.exc_info()[1]).replace("\n", "")
        logging.warning(err)
    return expected

def CreateORCImage(ocrtype="passport", ocrtexts=[]):
    ocrimg = ""
    try:
        # open word setting with OCRB font
        wordpath = Common.workingfolder + "Data\\zoom300.doc"
        
        if (ocrtype.upper() == "POSTAL") and (ocrtexts[1] in ["896", "247"]) and (ocrtexts[0].find(">") >= 0):
            wordpath = Common.workingfolder + "Data\\zoom230.doc"
        
        if ocrtype.upper() == "POSTAL":
            ocrtexts = [ocrtexts[0]]
              
        Utilities.StartProgram(wordpath)
        time.sleep(10.0)
        
        for text in ocrtexts:            
            texttype = str(text).replace(" ", "{SPACE}").replace("+", "{+}")
            KeyUtil.KeyUtil().Type(texttype)
            time.sleep(1.0)
            # send enter
            KeyUtil.KeyUtil().Type("{ENTER}")
        
        # enter some break line   
        for i in range(3):
            KeyUtil.KeyUtil().Type("{ENTER}") 
            
        # capture screen text
        # create screenshot name
        screenshotname = Utilities.CreateRandomString() + ".png"
        screenshotfoldertmp = Common.workingfolder + "Labels\\OCR\\Tmp\\"
        screenshotpath = screenshotfoldertmp + screenshotname
        Utilities.CaptureScreen(screenshotpath, 30, 300, 1220, 300)
        ocrimg = screenshotpath        
        
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
