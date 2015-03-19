# DRCUi.py
# Copyright (C) 2013 - Tobias Wenig
#            tobiaswenig@yahoo.com>
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
from DRCConfig import DRCConfig

class LabeledEdit:
    def __init__(self, box, text, value):
        self.label = Gtk.Label( text )
        box.add(self.label)
        self.entry = Gtk.Entry()
        self.entry.set_text( value )
        box.add( self.entry )

def getDeviceListFromAlsaOutput( command ):
    p = subprocess.Popen([command, "-l"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    pattern = re.compile("(\d*):\s.*?\[(.*?)\],\s.*?\s(\d*):.*?\s\[(.*?)\]", re.MULTILINE)
    alsaHardwareList = pattern.findall(str(out))
    print("found pattern : " + str(alsaHardwareList) )
    name_store = Gtk.ListStore(int, str)
    for i in range(0, len(alsaHardwareList)):
        name_store.append([ i, alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3]])
    return [alsaHardwareList, name_store]

def createDeviceCombo( command, label, vbox ):
    result = getDeviceListFromAlsaOutput(command)
    name_store = result[1]
    alsaPlayHardwareList = result[0]
    alsaPlayHardwareCombo = Gtk.ComboBox.new_with_model_and_entry(name_store)
    alsaPlayHardwareCombo.set_entry_text_column(1)
    vbox.add( Gtk.Label( label ) )
    alsaPlayHardwareCombo.set_active(0)
    vbox.add(alsaPlayHardwareCombo)
    return [alsaPlayHardwareCombo, alsaPlayHardwareList]

class DRCDlg(Gtk.Dialog):
    def __init__(self, parent):
        super(Gtk.Dialog, self).__init__()
        self.parent = parent
        aCfg = DRCConfig()
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

        playResult = createDeviceCombo( "aplay", "sweep output", self.vbox )
        self.alsaPlayHardwareCombo = playResult[0]
        self.alsaPlayHardwareList = playResult[1]
        recResult = createDeviceCombo( "arecord", "sweep record", self.vbox )
        self.alsaRecHardwareCombo = recResult[0]
        self.alsaRecHardwareList = recResult[1]

        #TBC: connect to Gtk.Entry to insert_text event to do input validation
        self.entryFilterFile = LabeledEdit(self.vbox, "filter file", aCfg.filterFile )
        openFileBtn = Gtk.Button( "Load filter" )
        openFileBtn.connect( "clicked", self.openFilterFile )
        self.vbox.add(openFileBtn)
        self.entryStartFreq = LabeledEdit(self.vbox, "start freq. [Hz]", str(aCfg.startFrequency) )
        self.entryEndFreq = LabeledEdit(self.vbox, "end freq. [Hz]", str(aCfg.endFrequency) )
        self.entrySweepDuration = LabeledEdit(self.vbox, "sweep duration. [s]", str(aCfg.sweepDuration) )
        self.vbox.add(slider)
        self.vbox.add( Gtk.Label( "sweep gain[%]" ) )
        measureBtn = Gtk.Button( "measure" )
        measureBtn.connect( "clicked", self.on_execMeasure )
        self.vbox.add(measureBtn)
        self.vbox.add(applyBtn)
        print(" alsa play HW : ", self.getAlsaPlayHardwareString())

    def slider_changed(self, hscale):
        self.sweep_level = hscale.get_value();

    def openFilterFile(self, param):
        currFilter = self.entryFilterFile.entry.get_text()
        currPath = os.path.split(currFilter)[0]
        dlg = Gtk.FileChooserDialog("Open..", None, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        try:
            dlg.set_current_folder(currPath)
            if dlg.run() == Gtk.ResponseType.OK:
                filename = dlg.get_filename()
                self.entryFilterFile.entry.set_text(filename)
                dlg.destroy()
                self.parent.updateFilter(filename)
        except Exception as inst:
            print( 'filter not set',  sys.exc_info()[0], type(inst), inst )
            pass
        dlg.destroy()

    def on_apply_settings(self, some_param):
        aCfg = DRCConfig()
        aCfg.alsaDevice = self.getAlsaHardwareString()
        aCfg.filterFile = self.entryFilterFile.entry.get_text()
        aCfg.recordGain = self.sweep_level
        aCfg.startFrequency = int( self.entryStartFreq.entry.get_text() )
        aCfg.endFrequency = int( self.entryEndFreq.entry.get_text() )
        aCfg.sweepDuration = int( self.entrySweepDuration.entry.get_text() )
        aCfg.save()

    def getAlsaPlayHardwareString(self):
        if len(self.alsaPlayHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaPlayHardwareCombo.get_active()
        alsaDevicePlayback = "hw:" + str(self.alsaPlayHardwareList[alsHardwareSelIndex][0]) + "," + str(self.alsaPlayHardwareList[alsHardwareSelIndex][2])
        print("alsa output device : " + alsaDevicePlayback)
        return alsaDevicePlayback

    def getAlsaRecordHardwareString(self):
        if len(self.alsaRecHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaRecHardwareCombo.get_active()
        alsaDeviceRec = "hw:" + str(self.alsaRecHardwareList[alsHardwareSelIndex][0]) + "," + str(self.alsaRecHardwareList[alsHardwareSelIndex][2])
        print("alsa output device : " + alsaDeviceRec)
        return alsaDeviceRec

    def on_execMeasure(self):
        aCfg = DRCConfig()
        #execute measure script to generate filters
        p = subprocess.Popen( [ "./measure1Channel", self.amplitude + ", " + self.getAlsaPlayHardwareString()  + ", " + self.getAlsaRecordHardwareString() + string(self.start_freq)  + ", " +  string(self.end_freq) + ", " +  self.measure_duration ], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from measure script : " + out )

    def on_close(self, shell):
        print( "closing ui")
        self.set_visible(False)
        return True

    def show_ui(self, shell, state, dummy):
        print("showing UI")
        self.show_all()
        self.present()
        print( "done showing UI" )

    def on_destroy(self, widget, data):
        self.on_close(None)
        return True
