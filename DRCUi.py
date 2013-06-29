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
import os, sys, inspect, subprocess, re
from config import Config

class LabeledEdit:
    def __init__(self, box, text, value):
        label = Gtk.Label( text )
        box.add(label)
        self.entry = Gtk.Entry()
        self.entry.set_text( value )
        box.add( self.entry )

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

        name_store = Gtk.ListStore(int, str)
        p = subprocess.Popen(["aplay", "-l"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from aplay : " + out )
        #append all available audio devices
        #parse all card:X ... device:y ... to alsa devices
        pattern = re.compile('(\d):.*(\d):(.*)', re.MULTILINE)
        self.alsaHardwareList = pattern.findall(out)
        for i in range(0, len(self.alsaHardwareList)):
            name_store.append([ i, self.alsaHardwareList[i][2] ] )
        self.alsaHardwareCombo = Gtk.ComboBox.new_with_model_and_entry(name_store)
        self.alsaHardwareCombo.set_entry_text_column(1)
        self.alsaHardwareCombo.set_active(0)
        self.vbox.add( Gtk.Label( "sound hardware" ) )
        self.vbox.add(self.alsaHardwareCombo)

        #TBC: connect to Gtk.Entry to insert_text event to do input validation
        self.entryFilterFile = LabeledEdit(self.vbox, "filter file", aCfg.filterFile )
        self.entryStartFreq = LabeledEdit(self.vbox, "start freq. [Hz]", str(aCfg.startFrequency) )
        self.entryEndFreq = LabeledEdit(self.vbox, "end freq. [Hz]", str(aCfg.endFrequency) )
        self.entrySweepDuration = LabeledEdit(self.vbox, "sweep duration. [s]", str(aCfg.sweepDuration) )
        self.vbox.add(slider)
        self.vbox.add( Gtk.Label( "sweep gain[%]" ) )
        measureBtn = Gtk.Button( "measure" )
        measureBtn.connect( "clicked", self.on_execMeasure )
        self.vbox.add(measureBtn)
        self.vbox.add(applyBtn)
        print("found pattern : ", self.alsaHardwareList, " alsa HW : ", self.getAlsaHardwareString())

    def slider_changed(self, hscale):
    	self.sweep_level = hscale.get_value();

    def on_apply_settings(self, some_param):
        aCfg = Config()
        aCfg.alsaDevice = self.getAlsaHardwareString()
        aCfg.filterFile = self.entryFilterFile.entry.get_text()
        aCfg.recordGain = self.sweep_level
        aCfg.startFrequency = int( entryStartFreq.entry.get_text() )
        aCfg.endFrequency = int( entryEndFreq.entry.get_text() )
        aCfg.sweepDuration = int( entrySweepDuration.entry.get_text() )
        aCfg.save()

    def getAlsaHardwareString(self):
        alsHardwareSelIndex = self.alsaHardwareCombo.get_active()
        alsaDevicePlaybackRecord = "hw:" + str(self.alsaHardwareList[alsHardwareSelIndex][0]) + "," + str(self.alsaHardwareList[alsHardwareSelIndex][1])
        print("alsa device used : " + alsaDevicePlaybackRecord)
        return alsaDevicePlaybackRecord

    def on_execMeasure(self):
        aCfg = Config()        
        #execute measure script to generate filters
        p = subprocess.Popen( [ "./measure1Channel", self.amplitude + ", " + aCfg.alsaDevice  + ", " + string(self.start_freq)  + ", " +  string(self.end_freq) + ", " +  self.measure_duration ], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from measure script : " + out )

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
