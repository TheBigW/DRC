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
	
class Config:
	def __init__(self):
		self.load()
	def load(self):	
		conf = GConf.Client.get_default()
		self.filterFile = conf.get_string( DRC_GCONF_BASE_PATH + '/filterFile' )
		self.recordGain = conf.get_float( DRC_GCONF_BASE_PATH + '/recordGain' )
		if None == self.filterFile:
			self.filterFile = ""
		if None == self.recordGain:
			self.recordGain = 0.5
	def save( self ):
		conf = GConf.Client.get_default()
		conf.set_string( DRC_GCONF_BASE_PATH + '/filterFile', self.filterFile )
		conf.set_float( DRC_GCONF_BASE_PATH + '/recordGain', self.recordGain )
