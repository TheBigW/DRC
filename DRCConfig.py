# config.py
# Copyright (C) 2013 - Tobias Wenig
#			tobiaswenig@yahoo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os

import gi
from gi.repository import RB

from XMLSerializer import Serializer

DRC_CFG_FILE = "DRC.xml"


class DRCConfig:
    def __init__(self):
        configDir = RB.user_cache_dir() + "/DRC"
        if not os.path.exists(configDir):
            os.makedirs(configDir)
        self.cfgFileName = configDir + "/" + DRC_CFG_FILE
        self.filterFile = ""
        self.recordGain = 0.5
        self.sweepDuration = 40
        self.numFilterChanels = 1
        self.FIRFilterMode = 0
        self.playHardwareIndex = 0
        self.recHardwareIndex = 0
        self.recHardwareChannelIndex = 0
        self.MicCalibrationFile = ""
        #0 - None
        #1 - GStreamerFIR
        #2 - BruteFIR
        self.load()

    def load(self):
        try:
            cfgFile = open(self.cfgFileName, 'r')
            cfg = Serializer.read(cfgFile, self)
            self.filterFile = cfg.filterFile
            self.sweepDuration = cfg.sweepDuration
            self.numFilterChanels = cfg.numFilterChanels
            self.FIRFilterMode = cfg.FIRFilterMode
            self.playHardwareIndex = cfg.playHardwareIndex
            self.recHardwareIndex = cfg.recHardwareIndex
            self.recHardwareChannelIndex = cfg.recHardwareChannelIndex
            self.MicCalibrationFile = cfg.MicCalibrationFile
        except:
            print("no cfg existing -> create default")
            self.save()
            pass

    def save(self):
        print("saving cfg to : " + self.cfgFileName)
        Serializer.write(self.cfgFileName, self)
