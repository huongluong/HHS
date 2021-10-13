import sys
import Common
import paramiko
#import ssh
import logging
from subprocess import Popen, PIPE, STDOUT
import os

class Ext():
    def __init__(self, exttype=Common.displayflag):
        self.dictinfo = {}
        self.exttype = exttype
        if exttype.upper() == "EPD":
            self.dictinfo = {'ip': '192.168.111.1', 'user': 'root', 'pwd': 'zxc', 'clearcmd': 'cd /media/sd/epd/ && /usr/local/bin/python -c "from epd import *; EPD().clear_display()"', 'displaycmd': 'cd /media/sd/epd/ && /usr/local/bin/python -c "from epd import *; EPD().display_barcode(\'%s\')"', 'imagefolder': '/media/sd/barcodes/'}
        elif exttype.upper() == "KINDLE":
            self.dictinfo = {'ip': '192.168.15.244', 'user': 'root', 'pwd': 'mario', 'clearcmd': '/usr/sbin/eips -c -f', 'displaycmd': '/usr/sbin/eips -g /mnt/us/images/%s', 'imagefolder': '/mnt/us/images/'}
        else:
            # do nothing if exttype = "pc"
            print("do nothing")
            
    def open(self):
        handleobj = None
        if len(self.dictinfo) > 0:
            handleobj = ssh.Connection(host=self.dictinfo["ip"], username=self.dictinfo["user"], password=self.dictinfo["pwd"])
        return handleobj
    
    def uploadImage(self, src):
        all_output = None
        if len(self.dictinfo) > 0:
            server = self.dictinfo["ip"]
            user = self.dictinfo["user"]
            pwd = self.dictinfo["pwd"]
            dst = self.dictinfo["imagefolder"]
            pathpscp = Common.workingfolder + "Extra\\"
            p = Popen(
                '%(pathpscp)spscp.exe -scp -pw %(pwd)s -batch %(src)s %(user)s@%(server)s:%(dst)s' % locals(), 
                shell=True, stdout=PIPE, stderr=STDOUT
                )
            all_output, null = p.communicate()
        return all_output
    
    def clearScreen(self, handleobj=None, numberofclear=1):
        if handleobj is not None:
            i = 1
            while i <= numberofclear:
                #print self.dictinfo["clearcmd"]
                handleobj.execute(self.dictinfo["clearcmd"])
                i += 1
                
    def displayImage(self, handleobj=None, imagename=None):
        if handleobj is not None:
            displaycmd = self.dictinfo["displaycmd"]
            handleobj.execute(displaycmd %imagename)

    def deleteImage(self, handleobj=None, imagename=None):
        if handleobj is not None:
            imagefilepath = self.dictinfo["imagefolder"] + imagename
            handleobj.execute("rm %s" %imagefilepath)
                
    def close(self, handleobj=None):
        if handleobj is not None:
            handleobj.close()
