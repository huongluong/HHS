# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import win32api, win32con
import ctypes
import os
import logging
import sys, re
import time
import sys
import wx
import re
import win32ui
import win32gui
from ctypes import *
import win32com.client
import time

##########################################
class Window():
    def __init__(self, windowtitle):
        self._windowtitle = windowtitle
    
    def Focus(self):
        try:            
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.AppActivate(self._windowtitle)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def WaitForWindowExists(self, timeout):
        bexistFlag = False        
        i = 0
        while (bexistFlag == False) and (i<=timeout): 
            try:
                win32ui.FindWindow(None, self._windowtitle)
            except win32ui.error:
                bexistFlag = False
            else:
                bexistFlag = True
            
            time.sleep(0.1)
            i = i + 0.1        
                
        return bexistFlag
    
    def BringToFront(self, timeout=1.5):
        try:
            if self.WaitForWindowExists(timeout):
                handle = win32gui.FindWindow(None, self._windowtitle) 
                win32gui.BringWindowToTop(handle)
                win32gui.SetForegroundWindow(handle)
            else:
                logging.warning(self._windowtitle + " NOT EXISTED")                           
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)

class MouseClick():
    def ClickXY1(self, x, y):
        try:
            win32api.SetCursorPos((x,y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def ClickXY(self, x, y):
        try:
            ctypes.windll.user32.SetCursorPos(x, y)
            ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
            ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def ClickOnWindow(self, windowtitle, del_x, del_y, timeout=1.5):
        try:            
            wexists = Window(windowtitle).WaitForWindowExists(timeout)
            if wexists:
                x, y = win32ui.FindWindow(None, windowtitle).GetWindowRect()[0:2]
                self.ClickXY(x + del_x, y + del_y)
            else:
                logging.warning(windowtitle + " NOT EXISTED")
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
