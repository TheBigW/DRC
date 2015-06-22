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

from XMLSerializer import Serializer
from gi.repository import RB

DRC_CFG_FILE="DRC.xml"

class DRCConfig:
    def __init__(self):
        self.cfgFileName = RB.user_cache_dir() + "/DRC/" + DRC_CFG_FILE
        self.filterFile = ""
        self.recordGain = 0.5
        self.startFrequency = 50
        self.endFrequency = 21000
        self.sweepDuration = 40
        self.numFilterChanels = 1
        self.load()
    def load(self):
        try:
            cfgFile = open(self.cfgFileName,'r')
            cfg = Serializer.read(cfgFile , self)
            self.filterFile = cfg.filterFile
            self.startFrequency = cfg.startFrequency
            self.endFrequency = cfg.endFrequency
            self.sweepDuration = cfg.sweepDuration
            self.numFilterChanels = cfg.numFilterChanels
        except:
            print("no cfg existing -> create default")
            self.save()
            pass
    def save( self ):
        print("saving cfg to : " + self.cfgFileName)
        Serializer.write(self.cfgFileName, self)