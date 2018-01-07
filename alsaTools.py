# -*- coding: utf-8 -*-
import threading
import subprocess
import re
import sys


class InputVolumeProcess():
    def __init__(self, updateProgressBar):
        self.progressBar = updateProgressBar
        self.proc = None
        self.t = None

    def reader_thread(self):
        for line in iter(self.proc.stdout.readline, b''):
            strLine = str(line)
            # print("reader_thread : " + strLine)
            result = self.pattern.findall(strLine)
            if len(result) > 0:
                # print("arecord: result : "+str(result))
                iValue = int(result[0])
                self.progressBar.set_fraction(iValue / 100)

    def start(self, recHW, chanel, mode=None):
        try:
            self.stop()
            if mode is None:
                mode = "S32_LE"
            # maybe using plughw and see if it removes the dependencies to
            # use that at all
            volAlsaCmd = ["arecord", "-D" + recHW, "-c" + chanel, "-d0",
                          "-f" + mode, "/dev/null", "-vvv"]
            print("starting volume monitoring with : " + str(volAlsaCmd))
            self.proc = subprocess.Popen(volAlsaCmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
            self.pattern = re.compile("(\d*)%", re.MULTILINE)
            self.t = threading.Thread(None, target=self.reader_thread).start()
        except Exception as inst:
            print('unexpected exception', sys.exc_info()[0], type(inst), inst)

    def stop(self):
        print("stoping volume monitoring")
        if self.t is not None:
            self.t.terminate()
        if self.proc is not None:
            self.proc.terminate()
        self.progressBar.set_fraction(0.0)
        self.proc = None
        self.t = None

def getDeviceListFromAlsaOutput(command):
    p = subprocess.Popen([command, "-l"], 0, None, None, subprocess.PIPE,
                         subprocess.PIPE)
    (out, err) = p.communicate()
    pattern = re.compile(
        "\w* (\d*):\s.*?\[(.*?)\],\s.*?\s(\d*):.*?\s\[(.*?)\]", re.MULTILINE)
    alsaHardwareList = pattern.findall(str(out))
    print("found pattern : " + str(alsaHardwareList))
    return alsaHardwareList

def execCommand(params):
    print(("executing: " + str(params)))
    p = subprocess.Popen(params, 0, None, None, subprocess.PIPE,
        subprocess.PIPE)
    return p.communicate()

def getAlsaRangedValue(valueString, inputStr):
    pattern = re.compile(valueString + ":\s\[?(\d{1,6})\s?(\d{1,6})?\]?",
                         re.MULTILINE)
    found = pattern.findall(str(inputStr))
    print ("found: ", found )
    # workaround to remove empty match in case of just single number
    # because I was not clever enough to have a clean
    # conditional regex...
    if len(found[0]) > 1 and not found[0][1]:
        result = [found[0][0]]
    else:
        result = [found[0][0], found[0][1]]
    print("result for " + valueString + " : ", result)
    return result

class AlsaDevInfo():
    def __init__(self):
        self.MaxChannel = 0
        self.MinChannel = 0
        self.supportedModes = None
        self.MinRate = 0
        self.MaxRate = 0

    def setDefaults(self):
        self.MaxChannel = 2
        self.MinChannel = 0
        self.supportedModes = ["S32_LE"]
        self.MinRate = 44100
        self.MaxRate = 44100

def getAlsaDeviceInfo(params):
    result = AlsaDevInfo()
    try:
        (out, err) = execCommand(params)
        print(("hw infos : err : " + str(err) + " out : " + str(out)))
        # I rely on alsa output as e.g. CHANNELS to be not translated
        channels = getAlsaRangedValue("CHANNELS",err)
        result.MaxChannel = int(channels[0] if (len(channels) < 2) else channels[1])
        result.MinChannel = int(channels[0])
        pattern = re.compile("(\D\d+_\w*)", re.MULTILINE)
        result.supportedModes = pattern.findall(str(err))
        #parse rate
        rates = getAlsaRangedValue("RATE", err)
        result.MaxRate = int(rates[0] if (len(rates) < 2) else rates[1])
        result.MinRate = int(rates[0])

        print(("numChannels : ", result.MaxChannel, result.MinChannel))
        print(("supportedModes : ", str(result.supportedModes)))
        print(("rates : ", result.MaxRate, result.MinRate))
        return result
    except Exception as inst:
        print((
            'failed to get rec hardware info...',
            sys.exc_info()[0], type(inst), inst))
    #proceed at least with reasonable defaults almost evrt device can meet
    result.setDefaults();
    return result

def getRecordingDeviceInfo(recHwString):
    params = ['arecord', '-D', recHwString,
        '--dump-hw-params', '-d 1']
    return getAlsaDeviceInfo(params)

def getPlayDeviceInfo(playHwString):
    #TODO create dummy wave file by recording for a very short period
    dummyWaveFile="/usr/lib/rhythmbox/plugins/DRC/dummy.wav"
    params = ['aplay', '-D', playHwString,
        '--dump-hw-params', dummyWaveFile]
    #TODO implement fallback in case this fails - provide default parameters
    return getAlsaDeviceInfo(params)

class AlsaDevice():
    def __init__(self, alsaLine):
        self.alsaHW = "hw:" + str(alsaLine[0]) + "," + str(alsaLine[2])
        self.alsaDevName = alsaLine[1]+" : " + alsaLine[3]
        self.validToUse = True
        self.MaxChannel = None
        self.samplingRates = []

    def fromDevInfo(self, devInfo):
        self.MaxChannel = devInfo.MaxChannel
        self.MinChannel = devInfo.MinChannel
        self.supportedModes = devInfo.supportedModes
        self.MinRate = devInfo.MinRate
        self.MaxRate = devInfo.MaxRate

class AlsaPlayDev(AlsaDevice):
    def __init__(self, alsaLine):
        AlsaDevice.__init__(self, alsaLine)

    def loadDeviceInfo(self):
        try:
            #loading is only needed once
            if self.MaxChannel is None:
                self.isDigitalOut = self.alsaDevName.lower().find("digital") > -1 or self.alsaDevName.lower().find("hdmi") > -1 or self.alsaDevName.find("S/PDIF") > -1 or self.alsaDevName.find("IEC958") > -1
                devInfo = getPlayDeviceInfo(self.alsaHW)
                AlsaDevice.fromDevInfo(self,devInfo)
        except Exception as inst:
            print((
            'failed to play hardware for AlsaPlayDev',
            sys.exc_info()[0], type(inst), inst))


class AlsaRecDev(AlsaDevice):
    def __init__(self, alsaLine):
        AlsaDevice.__init__(self, alsaLine)
        self.validToUse = False
        try:
            devInfo = getRecordingDeviceInfo(self.alsaHW)
            AlsaDevice.fromDevInfo(self,devInfo)
            #TODO I limit for rec devices that can deliver 32 bit; to be checked to support 16 bit too
            self.validToUse = "S32_LE" in self.supportedModes
        except Exception as inst:
            print((
            'failed to get rec hardware for AlsaRecDev',
            sys.exc_info()[0], type(inst), inst))

    def loadDeviceInfo(self):
        print("nothing to do for rec device")

class AlsaDevices():
    def __init__(self):
        self.alsaPlayDevs = []
        alsaPlayDev = getDeviceListFromAlsaOutput("aplay")
        for alsaDevLine in alsaPlayDev:
            self.alsaPlayDevs.append( AlsaPlayDev(alsaDevLine) )
        self.alsaRecDevs = []
        alsaRecDev = getDeviceListFromAlsaOutput("arecord")
        for alsaDevLine in alsaRecDev:
            self.alsaRecDevs.append( AlsaRecDev(alsaDevLine) )


def fillComboFromDeviceList(combo, alsaHardwareList, active):
    for alsaDev in alsaHardwareList:
        if alsaDev.validToUse:
            combo.append_text( alsaDev.alsaDevName )
    combo.set_active(active)
