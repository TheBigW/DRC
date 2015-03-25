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

from gi.repository import GConf

DRC_GCONF_BASE_PATH = '/apps/rhythmbox/plugins/DRC'
	
class DRCConfig:
	def __init__(self):
		self.load()
	def load(self):	
		conf = GConf.Client.get_default()
		self.filterFile = conf.get_string( DRC_GCONF_BASE_PATH + '/filterFile' )
		self.numFilterChanels = conf.get_int( DRC_GCONF_BASE_PATH + '/numFilterChanels' )
		self.recordGain = conf.get_float( DRC_GCONF_BASE_PATH + '/recordGain' )
		self.startFrequency = conf.get_int( DRC_GCONF_BASE_PATH + '/startFrequency' )
		self.endFrequency = conf.get_int( DRC_GCONF_BASE_PATH + '/endFrequency' )
		self.sweepDuration = conf.get_int( DRC_GCONF_BASE_PATH + '/sweepDuration' )
		if None == self.filterFile:
			self.filterFile = ""
		if None == self.recordGain:
			self.recordGain = 0.5
		if None == self.startFrequency:
			self.startFrequency = 50
		if None == self.endFrequency:
			self.endFrequency = 21000
		if None == self.sweepDuration:
			self.sweepDuration = 40
		if None == self.numFilterChanels:
			self.numFilterChanels = 1
	def save( self ):
		conf = GConf.Client.get_default()
		conf.set_string( DRC_GCONF_BASE_PATH + '/filterFile', self.filterFile if self.filterFile != None else "")
		conf.set_int( DRC_GCONF_BASE_PATH + '/numFilterChanels', self.numFilterChanels )
		conf.set_float( DRC_GCONF_BASE_PATH + '/recordGain', self.recordGain )
		conf.set_int( DRC_GCONF_BASE_PATH + '/startFrequency', self.startFrequency )
		conf.set_int( DRC_GCONF_BASE_PATH + '/endFrequency', self.endFrequency )
		conf.set_int( DRC_GCONF_BASE_PATH + '/sweepDuration', self.sweepDuration )
