# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015
import pyautogui
#import win32api, win32con
import logging
import time
import datetime
import sys

#############################################################
import win32api
import win32con


class KeyUtil:
    def Copy(self):
        try:
            pyautogui.hotkey('ctrl','c')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def SelectAll(self):
        try:
            pyautogui.hotkey('ctrl','a')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def SelectAll2(self):
        try:
            pyautogui.hotkey('ctrl','end')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def Copy2(self):
        try:
            pyautogui.hotkey('ctrl','insert')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def BackHome(self):
        try:
            pyautogui.hotkey('ctrl','home')
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
    
    def Type(data):
        try:
            pyautogui.write(data)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
            
    def IsCapsLockOn(self):
        return win32api.GetKeyState(win32con.VK_CAPITAL)
    
    def SetCaplock(self, iset=1):
        # enable caplock
        if self.IsCapsLockOn() == 0 and iset == 1:
            pyautogui.press('capslock')
        # disable caplock
        elif self.IsCapsLockOn() == 1 and iset == 0:
            pyautogui.press('capslock')
    
    # get numlock state
    def IsNumLockOn(self):
        # return 1 if CAPSLOCK is ON
        return win32api.GetKeyState(win32con.VK_NUMLOCK)

    # enable/disable numlock
    def SetNumlock(self, iset=1):
        # enable numlock
        if self.IsNumLockOn() == 0 and iset == 1:
            pyautogui.press('numlock')
        # disable numlock
        elif self.IsNumLockOn() == 1 and iset == 0:
            pyautogui.press('numlock')

#if __name__ == '__main__':
#    print("Test class KeyUtil")

