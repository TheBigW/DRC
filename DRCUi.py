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

class ChanelSelDlg:
    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file("DRCUI.glade")
        self.dlg = self.uibuilder.get_object("channel_no_dlg")
        okBtn = self.uibuilder.get_object("button_OK")
        okBtn.connect( "clicked", self.on_Ok )
        cancelBtn = self.uibuilder.get_object("button_Cancel")
        cancelBtn.connect( "clicked", self.on_Cancel )

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.destroy()
    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.dlg.destroy()
    def run(self):
        print("running dlg...")
        return self.dlg.run()
    def getNumChannels(self):
        numChanels = 1
        check2Chan = self.uibuilder.get_object("radiobutton_2Channel")
        if check2Chan.get_active() == True:
            numChanels = 2
        return numChanels

def getDeviceListFromAlsaOutput( command ):
    p = subprocess.Popen([command, "-l"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    pattern = re.compile("(\d*):\s.*?\[(.*?)\],\s.*?\s(\d*):.*?\s\[(.*?)\]", re.MULTILINE)
    alsaHardwareList = pattern.findall(str(out))
    print("found pattern : " + str(alsaHardwareList) )
    return alsaHardwareList

def getNameStoreFromHardwareList(alsaHardwareList):
    name_store = Gtk.ListStore(int, str)
    for i in range(0, len(alsaHardwareList)):
        name_store.append([ i, alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3]])
    return name_store

def fillComboFromDeviceList(combo, alsaHardwareList):
    for i in range(0, len(alsaHardwareList)):
        combo.append_text( alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3] )

def createDeviceCombo( command, label, vbox ):
    result = getDeviceListFromAlsaOutput(command)
    name_store = getNameStoreFromHardwareList(result)
    alsaPlayHardwareList = result[0]
    alsaPlayHardwareCombo = Gtk.ComboBox.new_with_model_and_entry(name_store)
    alsaPlayHardwareCombo.set_entry_text_column(1)
    vbox.add( Gtk.Label( label ) )
    alsaPlayHardwareCombo.set_active(0)
    vbox.add(alsaPlayHardwareCombo)
    return [alsaPlayHardwareCombo, alsaPlayHardwareList]

class DRCDlg:#(Gtk.Dialog):
    def __init__(self, parent):
        #super(Gtk.Dialog, self).__init__()
        self.parent = parent
        aCfg = DRCConfig()
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file("DRCUI.glade")
        self.dlg = self.uibuilder.get_object("DRCDlg")
        self.filechooserbtn = self.uibuilder.get_object("drcfilterchooserbutton")
        self.filechooserbtn.set_filename(aCfg.filterFile)
        self.filechooserbtn.connect("selection-changed", self.on_file_selected)

        self.alsaPlayHardwareCombo = self.uibuilder.get_object("comboOutput")
        self.alsaRecHardwareCombo = self.uibuilder.get_object("comboRecord")

        self.alsaPlayHardwareList = getDeviceListFromAlsaOutput("aplay")
        self.alsaRecHardwareList = getDeviceListFromAlsaOutput("arecord")
        fillComboFromDeviceList(self.alsaPlayHardwareCombo, self.alsaPlayHardwareList)
        fillComboFromDeviceList( self.alsaRecHardwareCombo, self.alsaRecHardwareList)

        calcDRCBtn = self.uibuilder.get_object("buttonCalculateFilter")
        calcDRCBtn.connect( "clicked", self.on_calculateDRC )

        slider = self.uibuilder.get_object("scaleSweepAmplitude")
        slider.set_range( 0.1, 1 )
        slider.set_value_pos( Gtk.PositionType.TOP )
        self.sweep_level = aCfg.recordGain
        slider.set_value(self.sweep_level)
        slider.connect( "value_changed", self.slider_changed )

        apply_closeBtn = self.uibuilder.get_object("apply_closeBtn")
        apply_closeBtn.connect( "clicked", self.on_apply_settings )
        print(" alsa play HW : ", self.getAlsaPlayHardwareString())

        self.comboDRC = self.uibuilder.get_object("combo_drc_type")
        #TODO: check availibility of PORC & DRC and fill combo accordingly
        self.comboDRC.append_text("DRC")
        self.comboDRC.append_text("PORC")

    def slider_changed(self, hscale):
        self.sweep_level = hscale.get_value();

    def on_file_selected(self, widget):
        self.DrcFilename= widget.get_filename()
        self.parent.updateFilter(self.DrcFilename)

    def on_apply_settings(self, some_param):
        aCfg = DRCConfig()
        aCfg.alsaDevice = self.getAlsaHardwareString()
        aCfg.filterFile = self.DrcFilename
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
        impOutputFile = "./impulse_resp.pcm"
        #execute measure script to generate filters
        p = subprocess.Popen( [ "./measure1Channel",\
                                self.amplitude + " " +\
                                self.getAlsaPlayHardwareString()  + " " +\
                                self.getAlsaRecordHardwareString() +\
                                str(self.start_freq)  + " " +\
                                str(self.end_freq) + " " +\
                                self.measure_duration + " " +\
                                impOutputFile], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from measure script : " + out )
        #TODO: check for errors
        self.uibuilder.get_object("impResponseFileChooserBtn").set_filename(impOutputFile)

    def on_calculateDRC(self):
        drcMethod = self.comboDRC.get_text()
        drcScript = "./calcFilterDRC"
        costumParams = ""
        if drcMethod == "DRC":
            drcScript = "./calcFilterDRC"
            costumParams =  "/usr/share/drc/config/44.1 kHz/erb-44.1.drc"
        elif drcMethod == "PORC":
            drcScript = "./calcFilterPORC"
        #execute measure script to generate filters
        filterResultFile = "Filter" + drcMethod.pcm
        p = subprocess.Popen( [ drcScript, self.impResponseFileChooserBtn + " " + filterResultFile + " " + costumParams], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from filter calculate script : " + out )

    def on_close(self, shell):
        print( "closing ui")
        self.set_visible(False)
        return True

    def show_ui(self, shell, state, dummy):
        print("showing UI")
        self.dlg.show_all()
        self.dlg.present()
        print( "done showing UI" )

    def on_destroy(self, widget, data):
        self.on_close(None)
        return True
