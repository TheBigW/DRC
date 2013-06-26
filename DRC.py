# DRC.py
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

import os, sys, inspect, struct

from gi.repository import GObject, Gst, Peas, RB, Gtk, Gdk, GdkPixbuf
from DRCUi import DRCDlg

from config import Config
MY_ICON_IMAGE = "MY_ITEM_IMAGE"

class DRCPlugin(GObject.Object, Peas.Activatable):
	object = GObject.property(type = GObject.Object)
	def __init__(self):
		super(DRCPlugin, self).__init__()

	def do_activate(self):
		self.shell = self.object
		self.shell_player = self.shell.props.shell_player
		self.player = self.shell_player.props.player
		self.fir_filter = Gst.ElementFactory.make('audiofirfilter', 'MyFIRFilter')	
		print "audiofirfilter :", self.fir_filter
		#open filter files
		aCfg = Config()
		num_filter_coeff = 0
		if aCfg.filterFile != '':
			filter_data_left = open( "./"+aCfg.filterFile, "r" )
			#filter_data_right = open( aCfg.filterFile, "r" )
			#read the pcm data as 32 bit float
			filter_array = []
			read_left = filter_data_left.read( 4 )
			#read_right = filter_data_right.read( 4 )
			while read_left != "":# and filter_data_right != "":
				#read left chanel
				float_left = struct.unpack( 'f', read_left )[0]
				read_left = filter_data_left.read( 4 )
				filter_array.append( float_left )
				#read right chanel			
				#float_right = struct.unpack( 'f', read_right )[0]
				#read_right = filter_data_right.read( 4 )
				#filter_array.append( float_right )
			#pass the filter data to the fir filter
			#print inspect.getdoc( self.fir_filter )
			num_filter_coeff = len( filter_array )
		self.fir_filter.set_property( 'latency', num_filter_coeff /2 )
		print "num_filter_coeff", num_filter_coeff
		kernel = self.fir_filter.get_property('kernel')
		print "kernel : ", kernel		
		for i in range(0, num_filter_coeff):
			 kernel.append( filter_array[i] )
			 #print "index %i : %f" % (i, filter_array[i])
		self.fir_filter.set_property('kernel', kernel)
		print inspect.getdoc( kernel )
		self.set_filter()
		print "filter succesfully set"
		self.psc_id = self.shell_player.connect('playing-song-changed', self.playing_song_changed)
		#finally add UI
		self.add_ui( self, self.shell )
	def add_ui(self, plugin, shell):
		self.drcDlg = DRCDlg()
		icon_factory = Gtk.IconFactory()
		filename = plugin.find_file("DRC.svg")
		print "svg: ", filename		
		picBuff = GdkPixbuf.Pixbuf.new_from_file(filename)
		#print inspect.getdoc( picBuff )
		icon_factory.add( MY_ICON_IMAGE, Gtk.IconSet( picBuff ) )
		icon_factory.add_default()

		action = Gtk.Action ('DRC', 
				_('_DRC'), 
				_('DRC'),
				MY_ICON_IMAGE)
		action.connect ('activate', self.drcDlg.show_ui, shell)
		action_group = Gtk.ActionGroup ('DRCActionGroup')
		action_group.add_action (action)
		ui_manager = shell.props.ui_manager
		ui_manager.insert_action_group (action_group)
		ui_manager.add_ui_from_file(plugin.find_file("drc-ui.xml"))
		
	def set_filter(self):
		try:
			print 'adding filter'
			self.player.add_filter(self.fir_filter)
			print 'done setting filter'
		except Exception as inst:
			print 'unexpected exception',  sys.exc_info()[0], type(inst), inst  
			pass

	def do_deactivate(self):
		print 'entering do_deactivate'
		self.shell_player.disconnect(self.psc_id)
		
		try:		
			self.player.remove_filter(self.fir_filter)
			print 'filter disabled'	
		except:
			pass
					
		del self.shell_player
		del self.shell
		del self.fir_filter

	def playing_song_changed(self, sp, entry):
		if entry == None:
			return
		genre = entry.get_string(RB.RhythmDBPropType.GENRE)
		print "genre : " + str(genre)
		print entry.get_string(RB.RhythmDBPropType.ALBUM)
		print entry.get_string(RB.RhythmDBPropType.TITLE)
	def find_file(self, filename):
		info = self.plugin_info
		data_dir = info.get_data_dir()
		path = os.path.join(data_dir, filename)
		
		if os.path.exists(path):
			return path

		return RB.file(filename)
