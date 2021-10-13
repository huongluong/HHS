import serial
import time
import io
import sys

globals().update({'__gDevHandle': None})

class Device:
    def __init__(self, port="COM1", baudrate=9600, bytesize=8, parity="N", stopbits=1, timeout=1.0, xonxoff=0, rtscts=0):
        try:
            self.ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts)

            #return __gDevHandle;
            globals().update({'__gDevHandle': self.ser})
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            print("WARNING:::_init_::: ERROR::: " + str(err))
    def write(self, data):
        self.ser.write(data.encode('utf-8'))

    def isOpen(self):
        isopen = False
        try:
            isopen = self.ser.isOpen()
        except:
            print("WARNING:::isOpen::: CANNOT OPEN SERIAL PORT")
        return isopen

    def open(self):
        if not self.ser.isOpen():
            self.ser.open()

    def readAll(self):
        result = self.ser.readall()
        return result

    def read(self):
        result = ""

        while True:
            byte = self.ser.read(1)
            time.sleep(0.01)
            if not self.ser.inWaiting():
                break
            result += str(byte)

        return result.encode()
    def read(self,term,tout):
        tic = time.time()
        buff = self.ser.read(1)
        while (((time.time() - tic) < tout) and (not term.encode('utf-8') in buff)):
            buff += self.ser.read(1)
        return buff
    def close(self):
        self.ser.close()
class DeviceObject:
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
            print("WARNING:::isOpen::: CANNOT OPEN SERIAL PORT")
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
        self._devobj.setBaudrate()
    
    def changeParity(self, parity):
        self._devobj.setParity(parity)
        
    def changeByteSize(self, bytesize):
        self._devobj.setByteSize(bytesize)
    
    def changeStopbits(self, stopbits):
        self._devobj.setStopbits(stopbits)
