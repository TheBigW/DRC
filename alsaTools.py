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


def fillComboFromDeviceList(combo, alsaHardwareList, active):
    for i in range(0, len(alsaHardwareList)):
        combo.append_text(
            alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3])
    combo.set_active(active)