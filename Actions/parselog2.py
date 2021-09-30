#Implement by Huong.Luong
#Date : 24-Aug-2021
# This use for parse log Image Capture

import os.path

import os

class parselog2():

    def ParseLog(filepath):
        # set temp excel file
        # Don't directly write to excel file because unicode format will be lost
        # tempfile = filepath.replace(".txt", "_Analyzed.xls")
        #filepath = "ImageCaptureLog_17082021_1439.txt"
        # save to .log file then paste to excel file
        tempfile = filepath.replace(".txt", "_Analyzed.log")

        # remove file temp if existed
        if os.path.isfile(tempfile):
            os.remove(tempfile)

            # open file log
        lines = []
        if os.path.isfile(filepath):
            f = open(filepath, "r")
            lines = f.readlines()
            f.close()

        # if file is not empty line
        if len(lines) > 0:
            # get last line
            lastline = len(lines) - 1

            # search key 'START SCENARIO' in log file
            startscensinfo = [x for x in lines if "START SCENARIO" in x]

            # get index of start scen info
            startscensindexes = [lines.index(x) for x in startscensinfo]

            # search key 'END SCENARIO' in log file
            endscensinfo = [x for x in lines if "END SCENARIO" in x]

            # get index of stop scen info
            endscenindexes = [lines.index(x) for x in endscensinfo]
            # merge 2 indexes
            #mergeindexes = zip(startscensindexes, endscenindexes)

            # write temp file
            # write header
            headerfile = "TESTCASE NAME \tIMAGE TYPE \tRESULT"
            # f = open(tempfile, 'a')
            f = open(tempfile, 'a')

            # write header
            f.writelines("%s\n" % headerfile)
            if(len(startscensindexes) == len(endscenindexes)):
                #set count number of scenarios
                count = 0
                #set variable for scen indexes
                scenindexes = []

                #run all indexs of scenarios
                logsceninfo = ""
                for index in endscenindexes:
                    # increase count scenario
                    count = count + 1

                    # get scenario line
                    scenariolinecontent = lines[index]
                    wordList = scenariolinecontent.split(" ")
                    #for(word in wordList):
                    tcName = wordList[8]
                    if tcName == 'HOST_CMD_CAPTURE' : tcName = 'Image Capture Auto'
                    elif tcName == 'HOST_CMD_CAPTURE_NO_HANDSHAKE': tcName = 'Image Capture Auto without HandShake'
                    elif tcName == 'HOST_CMD_CAPTURE_ON_TRIGGER': tcName = 'Single Capture on Trigger'
                    elif tcName == 'HOST_CMD_CAPTURE_ON_TRIGGER_NO_HANDSHAKE': tcName = 'Single Capture on Trigger without HandShake'
                    elif tcName == 'HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER': tcName = 'Multiple Capture on Trigger'
                    elif tcName == 'HOST_CMD_MULTIPLE_CAPTURE_ON_TRIGGER_NO_HANDSHAKE': tcName = 'Multiple Capture on Trigger without HandShake'
                    elif tcName == 'HOST_CMD_CAPTURE_ON_DECODE': tcName = 'Single Capture on Decode'
                    elif tcName == 'HOST_CMD_CAPTURE_ON_DECODE_NO_HANDSHAKE': tcName = 'Single Capture on Decode without HandShake'
                    elif tcName == 'HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE': tcName = 'Multiple Capture on Decode'
                    elif tcName == 'HOST_CMD_MULTIPLE_CAPTURE_ON_DECODE_NO_HANDSHAKE': tcName = 'Multiple Capture on Decode without HandShake'
                    imgType = wordList[11][:(len(wordList[11])-1)]  #strip \n
                    result = wordList[7]
                    line = tcName+'\t'+ imgType + '\t' + result
                    f.writelines("%s\n" % line)
            else:
                f.writelines("This log file content unexpected structure START SCENARIO <> END SCENARIO, so can not parse this file")
    #if __name__ == '__main__':
    #    ParseLog("ImageCaptureLog_17082021_1656.txt")