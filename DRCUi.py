# DRCUi.py
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
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf, Gst
import os, sys, inspect, subprocess
from config import Config

class DRCDlg(Gtk.Dialog):
    def __init__(self):
        super(Gtk.Dialog, self).__init__()
        aCfg = Config()
        self.set_deletable(False)	
        self.connect( "delete-event", self.on_destroy )
        self.set_title( "DRC" )
        applyBtn = Gtk.Button( "Save" )
        applyBtn.connect( "clicked", self.on_apply_settings )

        slider = Gtk.VScale()
        slider.set_range( 0.1, 1 )
        slider.set_inverted(True)
        slider.set_value_pos( Gtk.PositionType.TOP )
        self.sweep_level = aCfg.recordGain
        slider.set_value(self.sweep_level)
        slider.set_size_request( 100, 300 )
        slider.connect( "value_changed", self.slider_changed )

        self.entryFilterFile = Gtk.Entry()
        self.vbox.add( Gtk.Label( "filter file" ) )
        self.filterFile = aCfg.filterFile
        self.entryFilterFile.set_text( self.filterFile )
        self.vbox.add(self.entryFilterFile)
        self.vbox.add(slider)
        self.vbox.add( Gtk.Label( "sweep gain[%]" ) )
        measureBtn = Gtk.Button( "measure" )
        measureBtn.connect( "clicked", self.on_execMeasure )
        self.vbox.add(applyBtn)

    def slider_changed(self, hscale):
    	self.sweep_level = hscale.get_value();

    def on_apply_settings(self, some_param):
        aCfg = Config()
        aCfg.filterFile = self.entryFilterFile.get_text()
        aCfg.recordGain = self.sweep_level
        aCfg.save()

    def on_execMeasure(self):
        #execute measure script to generate filters		
        subprocess.call(["./measure1Channel", self.amplitude, self.inputhw, self.start_freq, self.end_freq, self.measure_duration], cwd="./")
			
    def on_close(self, shell):
        print "closing ui"
        self.set_visible(False)
        return True

    def show_ui(self, shell, state):
        print "showing UI"
        self.show_all()
        self.present()
        print "done showing UI"

    def on_destroy(self, widget, data):
        self.on_close(None)
        return True
