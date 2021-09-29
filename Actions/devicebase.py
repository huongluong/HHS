import serial
import time
import io
import sys

globals().update({'__gDevHandle': None})

class Device():
    def __init__(self, port="COM1", baudrate=9600, bytesize=8, parity="N", stopbits=1, timeout=1.0, xonxoff=0, rtscts=0):
        try:
            __gDevHandle = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts)
            globals().update({'__gDevHandle': __gDevHandle})
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            print "WARNING:::_init_::: ERROR::: " + str(err)

class DeviceObject():
    def __init__(self, devobj=None):
        if devobj is None:
            devobj = globals()['__gDevHandle']  
            
        self._devobj = devobj
    
    def write(self, data):
        self._devobj.write(data)
    
    def writeLines(self, data):
        self._devobj.writelines(data)
    
    def isOpen(self):
        isopen = False
        try:
            isopen = self._devobj.isOpen()
        except:
            print "WARNING:::isOpen::: CANNOT OPEN SERIAL PORT"
        return isopen
    
    def open(self):
        if not self.isOpen():
            self._devobj.open()
    
    def readAll(self):
        result = self._devobj.readall()
        return result
    
    def readSize(self, size=1):
        result = self._devobj.read(size)
        return result

    def read(self):
        result = ""
        
        while True:
            byte = self._devobj.read(1)
            time.sleep(0.01)
            if not self._devobj.inWaiting():
                break
            result += str(byte)
                   
        return result
    
    def clearBuffer(self):
        self._devobj.flush()
        self._devobj.flushInput()
        self._devobj.flushOutput()
    
    def readonetime(self, timeout):
        result = ""
        byte = ""
        self.clearBuffer()
        starttime = time.time()
        while (byte != "\x0d") and (time.time() - starttime <= timeout):
            byte = self._devobj.read(1)
            time.sleep(0.01)
            result += str(byte)
        self.clearBuffer()
        return result
    
    def readtimeout(self, timeout):                
        result = ""
        self.clearBuffer()
        starttime = time.time()
        while time.time() - starttime <= timeout:
            byte = self._devobj.read(1)            
            result += str(byte)
            if not self._devobj.inWaiting():
                break            
        return result
    
    def close(self):
        if self.isOpen():
            self._devobj.close()
    
    def changeBaudrate(self, baudrate):
        self._devobj.setBaudrate(baudrate)
    
    def changeParity(self, parity):
        self._devobj.setParity(parity)
        
    def changeByteSize(self, bytesize):
        self._devobj.setByteSize(bytesize)
    
    def changeStopbits(self, stopbits):
        self._devobj.setStopbits(stopbits)
