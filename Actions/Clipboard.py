# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import win32api, win32con
import ctypes
import os
import logging
import sys, re
import sys
import win32clipboard

##########################################################################
class Clipboard():
    def OpenClipboard(self):
        win32clipboard.OpenClipboard()
    
    def CloseClipboard(self):       
        win32clipboard.CloseClipboard()
        
    def ClearClipboard1(self):        
        from ctypes import windll
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard() 
    
    def ClearClipboard(self):        
        self.OpenClipboard()
        win32clipboard.EmptyClipboard()
        self.CloseClipboard() 
    
    def GetClipboard(self):
        data = ""
        try:
            self.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            self.CloseClipboard()
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return data
    
    def GetClipboard1(self):
        result =''        
        CF_TEXT = 1
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        #open clipboard
        user32.OpenClipboard(0)
        if user32.IsClipboardFormatAvailable(CF_TEXT):
            data = user32.GetClipboardData(CF_TEXT)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            result = text.value
            kernel32.GlobalUnlock(data_locked)
        # close clipboard
        user32.CloseClipboard()
        return result
    
    def SetClipboard(self, data):        
        self.OpenClipboard()
        self.ClearClipboard()
        win32clipboard.SetClipboardText(data, win32clipboard.CF_UNICODETEXT)
        self.CloseClipboard()
