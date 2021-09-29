# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import SendKeys
import win32api, win32con
import logging
import time
import datetime
import sys

#############################################################
class KeyUtil():
    def Copy(self):
        try:
            SendKeys.SendKeys('^(c)')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def SelectAll(self):
        try:
            SendKeys.SendKeys('^(a)')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def SelectAll2(self):
        try:
            SendKeys.SendKeys('^+{END}')            
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def Copy2(self):
        try:
            SendKeys.SendKeys('^{INSERT}')            
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def BackHome(self):
        try:
            SendKeys.SendKeys('^{HOME}')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def Type(self, data):
        try:
            SendKeys.SendKeys(data)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def IsCapsLockOn(self):
        return win32api.GetKeyState(win32con.VK_CAPITAL)
    
    def SetCaplock(self, iset=1):
        # enable caplock
        if self.IsCapsLockOn() == 0 and iset == 1:
            SendKeys.SendKeys("{CAPSLOCK}")
        # disable caplock
        elif self.IsCapsLockOn() == 1 and iset == 0:
            SendKeys.SendKeys("{CAPSLOCK}")
    
    # get numlock state
    def IsNumLockOn(self):
        # return 1 if CAPSLOCK is ON
        return win32api.GetKeyState(win32con.VK_NUMLOCK)

    # enable/disable numlock
    def SetNumlock(self, iset=1):
        # enable numlock
        if self.IsNumLockOn() == 0 and iset == 1:
            SendKeys.SendKeys("{NUMLOCK}")
        # disable numlock
        elif self.IsNumLockOn() == 1 and iset == 0:
            SendKeys.SendKeys("{NUMLOCK}")