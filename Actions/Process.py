# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Implemented Date: 08-Apr-2015

import logging
import time
import sys
import subprocess
import psutil
import os

#####################
class Process():
    # check process exist
    def ProcessCheck(self, processname):
        result = False
        try:
            plist = psutil.get_process_list()
            str1=" ".join(str(x) for x in plist)
            if processname in str1:
                result = True
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)
        return result
    
    # Kill process
    def KillProcess(self, processname):
        try:
            if self.ProcessCheck(processname):
                os.system("taskkill /f /im " + processname)
                #time.sleep(1.0)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)

    # Kill process by window title
    def KillProcessByWindowTitle(self, windowtitle):        
        #subprocess.call(['TASKKILL', '/F', '/FI', 'WINDOWTITLE eq ' + windowtitle + '*'])        
        #os.system('TASKKILL /F /FI "WINDOWTITLE eq ' + windowtitle + '*"')
        subprocess.call(['TASKKILL', '/F', '/FI', 'WINDOWTITLE eq ' + windowtitle + '*'])
        
        # wait a bit
        time.sleep(1.0)

    def WaitForProcessExists(self, processname, timeout):
        i = 0
        processexistflag = self.ProcessCheck(processname)
        while (processexistflag == False) and (i <= timeout):
            time.sleep(1.0)
            processexistflag = self.ProcessCheck(processname)
            i = i + 1
