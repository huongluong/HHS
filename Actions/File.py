# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import ctypes
import ConfigParser
import os
import logging
import sys, re
import glob
import time
import sys
import wx
import psutil
import datetime
import shutil
import re
import wx
import Common

##################################
class Folder():
    def __init__(self, parentfolderpath):
        self._parentfolderpath = parentfolderpath
        
    def IsFolderExists(self):
        return os.path.exists(self._parentfolderpath)
    
    def GetSubFolders(self):
        subfolders = []
        try:
            # list all children folder
            listallitems = os.listdir(self._parentfolderpath)
            for sub in listallitems:
                subpath = self._parentfolderpath + sub + "\\"
                if os.path.isdir(subpath) == True:
                    tmp = subfolders.append(subpath)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return subfolders

    def GetFilesByFilter(self, wildcard):
        listfile = []
        try:
            # list out all children folder
            os.chdir(self._parentfolderpath)
            
            # filter by wildcard
            tmpfilelist = glob.glob(wildcard)            
            listfile = [self._parentfolderpath + x for x in tmpfilelist]
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return listfile
    
    def GetAllSubFolders(self):
        allsubfolders = []
        try:
            allsubfolders = [x[0] for x in os.walk(self._parentfolderpath)]
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return allsubfolders
    
    def GetFilePathByName(self, givenfilename):
        filepath = ""
        try:
            for root, dirs, files in os.walk(self._parentfolderpath):
                for fileName in files:
                    if givenfilename == fileName:
                        filepath = root + "\\" + fileName
                        return filepath
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return filepath
    
    def GetFilePathsByFilter(self, filter):
        listfilepath = []
        try:
            for root, dirs, files in os.walk(self._parentfolderpath):
                for fileName in files:
                    if filter in fileName:
                        filepath = root + "\\" + fileName
                        tmp = listfilepath.append(filepath)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return listfilepath

class File():
    def IsFileExists(self, filepath):
        return os.path.exists(filepath)
    
    # Read file config
    def ReadConfigFile(self, strcfgfilepath = 'C:\\Keyboard\\CountryMode\\keyboard.conf'):
        result = {}
        cp = ConfigParser.SafeConfigParser()
        cp.read(strcfgfilepath)
        sections = cp._sections        
        for values in sections.values():
            if '__name__' in values:
                del values['__name__']
            for key, val in values.items():
                values[key] = eval(values[key])
            # return dict contain section and value
            result = dict(sections)
        return result 
    
    def MoveAndRenameFile(self, sourcefilepath, destinationfilepath):
        try:
            shutil.move(sourcefilepath, destinationfilepath)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)

    def CopyAndRenameFile(self, sourcefilepath, destinationfilepath):
        try:
            if not os.path.exists(destinationfilepath):
                shutil.copy(sourcefilepath, destinationfilepath)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def Remove(self, filepath):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)

class Log():
    def OpenLog(self, logpath=Common.tmplogpath, mode="w"):
        f = open(logpath, mode)
        return f
    
    def ReportLog(self, obj=None, levelmsg=None, msgcontent=None):
        #if obj is None:
            #obj = self.OpenLog()
        
        # get date and time
        if obj is not None: 
            currentdatetime = datetime.datetime.now()
            newmsgcontent = ""
            
            if (levelmsg is not None) and (msgcontent is not None):
                newmsgcontent = str(currentdatetime) + '\t' + levelmsg + '\t' + msgcontent + '\n'
            
            obj.write(newmsgcontent)
    
    def CloseLog(self, obj=None):
        if obj is not None:
            obj.close()

    def CaptureScreenshot(self, screenshotpath):
        app = wx.App(False)
        s = wx.ScreenDC()
        w, h = s.Size.Get()
        b = wx.EmptyBitmap(w, h)
        m = wx.MemoryDCFromDC(s)
        m.SelectObject(b)
        m.Blit(0, 0, w, h, s, 0, 0)
        m.SelectObject(wx.NullBitmap)
        b.SaveFile(screenshotpath, wx.BITMAP_TYPE_PNG)

    
    def LogScreenshot(self, obj=None, levelmsg=None, msgcontent=None):
        currentdatetime = datetime.datetime.now()
        datename = str(currentdatetime)[: str(currentdatetime).find(" ")]
        datefolder = Common.screenshotfolder + datename + "\\"
        screenshotname = str(currentdatetime).replace(" ", "_").replace(":", "-").replace(".", "_")
        # create folder date
        if not Folder(datefolder).IsFolderExists():
            os.makedirs(datefolder)
        
        # create screenshot path
        screenshotpath = datefolder + screenshotname + ".png"
        self.CaptureScreenshot(screenshotpath)

        if (obj is not None) and (levelmsg is not None) and (msgcontent is not None):
            # report fail
            self.ReportLog(obj, levelmsg, msgcontent + "\tScreenshot was captured as '" + screenshotpath + "'")
        
        return screenshotpath